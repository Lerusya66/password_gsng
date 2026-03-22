"""
Fitness Evaluator Module
Evaluates prompt quality by testing on validation data
"""

import json
import random
from typing import List, Dict, Tuple
from datetime import datetime
from src.generator import PasswordGenerator
from rapidfuzz.distance import Levenshtein


class FitnessEvaluator:
    """
    Evaluates prompt fitness by calculating cracked rate on validation set
    """
    
    def __init__(self, config: dict, generator: PasswordGenerator):
        """
        Initialize fitness evaluator
        
        Args:
            config: Configuration dictionary
            generator: PasswordGenerator instance (shared to avoid reloading model)
        """
        self.config = config
        self.generator = generator
        self.eval_config = config['evaluation']
        
        # Load and split data
        print(f"Loading training data from {config['data']['train_path']}...")
        with open(config['data']['train_path'], 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        # Create train/val split
        seed = config['evolution']['seed']
        random.seed(seed)
        random.shuffle(all_data)
        
        val_size = self.eval_config['val_size']
        self.val_data = all_data[:val_size]
        self.train_data = all_data[val_size:]
        
        print(f"Data split: {len(self.train_data)} train, {len(self.val_data)} validation")
        
        # Cache for faster evaluation
        self.cache = {}
        
        # Logging
        self.log_file = None
        self.log_enabled = False
    
    def enable_logging(self, log_dir: str = "outputs/evolution_logs"):
        """Enable interactive logging to file"""
        import os
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"evolution_{timestamp}.md")
        self.log_enabled = True
        
        # Write header
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"# Password Guessing Evolution Log\n\n")
            f.write(f"**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Validation Set Size:** {len(self.val_data)}\n\n")
            f.write("---\n\n")
        
        print(f"📝 Interactive log enabled: {self.log_file}")
    
    def _log_evaluation(self, prompt_template: str, cracked_rate: float,
                       failed_passwords: List[Tuple[str, str, List[str]]]):
        """Log evaluation results to file"""
        if not self.log_enabled or not self.log_file:
            return
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"## Evaluation at {datetime.now().strftime('%H:%M:%S')}\n\n")
            f.write(f"**Cracked Rate:** {cracked_rate:.2f}%\n\n")
            f.write(f"**Failed:** {len(failed_passwords)}/{len(self.val_data)}\n\n")
            
            if failed_passwords:
                f.write("### Failed Passwords\n\n")
                for old_pwd, true_pwd, attempts in failed_passwords[:20]:  # Show first 20
                    f.write(f"- **Old:** `{old_pwd}` → **True:** `{true_pwd}`\n")
                    f.write(f"  - **Attempts:** {', '.join([f'`{a}`' for a in attempts[:10]])}\n")
                
                if len(failed_passwords) > 20:
                    f.write(f"\n*... and {len(failed_passwords) - 20} more*\n")
            
            f.write("\n---\n\n")

    def evaluate_old(self, prompt_template: str) -> float:
        """
        Evaluate prompt on validation set
        
        Args:
            prompt_template: Prompt template with {old_password} placeholder
            
        Returns:
            Cracked rate percentage (0-100)
        """
        # Check cache
        cache_key = hash(prompt_template)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        correct = 0
        total = len(self.val_data)
        num_candidates = self.eval_config['num_candidates']
        failed_passwords = []
        
        for entry in self.val_data:
            old_password = entry['Knowledge']['Old password']
            true_password = entry['password']
            
            # Generate candidates
            candidates = self.generator.generate_candidates(
                old_password,
                prompt_template,
                num_candidates=num_candidates
            )
            
            # Check if true password is in candidates
            if true_password in candidates:
                correct += 1
            else:
                # Track failed attempts for logging
                failed_passwords.append((old_password, true_password, candidates))
        
        cracked_rate = (correct / total) * 100
        
        # Log results if enabled
        if self.log_enabled:
            self._log_evaluation(prompt_template, cracked_rate, failed_passwords)
        
        # Cache result
        self.cache[cache_key] = cracked_rate
        
        return cracked_rate

    def evaluate(self, prompt_template: str) -> float:
        cache_key = hash(prompt_template)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        total = len(self.val_data)
        num_candidates = self.eval_config['num_candidates']
        
        cracked = 0
        soft_score = 0.0
        
        for entry in self.val_data:
            old_password = entry['Knowledge']['Old password']
            true_password = entry['password']
            
            candidates = self.generator.generate_candidates(
                old_password,
                prompt_template,
                num_candidates=num_candidates
            )
            
            # === HARD METRIC (Kaggle) ===
            if true_password in candidates:
                cracked += 1
                soft_score += 1.0
                continue
            
            # === SOFT METRIC ===
            best_sim = 0.0
            
            for cand in candidates:
                dist = Levenshtein.distance(cand, true_password)
                max_len = max(len(cand), len(true_password))
                
                sim = 1 - dist / max_len  # [0,1]
                best_sim = max(best_sim, sim)
            
            soft_score += best_sim
        
        cracked_rate = (cracked / total) * 100
        soft_rate = (soft_score / total) * 100
        
        # 🔥 ключевая идея: комбинируем
        final_score = 0.7 * cracked_rate + 0.3 * soft_rate
        
        self.cache[cache_key] = final_score
        return [cracked_rate, final_score]
    
    def evaluate_with_details(self, prompt_template: str) -> Dict:
        """
        Evaluate prompt and return detailed metrics
        
        Args:
            prompt_template: Prompt template
            
        Returns:
            Dictionary with detailed evaluation metrics
        """
        correct = 0
        total = len(self.val_data)
        num_candidates = self.eval_config['num_candidates']
        
        for entry in self.val_data:
            old_password = entry['Knowledge']['Old password']
            true_password = entry['password']
            
            candidates = self.generator.generate_candidates(
                old_password, 
                prompt_template,
                num_candidates=num_candidates
            )
            
            if true_password in candidates:
                correct += 1
        
        cracked_rate = (correct / total) * 100
        
        return {
            'cracked_rate': cracked_rate,
            'correct': correct,
            'total': total,
            'num_candidates': num_candidates
        }


def evaluate_on_full_train(
    generator: PasswordGenerator,
    prompt_template: str,
    train_path: str,
    max_samples: int = None,
    num_candidates: int = 10
) -> Dict:
    """
    Evaluate prompt on full training set (or subset)
    
    Args:
        generator: PasswordGenerator instance
        prompt_template: Prompt template to evaluate
        train_path: Path to training data
        max_samples: Maximum samples to evaluate (None for all)
        num_candidates: Number of candidates per password
        
    Returns:
        Dictionary with evaluation results
    """
    print(f"Loading data from {train_path}...")
    with open(train_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if max_samples and max_samples < len(data):
        data = random.sample(data, max_samples)
        print(f"Using {max_samples} samples for evaluation")
    
    correct = 0
    total = len(data)
    
    print(f"Evaluating on {total} samples...")
    
    from tqdm import tqdm
    for entry in tqdm(data):
        old_password = entry['Knowledge']['Old password']
        true_password = entry['password']
        
        candidates = generator.generate_candidates(
            old_password,
            prompt_template,
            num_candidates=num_candidates
        )
        
        if true_password in candidates:
            correct += 1
    
    cracked_rate = (correct / total) * 100
    
    return {
        'cracked_rate': cracked_rate,
        'correct': correct,
        'total': total,
        'num_candidates': num_candidates
    }

"""
Password Generator Module
Generates password candidates using PassLLM fine-tuned model
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from typing import List, Set
from tqdm import tqdm


class PasswordGenerator:
    """Generates passwords using fine-tuned PassLLM model"""
    
    def __init__(self, config: dict):
        """
        Initialize password generator
        
        Args:
            config: Configuration dictionary with model and generation parameters
        """
        model_config = config['model']
        self.gen_config = config['generation']
        
        print(f"Loading base model from {model_config['base_model_path']}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_config['base_model_path'])
        
        # Set padding side to left for decoder-only models (required for batching)
        self.tokenizer.padding_side = 'left'
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_config['base_model_path'],
            torch_dtype=getattr(torch, model_config['torch_dtype']),
            device_map=model_config['device_map']
        )
        
        adapter_path = model_config.get("adapter_path")

        if adapter_path:
            print(f"Loading adapter from {adapter_path}...")
            self.model = PeftModel.from_pretrained(self.model, adapter_path)
        else:
            print("No adapter provided, using base model")

        self.model.eval()
        print("Model loaded successfully!")
    
    def generate_candidates(
        self, 
        old_password: str, 
        prompt_template: str,
        num_candidates: int = None,
        temperature: float = None
    ) -> List[str]:
        """
        Generate password candidates for a given old password
        
        Args:
            old_password: The old password to base generation on
            prompt_template: Prompt template with {old_password} placeholder
            num_candidates: Number of candidates to generate (uses config if None)
            temperature: Sampling temperature (uses config if None)
            
        Returns:
            List of unique password candidates
        """
        if num_candidates is None:
            num_candidates = self.gen_config['num_return_sequences']
        if temperature is None:
            temperature = self.gen_config['temperature']
        
        # Format prompt
        prompt = prompt_template.format(old_password=old_password)
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.gen_config['max_new_tokens'],
                num_return_sequences=num_candidates,
                do_sample=True,
                temperature=temperature,
                top_p=self.gen_config['top_p'],
                top_k=self.gen_config['top_k'],
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode and extract passwords
        generated_texts = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        
        passwords: Set[str] = set()
        for text in generated_texts:
            extracted = self._extract_passwords(text, prompt)
            passwords.update(extracted)
        
        # Always include old password as fallback
        passwords.add(old_password)
        
        return list(passwords)
    
    def _extract_passwords(self, text: str, prompt: str) -> List[str]:
        """
        Extract passwords from generated text
        
        Args:
            text: Generated text from model
            prompt: Original prompt (to remove from output)
            
        Returns:
            List of extracted passwords
        """
        # Remove prompt from text
        if prompt in text:
            text = text[len(prompt):].strip()
        
        passwords = []
        
        # Look for common output markers
        markers = ['Passwords:', 'Output:', 'Generated:', 'New passwords:',
                   'Candidates:', 'List:', 'Results:', 'New:', 'passwords:']
        
        for marker in markers:
            if marker in text:
                text = text.split(marker)[-1].strip()
                break
        
        # Split by newlines, commas, and semicolons
        # First split by newlines
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Also try splitting by comma or semicolon
            if ',' in line or ';' in line:
                sub_items = line.replace(';', ',').split(',')
                for item in sub_items:
                    item = item.strip()
                    # Remove common prefixes
                    for prefix in ['- ', '* ', '• ', '1. ', '2. ', '3. ', '4. ', '5. ',
                                  '6. ', '7. ', '8. ', '9. ', '10. ', '11. ', '12. ']:
                        if item.startswith(prefix):
                            item = item[len(prefix):].strip()
                    
                    # Remove quotes and brackets
                    item = item.strip('"\'[](){}')
                    
                    # Validate password
                    if self._is_valid_password(item):
                        passwords.append(item)
            else:
                # Remove common prefixes
                for prefix in ['- ', '* ', '• ', '1. ', '2. ', '3. ', '4. ', '5. ',
                              '6. ', '7. ', '8. ', '9. ', '10. ', '11. ', '12. ']:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                
                # Remove quotes and brackets
                line = line.strip('"\'[](){}')
                
                # Validate password
                if self._is_valid_password(line):
                    passwords.append(line)
        
        return passwords
    
    def _is_valid_password(self, pwd: str) -> bool:
        """
        Check if string looks like a valid password
        
        Args:
            pwd: Potential password string
            
        Returns:
            True if valid password candidate
        """
        if not pwd or len(pwd) == 0:
            return False
        
        if len(pwd) < 3:  # Too short
            return False
        
        if len(pwd) > 50:  # Too long
            return False
        
        # Allow passwords with spaces if they look reasonable
        # But skip if too many spaces
        if pwd.count(' ') > 2:
            return False
        
        # Skip lines that look like instructions or explanations
        skip_words = ['password', 'generate', 'example', 'old', 'new',
                     'based', 'using', 'apply', 'transform', 'given',
                     'create', 'make', 'change', 'add', 'try', 'user',
                     'increment', 'append', 'prepend', 'substitute',
                     'pattern', 'strategy', 'focus', 'avoid', 'keep']
        
        pwd_lower = pwd.lower()
        if any(word in pwd_lower for word in skip_words):
            return False
        
        # Skip if it looks like a sentence (has multiple words)
        if ' ' in pwd and len(pwd.split()) > 3:
            return False
        
        return True
    
    def generate_for_dataset(
        self,
        data: List[dict],
        prompt_template: str,
        show_progress: bool = True
    ) -> List[str]:
        """
        Generate best password for each entry in dataset
        
        Args:
            data: List of data entries with 'Knowledge'/'Old password'
            prompt_template: Prompt template to use
            show_progress: Whether to show progress bar
            
        Returns:
            List of generated passwords (one per entry)
        """
        results = []
        
        iterator = tqdm(data, desc="Generating passwords") if show_progress else data
        
        for entry in iterator:
            old_password = entry['Knowledge']['Old password']
            candidates = self.generate_candidates(old_password, prompt_template)
            # Take first (best) candidate
            best_password = candidates[0] if candidates else old_password
            results.append(best_password)
        
        return results


def load_prompt_template(prompt_file: str) -> str:
    """
    Load prompt template from file
    
    Args:
        prompt_file: Path to prompt template file
        
    Returns:
        Prompt template string
    """
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()

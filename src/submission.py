"""
Submission Generator Module
Creates final submission CSV file for competition
"""

import json
import csv
from typing import List
from tqdm import tqdm
from src.generator import PasswordGenerator


def generate_submission(
    generator: PasswordGenerator,
    test_data_path: str,
    prompt_template: str,
    output_csv: str,
    output_json: str = None
):
    """
    Generate submission file for test data
    
    Args:
        generator: PasswordGenerator instance
        test_data_path: Path to test.json
        prompt_template: Prompt template to use
        output_csv: Output CSV file path
        output_json: Optional output JSON file path
    """
    print(f"Loading test data from {test_data_path}...")
    with open(test_data_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    print(f"Generating passwords for {len(test_data)} entries...")
    
    results = []
    
    for entry in tqdm(test_data, desc="Generating"):
        old_password = entry['Knowledge']['Old password']
        
        # Generate candidates and take best (first) one
        candidates = generator.generate_candidates(old_password, prompt_template)
        best_password = candidates[0] if candidates else old_password
        
        results.append(best_password)
    
    # Save CSV
    print(f"Saving submission to {output_csv}...")
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'password', 'usage'])
        
        for i, password in enumerate(results):
            writer.writerow([i, password, 'Public'])
    
    print(f"✓ Submission saved to {output_csv}")
    
    # Optionally save JSON
    if output_json:
        json_results = [{'password': pwd} for pwd in results]
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        print(f"✓ Predictions saved to {output_json}")
    
    print(f"\nGenerated {len(results)} passwords")
    return results


def generate_multi_candidate_submission(
    generator: PasswordGenerator,
    test_data_path: str,
    prompt_template: str,
    output_csv: str,
    max_candidates: int = 100
):
    """
    Generate submission with multiple candidates per password
    
    Args:
        generator: PasswordGenerator instance
        test_data_path: Path to test.json
        prompt_template: Prompt template to use
        output_csv: Output CSV file path
        max_candidates: Maximum candidates per password
    """
    print(f"Loading test data from {test_data_path}...")
    with open(test_data_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    print(f"Generating {max_candidates} candidates for {len(test_data)} entries...")
    
    all_candidates = []
    
    for entry in tqdm(test_data, desc="Generating"):
        old_password = entry['Knowledge']['Old password']
        
        # Generate many candidates with different temperatures
        candidates = set()
        candidates.add(old_password)  # Always include old password
        
        # Generate with multiple temperatures for diversity
        for temp in [0.6, 0.8, 1.0]:
            batch = generator.generate_candidates(
                old_password, 
                prompt_template,
                num_candidates=max_candidates // 3,
                temperature=temp
            )
            candidates.update(batch)
            
            if len(candidates) >= max_candidates:
                break
        
        # Add rule-based candidates if needed
        if len(candidates) < max_candidates:
            rule_based = _generate_rule_based_candidates(old_password)
            candidates.update(rule_based)
        
        # Convert to list and pad/trim to exact size
        candidate_list = list(candidates)[:max_candidates]
        while len(candidate_list) < max_candidates:
            candidate_list.append(old_password)
        
        all_candidates.append(candidate_list)
    
    # Save CSV with multiple candidates
    print(f"Saving submission to {output_csv}...")
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        header = ['id'] + [f'password{i+1}' for i in range(max_candidates)]
        writer.writerow(header)
        
        # Data
        for i, candidates in enumerate(all_candidates):
            row = [i] + candidates
            writer.writerow(row)
    
    print(f"✓ Multi-candidate submission saved to {output_csv}")
    print(f"Generated {len(all_candidates)} entries with {max_candidates} candidates each")


def _generate_rule_based_candidates(old_password: str) -> List[str]:
    """
    Generate candidates using rule-based transformations
    
    Args:
        old_password: Old password
        
    Returns:
        List of candidate passwords
    """
    candidates = set()
    
    # Append numbers
    for num in ['1', '12', '123', '1234', '321', '2024', '2025', '2026', '2027']:
        candidates.add(old_password + num)
    
    # Append symbols
    for sym in ['!', '@', '#', '$', '!!', '@@', '!@', '@!']:
        candidates.add(old_password + sym)
    
    # Append year + symbol
    for year in ['2024', '2025', '2026']:
        for sym in ['!', '@', '#']:
            candidates.add(old_password + year + sym)
            candidates.add(old_password + sym + year)
    
    # Capitalize
    if old_password:
        candidates.add(old_password.capitalize())
        candidates.add(old_password.upper())
        candidates.add(old_password.lower())
    
    # Prepend
    for prefix in ['!', '@', '#', '1', '12']:
        candidates.add(prefix + old_password)
    
    # Leetspeak
    leet_map = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$', 't': '7'}
    leet_pwd = old_password.lower()
    for char, replacement in leet_map.items():
        leet_pwd = leet_pwd.replace(char, replacement)
    candidates.add(leet_pwd)
    
    # Reverse
    candidates.add(old_password[::-1])
    
    # Double last char
    if old_password:
        candidates.add(old_password + old_password[-1])
    
    # Keyboard patterns
    for pattern in ['qwerty', 'asdf', 'zxcv', '123456']:
        candidates.add(old_password + pattern)
    
    return list(candidates)


def load_best_prompt_from_evolution(evolution_results_path: str) -> str:
    """
    Load best prompt from evolution results
    
    Args:
        evolution_results_path: Path to evolution results JSON
        
    Returns:
        Best prompt template string
    """
    with open(evolution_results_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    return results['best_prompt']['text']

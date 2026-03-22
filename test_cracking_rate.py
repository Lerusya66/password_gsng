#!/usr/bin/env python3
"""
Test script to verify cracking rate calculation
"""

import json
from src.generator import PasswordGenerator, load_prompt_template
from src.evaluator import FitnessEvaluator

def main():
    print("="*70)
    print("TESTING CRACKING RATE CALCULATION")
    print("="*70)
    
    # Load configuration
    print("\n1. Loading configuration...")
    with open('configs/config.json', 'r') as f:
        config = json.load(f)
    
    # Initialize generator
    print("\n2. Initializing password generator...")
    generator = PasswordGenerator(config)
    
    # Load test data (small sample)
    print("\n3. Loading test data...")
    with open(config['data']['train_path'], 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Test on first 10 samples
    test_samples = data[:10]
    
    # Load prompt
    print("\n4. Loading prompt template...")
    if config['paths']['initial_prompt']:
        prompt_template = load_prompt_template(config['paths']['initial_prompt'])
    else:
        prompt_template = """You are a password prediction expert. Given an old password, predict the most likely new password.

Old password: {old_password}

Passwords:"""
    
    print("\n5. Testing password generation and extraction...")
    print("-"*70)
    
    correct = 0
    total = len(test_samples)
    
    for i, entry in enumerate(test_samples):
        old_password = entry['Knowledge']['Old password']
        true_password = entry['password']
        
        print(f"\nTest {i+1}/{total}:")
        print(f"  Old password: {old_password}")
        print(f"  True password: {true_password}")
        
        # Generate candidates
        candidates = generator.generate_candidates(
            old_password,
            prompt_template,
            num_candidates=10
        )
        
        print(f"  Generated {len(candidates)} candidates:")
        for j, cand in enumerate(candidates[:5], 1):
            marker = "✓" if cand == true_password else " "
            print(f"    {marker} {j}. {cand}")
        
        if len(candidates) > 5:
            print(f"    ... and {len(candidates) - 5} more")
        
        if true_password in candidates:
            correct += 1
            print(f"  ✓ SUCCESS: True password found in candidates!")
        else:
            print(f"  ✗ FAILED: True password not in candidates")
    
    cracking_rate = (correct / total) * 100
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Cracked: {correct}/{total}")
    print(f"Cracking rate: {cracking_rate:.2f}%")
    print("="*70)
    
    if cracking_rate < 20:
        print("\n⚠️  WARNING: Cracking rate is very low!")
        print("This suggests issues with:")
        print("  - Password extraction from model output")
        print("  - Prompt template effectiveness")
        print("  - Model quality")
    elif cracking_rate < 40:
        print("\n⚠️  Cracking rate is moderate. Room for improvement.")
    else:
        print("\n✓ Cracking rate looks good!")

if __name__ == "__main__":
    main()

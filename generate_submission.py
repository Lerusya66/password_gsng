#!/usr/bin/env python3
"""
Generate final submission CSV file
"""

import json
import os
import sys
from src.generator import PasswordGenerator, load_prompt_template
from src.submission import generate_submission, generate_multi_candidate_submission, load_best_prompt_from_evolution


def main():
    # Load configuration
    print("Loading configuration...")
    with open('configs/config.json', 'r') as f:
        config = json.load(f)
    
    print("\n" + "="*70)
    print("PASSWORD GUESSING - SUBMISSION GENERATION")
    print("="*70)
    
    # Initialize generator
    print("\nInitializing password generator...")
    generator = PasswordGenerator(config)
    
    # Load best prompt
    evolution_log = config['paths']['evolution_log']
    best_prompt_file = config['paths']['best_prompt_file']
    
    if os.path.exists(evolution_log):
        print(f"\nLoading best prompt from evolution results: {evolution_log}")
        prompt_template = load_best_prompt_from_evolution(evolution_log)
    elif os.path.exists(best_prompt_file):
        print(f"\nLoading best prompt from: {best_prompt_file}")
        prompt_template = load_prompt_template(best_prompt_file)
    else:
        print("\nERROR: No prompt found!")
        print("Please run run_evolution.py first or provide a prompt file.")
        prompt_template = """You are a password prediction expert. Given an old password, predict the most likely new password.

CRITICAL INSIGHTS from data analysis:
- 30.84% of passwords remain UNCHANGED - this is the most important pattern!
- 20.97% add numbers at the end
- 47.41% have other complex changes
- Average length increase: 1.6 characters
- 91% contain numbers, only 4.5% have special characters

PREDICTION STRATEGY (in order of priority):
1. FIRST CANDIDATE: Return the old password unchanged (highest probability!)
2. If numbers at end: Try incrementing them or adding more digits
3. Add common number sequences: 123, 1234, 2024, 2025, 888, 666, 520, 1314
4. Add 1-4 digits at the end
5. Duplicate parts of the password
6. Make small character substitutions

IMPORTANT: 
- Focus on NUMBER-based changes (91% of passwords have numbers)
- Avoid special characters (only 4.5% use them)
- Keep changes minimal (average +1.6 chars)
- The FIRST password you generate should be the MOST LIKELY one

Old password: {old_password}

Passwords:"""
        #sys.exit(1)
    
    # Generate submission
    print("\nGenerating submission...")
    generate_multi_candidate_submission(
        generator=generator,
        test_data_path=config['data']['test_path'],
        prompt_template=prompt_template,
        output_csv=config['paths']['submission_csv'],
        max_candidates=100
    )

    
    print("\n" + "="*70)
    print("SUBMISSION GENERATION COMPLETE")
    print("="*70)
    print(f"\n✓ Submission file: {config['paths']['submission_csv']}")
    print(f"✓ Predictions file: {config['paths']['predictions_json']}")
    print("\nYou can now submit the CSV file to the competition!")


if __name__ == "__main__":
    main()

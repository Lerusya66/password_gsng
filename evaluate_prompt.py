#!/usr/bin/env python3
"""
Evaluate a prompt on training data
"""

import json
import sys
import argparse
from src.generator import PasswordGenerator, load_prompt_template
from src.evaluator import evaluate_on_full_train


def main():
    parser = argparse.ArgumentParser(description='Evaluate prompt on training data')
    parser.add_argument('--prompt', type=str, required=True,
                        help='Path to prompt template file')
    parser.add_argument('--max_samples', type=int, default=1000,
                        help='Maximum samples to evaluate (default: 1000)')
    parser.add_argument('--num_candidates', type=int, default=10,
                        help='Number of candidates per password (default: 10)')
    parser.add_argument('--config', type=str, default='configs/config.json',
                        help='Path to config file (default: configs/config.json)')
    
    args = parser.parse_args()
    
    # Load configuration
    print("Loading configuration...")
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    print("\n" + "="*70)
    print("PROMPT EVALUATION")
    print("="*70)
    
    # Load prompt
    print(f"\nLoading prompt from {args.prompt}...")
    prompt_template = load_prompt_template(args.prompt)
    
    # Initialize generator
    print("\nInitializing password generator...")
    generator = PasswordGenerator(config)
    
    # Evaluate
    print(f"\nEvaluating on up to {args.max_samples} samples...")
    results = evaluate_on_full_train(
        generator=generator,
        prompt_template=prompt_template,
        train_path=config['data']['train_path'],
        max_samples=args.max_samples,
        num_candidates=args.num_candidates
    )
    
    # Print results
    print("\n" + "="*70)
    print("EVALUATION RESULTS")
    print("="*70)
    print(f"Total samples: {results['total']}")
    print(f"Correct guesses: {results['correct']}")
    print(f"Cracked rate: {results['cracked_rate']:.2f}%")
    print(f"Candidates per password: {results['num_candidates']}")
    print("="*70)


if __name__ == "__main__":
    main()

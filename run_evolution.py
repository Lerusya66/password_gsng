#!/usr/bin/env python3
"""
Main script to run prompt evolution
"""

import json
import os
import sys
from src.generator import PasswordGenerator, load_prompt_template
from src.evaluator import FitnessEvaluator
from src.evolution import PromptEvolver


def main():
    # Load configuration
    print("Loading configuration...")
    with open('configs/config.json', 'r') as f:
        config = json.load(f)
    
    # Create output directory
    os.makedirs(config['paths']['output_dir'], exist_ok=True)
    
    print("\n" + "="*70)
    print("PASSWORD GUESSING - PROMPT EVOLUTION")
    print("="*70)
    
    # Initialize generator (loads model once)
    print("\nStep 1: Initializing password generator...")
    generator = PasswordGenerator(config)
    
    # Initialize evaluator
    print("\nStep 2: Initializing fitness evaluator...")
    evaluator = FitnessEvaluator(config, generator)
    
    # Enable interactive logging
    evaluator.enable_logging()

    # Initialize evolver
    print("\nStep 3: Initializing evolutionary optimizer...")
    evolver = PromptEvolver(config)
    
    # Load initial prompt if exists
    initial_prompt = None
    if os.path.exists(config['paths']['initial_prompt']):
        print(f"\nLoading initial prompt from {config['paths']['initial_prompt']}...")
        initial_prompt = load_prompt_template(config['paths']['initial_prompt'])
    
    # Initialize population
    print("\nStep 4: Initializing population...")
    evolver.initialize_population(initial_prompt)
    
    # Run evolution
    print("\nStep 5: Running evolution...")
    print(f"Generations: {config['evolution']['num_generations']}")
    print(f"Population size: {config['evolution']['population_size']}")
    print(f"Validation size: {config['evaluation']['val_size']}")
    
    best_prompt = evolver.evolve(evaluator, verbose=True)
    
    # Save results
    print("\n" + "="*70)
    print("EVOLUTION COMPLETE")
    print("="*70)
    print(f"\nBest fitness: {best_prompt.fitness:.2f}%")
    print(f"Generation: {best_prompt.generation}")
    
    # Save best prompt
    best_prompt_file = config['paths']['best_prompt_file']
    with open(best_prompt_file, 'w', encoding='utf-8') as f:
        f.write(best_prompt.text)
    print(f"\n✓ Best prompt saved to {best_prompt_file}")
    
    # Save evolution log
    evolution_log = config['paths']['evolution_log']
    evolver.save_results(evolution_log)
    print(f"✓ Evolution log saved to {evolution_log}")
    
    print("\n" + "="*70)
    print("Next step: Run generate_submission.py to create final submission")
    print("="*70)


if __name__ == "__main__":
    main()

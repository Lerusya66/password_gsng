#!/usr/bin/env python3
"""
Quick test to verify the setup is correct
"""

import os
import sys
import json

def test_structure():
    """Test that all required files and directories exist"""
    print("Testing project structure...")
    
    required_dirs = ['src', 'configs', 'data', 'outputs', 'models']
    required_files = [
        'configs/config.json',
        'src/generator.py',
        'src/evaluator.py',
        'src/evolution.py',
        'src/submission.py',
        'run_evolution.py',
        'generate_submission.py',
        'evaluate_prompt.py',
        'requirements.txt',
        'README.md',
        'README_detailed.md'
    ]
    
    # Check directories
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ Directory exists: {dir_name}")
        else:
            print(f"✗ Missing directory: {dir_name}")
            if dir_name != 'models':  # models is optional
                return False
    
    # Check files
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✓ File exists: {file_name}")
        else:
            print(f"✗ Missing file: {file_name}")
            return False
    
    return True

def test_config():
    """Test that config file is valid JSON"""
    print("\nTesting configuration...")
    
    try:
        with open('configs/config.json', 'r') as f:
            config = json.load(f)
        
        required_keys = ['model', 'data', 'evolution', 'evaluation', 'generation', 'paths']
        for key in required_keys:
            if key in config:
                print(f"✓ Config has '{key}' section")
            else:
                print(f"✗ Config missing '{key}' section")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return False

def test_imports():
    """Test that all modules can be imported"""
    print("\nTesting module imports...")
    
    try:
        from src import generator
        print("✓ Can import src.generator")
    except Exception as e:
        print(f"✗ Cannot import src.generator: {e}")
        return False
    
    try:
        from src import evaluator
        print("✓ Can import src.evaluator")
    except Exception as e:
        print(f"✗ Cannot import src.evaluator: {e}")
        return False
    
    try:
        from src import evolution
        print("✓ Can import src.evolution")
    except Exception as e:
        print(f"✗ Cannot import src.evolution: {e}")
        return False
    
    try:
        from src import submission
        print("✓ Can import src.submission")
    except Exception as e:
        print(f"✗ Cannot import src.submission: {e}")
        return False
    
    return True

def test_data():
    """Test that data files exist"""
    print("\nTesting data files...")
    
    data_files = ['data/train.json', 'data/test.json', 'data/prompt.txt']
    
    for file_name in data_files:
        if os.path.exists(file_name):
            print(f"✓ Data file exists: {file_name}")
        else:
            print(f"⚠ Data file missing: {file_name} (may need to be added)")
    
    return True

def main():
    print("="*70)
    print("PASSWORD GUESSING - SETUP TEST")
    print("="*70)
    
    tests = [
        ("Project Structure", test_structure),
        ("Configuration", test_config),
        ("Module Imports", test_imports),
        ("Data Files", test_data)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All tests passed! Setup is correct.")
        print("\nNext steps:")
        print("1. Ensure models are in .model/ directory")
        print("2. Ensure adapters are in place")
        print("3. Run: python run_evolution.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Project Structure

This document shows the final clean structure of the refactored password guessing project.

## Directory Tree

```
password-guessing/
│
├── src/                          # Core modules (clean, modular code)
│   ├── generator.py              # Password generation using PassLLM
│   ├── evaluator.py              # Fitness evaluation on validation set
│   ├── evolution.py              # Evolutionary algorithm for prompt optimization
│   └── submission.py             # Submission file generation
│
├── configs/                      # Configuration files
│   └── config.json               # Centralized configuration (all parameters)
│
├── data/                         # Data files
│   ├── train.json                # Training data
│   ├── test.json                 # Test data
│   └── prompt.txt                # Initial prompt template
│
├── outputs/                      # Generated outputs
│   ├── best_prompt.txt           # Best evolved prompt (created by run_evolution.py)
│   ├── evolution_log.json        # Evolution history (created by run_evolution.py)
│   ├── submission.csv            # Final submission (created by generate_submission.py)
│   └── predictions.json          # Predictions in JSON format
│
├── models/                       # Placeholder for model files
│
├── .model/                       # Base models (downloaded separately)
│   └── Qwen2.5-0.5B-Instruct/    # Base model
│
├── rockyou_100w_disQwen0.5B/     # LoRA adapter weights
│   └── rockyou_100w_disQwen0.5B/
│
├── 126_csdn_disQwen0.5B/         # Alternative LoRA adapter
│   └── 126_csdn_disQwen0.5B/
│
├── run_evolution.py              # Main script: Run prompt evolution
├── generate_submission.py        # Generate final submission CSV
├── evaluate_prompt.py            # Evaluate a prompt on training data
├── test_setup.py                 # Test that setup is correct
│
├── requirements.txt              # Python dependencies
├── setup_models.sh               # Script to download models
│
├── README.md                     # Quick start guide (concise)
└── README_detailed.md            # Detailed documentation (comprehensive)
```

## File Descriptions

### Core Modules (`src/`)

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `generator.py` | Password generation using PassLLM | `PasswordGenerator` |
| `evaluator.py` | Fitness evaluation | `FitnessEvaluator`, `evaluate_on_full_train()` |
| `evolution.py` | Evolutionary optimization | `PromptEvolver`, `Prompt` |
| `submission.py` | Submission generation | `generate_submission()`, `load_best_prompt_from_evolution()` |

### Executable Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `run_evolution.py` | Run prompt evolution | `python3 run_evolution.py` |
| `generate_submission.py` | Create submission CSV | `python3 generate_submission.py` |
| `evaluate_prompt.py` | Test a prompt | `python3 evaluate_prompt.py --prompt data/prompt.txt` |
| `test_setup.py` | Verify setup | `python3 test_setup.py` |

### Configuration

| File | Purpose |
|------|---------|
| `configs/config.json` | All tunable parameters (model paths, evolution params, generation params) |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Quick start guide (2-3 minutes to understand and run) |
| `README_detailed.md` | Comprehensive documentation (architecture, algorithms, extensions) |
| `PROJECT_STRUCTURE.md` | This file - project structure overview |

## What Was Removed

The following redundant/temporary files were removed during refactoring:

### Redundant Scripts
- `password_generator.py` → Replaced by `src/generator.py`
- `prompt_evolution.py` → Replaced by `src/evolution.py`
- `evolutionary_optimizer.py` → Replaced by `src/evolution.py`
- `fitness_evaluator.py` → Replaced by `src/evaluator.py`
- `submission_generator.py` → Replaced by `src/submission.py`
- `example_usage.py` → Functionality integrated into main scripts
- `check_setup.py` → Replaced by `test_setup.py`
- `analyze_data.py` → Not needed for production
- `test_system.py` → Replaced by `test_setup.py`

### Redundant Documentation
- `EVOLUTION_GUIDE.md` → Merged into `README_detailed.md`
- `QUICKSTART_EVOLUTION.md` → Merged into `README.md`
- `README_EVOLUTION.md` → Merged into `README.md`
- `QUICKSTART.md` → Merged into `README.md`
- `PIPELINE_SUMMARY.md` → Merged into `README_detailed.md`
- `SYSTEM_SUMMARY.md` → Merged into `README_detailed.md`
- `FINAL_INSTRUCTIONS.md` → Merged into `README.md`

### Temporary Files
- `prompt_v2.txt`, `prompt_v3.txt`, `prompt_optimized.txt` → Moved to `data/prompt.txt`
- `submission_promt.txt` → Removed (typo in name)
- `sample_submission.csv`, `submission.csv` → Will be generated in `outputs/`
- `run_pipeline.sh` → Replaced by Python scripts
- `requirements_evolution.txt` → Merged into `requirements.txt`

### External Dependencies
- `evolution/` directory → Removed (unused)
- `openevolve/` directory → Removed (not needed, implemented our own evolution)
- `PassLLM/` directory → Removed (only need the trained adapters)

## Key Improvements

### 1. **Centralized Configuration**
- All parameters in one place: `configs/config.json`
- No hardcoded values in code
- Easy to adjust without editing code

### 2. **Modular Architecture**
- Clear separation of concerns
- Each module has single responsibility
- Easy to test and extend

### 3. **Clean Code**
- Removed duplicated logic
- Clear naming conventions
- Comprehensive docstrings
- Type hints where appropriate

### 4. **Better Documentation**
- Concise README for quick start
- Detailed README for deep understanding
- Clear project structure

### 5. **Simplified Workflow**
```bash
# Before (confusing)
python prompt_evolution.py
python evolutionary_optimizer.py
python submission_generator.py --checkpoint ...

# After (clear)
python3 run_evolution.py
python3 generate_submission.py
```

## Usage Workflow

### Standard Workflow
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify setup
python3 test_setup.py

# 3. Run evolution
python3 run_evolution.py

# 4. Generate submission
python3 generate_submission.py
```

### Development Workflow
```bash
# Test a prompt
python3 evaluate_prompt.py --prompt data/prompt.txt --max_samples 500

# Adjust config
vim configs/config.json

# Re-run evolution
python3 run_evolution.py
```

## Configuration Examples

### Quick Test (Fast)
```json
{
  "evolution": {
    "num_generations": 5,
    "population_size": 10
  },
  "evaluation": {
    "val_size": 50,
    "num_candidates": 5
  }
}
```

### Production Run (Best Results)
```json
{
  "evolution": {
    "num_generations": 20,
    "population_size": 30
  },
  "evaluation": {
    "val_size": 300,
    "num_candidates": 15
  }
}
```

## Next Steps

1. **Ensure models are downloaded**: Check `.model/` directory
2. **Verify adapters are in place**: Check adapter directories
3. **Run test**: `python3 test_setup.py`
4. **Start evolution**: `python3 run_evolution.py`
5. **Generate submission**: `python3 generate_submission.py`

## Maintenance

### Adding New Features
- New mutation operators → Edit `src/evolution.py`
- New fitness metrics → Edit `src/evaluator.py`
- New generation strategies → Edit `src/generator.py`
- New submission formats → Edit `src/submission.py`

### Adjusting Parameters
- All parameters → Edit `configs/config.json`
- No code changes needed for parameter tuning

### Debugging
- Check logs in terminal output
- Inspect `outputs/evolution_log.json` for evolution history
- Use `evaluate_prompt.py` to test individual prompts

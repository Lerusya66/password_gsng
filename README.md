# Password Guessing with PassLLM + Prompt Evolution

Automated password generation using fine-tuned PassLLM with evolutionary prompt optimization.

## 🎯 What This Does

Generates likely new passwords based on old passwords using:
1. **PassLLM** - Fine-tuned language model for password generation
2. **Prompt Evolution** - Evolutionary algorithm to optimize generation prompts
3. **Fitness Evaluation** - Tests prompts on validation data to maximize cracked rate

**Baseline**: 56.31% cracked rate  
**Target**: 60-65%+ with optimized prompts

## 🚀 Quick Start

### 1. Install Dependencies

python3 -m venv venv
source venv/bin/activate 

```bash
pip install -r requirements.txt
```

### 2. Setup Models

Download base models to `.model/` directory:
- [Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)

Ensure adapter weights are in place:
- `rockyou_100w_disQwen0.5B/rockyou_100w_disQwen0.5B/`
- `126_csdn_disQwen0.5B/126_csdn_disQwen0.5B/`

### 3. Run Prompt Evolution

```bash
python run_evolution.py
```

This will:
- Initialize population of diverse prompts
- Evolve prompts over 10 generations
- Save best prompt to `outputs/best_prompt.txt`
- Save evolution log to `outputs/evolution_log.json`

**Time**: ~30-60 minutes depending on hardware

### 4. Generate Submission

```bash
python generate_submission.py
```

Creates `outputs/submission.csv` ready for submission.

## 📊 Evaluate a Prompt

Test any prompt on training data:

```bash
python evaluate_prompt.py --prompt data/prompt_optimized.txt --max_samples 16000
```

## ⚙️ Configuration

All parameters are in [`configs/config.json`](configs/config.json):

```json
{
  "evolution": {
    "population_size": 20,      // Number of prompts in population
    "num_generations": 10,      // Evolution iterations
    "mutation_rate": 0.7        // Probability of mutation
  },
  "evaluation": {
    "val_size": 200,            // Validation set size
    "num_candidates": 10        // Candidates per password
  },
  "generation": {
    "temperature": 0.8,         // Sampling temperature
    "top_p": 0.95              // Nucleus sampling
  }
}
```

## 📁 Project Structure

```
password-guessing/
├── src/
│   ├── generator.py       # Password generation
│   ├── evaluator.py       # Fitness evaluation
│   ├── evolution.py       # Evolutionary algorithm
│   └── submission.py      # Submission creation
├── configs/
│   └── config.json        # All parameters
├── data/
│   ├── train.json         # Training data
│   ├── test.json          # Test data
│   └── prompt.txt         # Initial prompt
├── outputs/
│   ├── best_prompt.txt    # Best evolved prompt
│   ├── evolution_log.json # Evolution history
│   └── submission.csv     # Final submission
├── run_evolution.py       # Run evolution
├── generate_submission.py # Create submission
└── evaluate_prompt.py     # Test prompts
```

## 🔧 Advanced Usage

### Use Different Adapter

Edit [`configs/config.json`](configs/config.json):

```json
{
  "model": {
    "adapter_path": "126_csdn_disQwen0.5B/126_csdn_disQwen0.5B"
  }
}
```

### Adjust Evolution Parameters

Increase generations for better results (slower):

```json
{
  "evolution": {
    "num_generations": 20,
    "population_size": 30
  }
}
```

### Quick Test Run

Reduce validation size for faster iteration:

```json
{
  "evaluation": {
    "val_size": 50
  }
}
```

## 📈 Expected Results

- **Initial prompt**: ~56-58% cracked rate
- **After 10 generations**: ~60-62% cracked rate
- **After 20 generations**: ~62-65% cracked rate

## 🐛 Troubleshooting

**CUDA out of memory**:
- Reduce `batch_size` in config
- Use `torch_dtype: "float32"` instead of `"float16"`

**Slow generation**:
- Reduce `val_size` in config
- Reduce `num_candidates` in config
- Use GPU if available

**Model not found**:
```bash
ls -la .model/
# Ensure Qwen2.5-0.5B-Instruct exists
```

## 📚 More Information

See [`README_detailed.md`](README_detailed.md) for:
- System architecture
- Algorithm details
- Design decisions
- Extension guide

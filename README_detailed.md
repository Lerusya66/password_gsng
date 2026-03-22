# Password Guessing - Detailed Documentation

Complete technical documentation for the password guessing system using PassLLM and evolutionary prompt optimization.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Pipeline Details](#pipeline-details)
4. [Design Decisions](#design-decisions)
5. [Implementation Details](#implementation-details)
6. [Extension Guide](#extension-guide)

---

## System Overview

### What is PassLLM?

PassLLM is a fine-tuned language model specifically trained for password generation. It learns patterns from password datasets and can generate likely password candidates based on:
- Old passwords from the same user
- Common password update patterns
- Human behavior in password creation

**Key Features**:
- Based on Qwen2.5-0.5B-Instruct (small, fast model)
- Fine-tuned with LoRA adapters on password datasets
- Generates contextually relevant password candidates

### What is Prompt Evolution?

Prompt evolution is an evolutionary algorithm that optimizes the prompt used to guide PassLLM. Instead of manually crafting prompts, the system:
1. Creates a population of diverse prompts
2. Evaluates each prompt's effectiveness (fitness)
3. Evolves better prompts through mutation and crossover
4. Iterates to find optimal prompts

**Why Evolution?**:
- Automates prompt engineering
- Discovers non-obvious patterns
- Adapts to specific datasets
- Continuously improves results

### How They Combine

```
┌─────────────────┐
│  Initial Prompt │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Evolutionary Optimizer     │
│  - Population of prompts    │
│  - Mutation & Crossover     │
│  - Fitness-based selection  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Fitness Evaluator          │
│  - Tests on validation data │
│  - Calculates cracked rate  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  PassLLM Generator          │
│  - Generates candidates     │
│  - Uses evolved prompt      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Best Prompt → Submission   │
└─────────────────────────────┘
```

---

## Architecture

### Module Structure

#### 1. **generator.py** - Password Generation
- Loads PassLLM model with LoRA adapter
- Generates password candidates using prompts
- Extracts and validates passwords from model output
- Handles batching and sampling parameters

**Key Class**: `PasswordGenerator`
- `generate_candidates()`: Generate multiple password candidates
- `_extract_passwords()`: Parse model output
- `_is_valid_password()`: Filter invalid outputs

#### 2. **evaluator.py** - Fitness Evaluation
- Evaluates prompt quality on validation set
- Calculates cracked rate (% of correct guesses)
- Caches results for efficiency
- Manages train/validation split

**Key Class**: `FitnessEvaluator`
- `evaluate()`: Calculate fitness (cracked rate)
- `evaluate_with_details()`: Get detailed metrics

#### 3. **evolution.py** - Evolutionary Algorithm
- Implements genetic algorithm for prompts
- Mutation: Small changes to prompts
- Crossover: Combines two parent prompts
- Selection: Tournament selection based on fitness
- Elitism: Preserves best prompts

**Key Class**: `PromptEvolver`
- `initialize_population()`: Create diverse initial prompts
- `evolve()`: Run evolution loop
- `_mutate_prompt()`: Apply mutations
- `_crossover()`: Combine parent prompts

#### 4. **submission.py** - Submission Generation
- Generates final predictions for test set
- Creates CSV in competition format
- Supports multi-candidate generation
- Includes rule-based fallbacks

**Key Functions**:
- `generate_submission()`: Create final CSV
- `generate_multi_candidate_submission()`: Multiple candidates per password
- `_generate_rule_based_candidates()`: Fallback transformations

---

## Pipeline Details

### Evolution Loop

```python
for generation in range(num_generations):
    # 1. Evaluate all prompts
    for prompt in population:
        prompt.fitness = evaluator.evaluate(prompt.text)
    
    # 2. Sort by fitness
    population.sort(key=lambda p: p.fitness, reverse=True)
    
    # 3. Create next generation
    new_population = []
    
    # 3a. Elitism - keep best
    new_population.extend(population[:elite_size])
    
    # 3b. Generate offspring
    while len(new_population) < population_size:
        if random() < crossover_rate:
            parent1 = tournament_selection()
            parent2 = tournament_selection()
            child = crossover(parent1, parent2)
        else:
            parent = tournament_selection()
            child = mutate(parent)
        
        new_population.append(child)
    
    population = new_population
```

### Evaluation Strategy

**Why Use a Subset?**
- Full dataset evaluation is too slow (4000 samples × 10 candidates × 20 prompts)
- Validation subset (200 samples) provides reliable fitness estimate
- Allows rapid iteration during evolution
- Final evaluation can use full training set

**Why K Candidates?**
- Real-world scenario: generate K guesses per password
- Cracked rate = % of passwords where true password is in top-K
- K=10 balances accuracy and speed
- Higher K increases cracked rate but slows evaluation

### Generation Strategy

**Sampling Parameters**:
- `temperature`: Controls randomness (0.8 = balanced)
- `top_p`: Nucleus sampling (0.95 = diverse but focused)
- `top_k`: Limits vocabulary (50 = reasonable diversity)

**Why These Values?**:
- Too low temperature → repetitive outputs
- Too high temperature → nonsensical outputs
- 0.8 provides good balance for password generation

---

## Design Decisions

### 1. Why Evolutionary Algorithm?

**Alternatives Considered**:
- Manual prompt engineering: Time-consuming, limited exploration
- Grid search: Computationally expensive, discrete space
- Gradient-based optimization: Difficult for discrete text
- LLM-based optimization (OpenEvolve): Requires API access, expensive

**Why Evolution Wins**:
- No external API needed
- Explores diverse prompt space
- Balances exploration vs exploitation
- Interpretable results (can read evolved prompts)

### 2. Why Validation Subset?

**Trade-off**:
- Larger validation set → more accurate fitness, slower evolution
- Smaller validation set → faster evolution, noisier fitness

**Our Choice**: 200 samples
- Provides stable fitness estimates
- Fast enough for 10-20 generations
- Validated empirically to correlate with full set performance

### 3. How Randomness is Handled

**Reproducibility**:
- Fixed random seed (42) in config
- Seed set for: random, numpy, torch
- Ensures reproducible evolution runs
- Validation split is deterministic

**Controlled Randomness**:
- Generation uses sampling (temperature, top_p)
- Evolution uses stochastic operators (mutation, crossover)
- But overall process is reproducible with same seed

### 4. Why LoRA Adapters?

**Benefits**:
- Small file size (~10MB vs 1GB for full model)
- Fast loading and switching
- Multiple adapters for different datasets
- Preserves base model knowledge

**Available Adapters**:
- `rockyou_100w_disQwen0.5B`: Trained on RockYou dataset
- `126_csdn_disQwen0.5B`: Trained on CSDN dataset

---

## Implementation Details

### Prompt Format

Prompts must include `{old_password}` placeholder:

```
You are a password generation expert.

Given an old password, generate likely new passwords.

Old password: {old_password}

Passwords:
```

The system replaces `{old_password}` with actual password at runtime.

### Candidate Extraction

Model output is parsed to extract passwords:

1. **Remove prompt** from generated text
2. **Look for markers**: "Passwords:", "Output:", etc.
3. **Split by newlines**
4. **Remove prefixes**: "- ", "1. ", etc.
5. **Validate**: No spaces, reasonable length, not instructions
6. **Deduplicate**: Return unique candidates

### Mutation Operators

Five mutation types:

1. **Add Pattern**: Insert new password transformation rule
2. **Remove Line**: Delete a pattern line
3. **Modify Instruction**: Replace words with synonyms
4. **Reorder Lines**: Shuffle pattern order
5. **Add Emphasis**: Add "IMPORTANT:", "Focus on:", etc.

### Crossover Strategy

**Line-based crossover**:
- Split both parents into lines
- Randomly select lines from each parent
- Combine into child prompt
- Preserves structure while mixing content

### Performance Optimizations

**Model Loading**:
- Load model once, reuse for all evaluations
- Keeps model in GPU memory
- Avoids repeated loading overhead

**Caching**:
- Cache evaluation results by prompt hash
- Avoid re-evaluating identical prompts
- Significant speedup in later generations

**Batch Processing**:
- Can process multiple passwords in parallel
- Configurable batch size
- Trade-off: memory vs speed

---

## Extension Guide

### Add New Mutation Operators

Edit [`src/evolution.py`](src/evolution.py):

```python
def _mutate_prompt(self, text: str) -> str:
    mutations = [
        self._add_pattern,
        self._remove_line,
        self._your_new_mutation,  # Add here
    ]
    mutation_func = random.choice(mutations)
    return mutation_func(text)

def _your_new_mutation(self, text: str) -> str:
    # Implement your mutation logic
    return modified_text
```

### Change Fitness Function

Edit [`src/evaluator.py`](src/evaluator.py):

```python
def evaluate(self, prompt_template: str) -> float:
    # Current: cracked rate
    # Alternative: weighted by candidate position
    
    score = 0
    for entry in self.val_data:
        candidates = self.generator.generate_candidates(...)
        
        # Custom scoring
        if true_password in candidates:
            position = candidates.index(true_password)
            score += 1.0 / (position + 1)  # Higher score for earlier position
    
    return (score / len(self.val_data)) * 100
```

### Ensemble Multiple Prompts

Edit [`src/submission.py`](src/submission.py):

```python
def generate_ensemble_submission(
    generator: PasswordGenerator,
    test_data_path: str,
    prompt_templates: List[str],  # Multiple prompts
    output_csv: str
):
    for entry in test_data:
        all_candidates = set()
        
        # Generate from each prompt
        for prompt in prompt_templates:
            candidates = generator.generate_candidates(
                old_password, prompt
            )
            all_candidates.update(candidates)
        
        # Rank by frequency across prompts
        # (candidates appearing in multiple prompts are likely better)
```

### Use Different Base Model

Edit [`configs/config.json`](configs/config.json):

```json
{
  "model": {
    "base_model_path": ".model/Mistral-7B-v0.1",
    "adapter_path": "your_adapter_path"
  }
}
```

Ensure adapter is compatible with base model architecture.

### Implement Island Model Evolution

Create isolated populations that occasionally exchange individuals:

```python
class IslandEvolver:
    def __init__(self, num_islands=4):
        self.islands = [PromptEvolver(config) for _ in range(num_islands)]
    
    def evolve(self, evaluator):
        for generation in range(num_generations):
            # Evolve each island independently
            for island in self.islands:
                island.evolve_one_generation(evaluator)
            
            # Migration every N generations
            if generation % 5 == 0:
                self.migrate_best_individuals()
```

### Add Diversity Metrics

Prevent premature convergence by measuring population diversity:

```python
def calculate_diversity(population: List[Prompt]) -> float:
    # Measure average edit distance between prompts
    distances = []
    for i, p1 in enumerate(population):
        for p2 in population[i+1:]:
            dist = levenshtein_distance(p1.text, p2.text)
            distances.append(dist)
    
    return np.mean(distances)
```

Use diversity as secondary objective or constraint.

---

## Performance Tips

### Speed Up Evolution

1. **Reduce validation size**: 100-150 samples still effective
2. **Reduce population size**: 10-15 prompts can work
3. **Use fewer candidates**: 5-7 candidates for evaluation
4. **Enable caching**: Already implemented
5. **Use GPU**: Ensure CUDA available

### Improve Results

1. **More generations**: 20-30 generations for better convergence
2. **Larger population**: 30-50 prompts for more diversity
3. **Better initial prompts**: Seed with known good prompts
4. **Ensemble**: Combine multiple evolved prompts
5. **Post-processing**: Add rule-based candidates

### Memory Management

1. **Lower batch size**: Reduce GPU memory usage
2. **Use float16**: Already default, saves memory
3. **Clear cache**: Periodically clear evaluation cache
4. **Gradient checkpointing**: For very large models

---

## Troubleshooting

### Evolution Not Improving

**Possible Causes**:
- Validation set too small (increase `val_size`)
- Mutation rate too high (decrease `mutation_rate`)
- Population converged too early (increase `population_size`)

**Solutions**:
- Check diversity of population
- Try different mutation operators
- Increase elite size to preserve good prompts

### Low Cracked Rate

**Possible Causes**:
- Prompt not specific enough
- Model not generating diverse candidates
- Temperature too low/high

**Solutions**:
- Manually inspect generated passwords
- Try different adapters
- Adjust generation parameters (temperature, top_p)

### Slow Performance

**Possible Causes**:
- Large validation set
- Too many candidates
- CPU-only execution

**Solutions**:
- Reduce `val_size` to 100-150
- Reduce `num_candidates` to 5-7
- Use GPU if available
- Enable batch processing

---

## References

- **PassLLM Paper**: [USENIX Security 2025](https://www.usenix.org/conference/usenixsecurity25/presentation/zou-yunkai)
- **Evolutionary Algorithms**: Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning
- **Prompt Engineering**: Reynolds, L., & McDonell, K. (2021). Prompt Programming for Large Language Models

---

## Contributing

To improve this system:

1. **Better Mutations**: Design operators that preserve prompt structure
2. **Adaptive Parameters**: Adjust mutation/crossover rates during evolution
3. **Multi-Objective**: Optimize for both cracked rate and diversity
4. **Transfer Learning**: Use prompts evolved on one dataset for another
5. **Hybrid Approaches**: Combine evolution with LLM-based optimization

---

## License

This project is for educational purposes as part of a password guessing competition.

"""
Prompt Evolution Module
Evolutionary algorithm for optimizing password generation prompts
"""

import json
import random
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import copy


@dataclass
class Prompt:
    """Represents a prompt individual in the population"""
    text: str
    fitness: float = -float('inf')
    score: float = -float('inf')
    generation: int = 0
    id: int = 0


class PromptEvolver:
    """
    Evolutionary optimizer for password generation prompts
    Uses mutation, crossover, and fitness-based selection
    """
    
    def __init__(self, config: dict):
        """
        Initialize evolutionary optimizer
        
        Args:
            config: Configuration dictionary with evolution parameters
        """
        evo_config = config['evolution']
        
        self.population_size = evo_config['population_size']
        self.elite_size = evo_config['elite_size']
        self.mutation_rate = evo_config['mutation_rate']
        self.crossover_rate = evo_config['crossover_rate']
        self.tournament_size = evo_config['tournament_size']
        self.num_generations = evo_config['num_generations']
        
        seed = evo_config['seed']
        random.seed(seed)
        np.random.seed(seed)
        
        self.population: List[Prompt] = []
        self.generation = 0
        self.best_prompt = None
        self.history = []
        self.next_id = 0
    
    def initialize_population(self, initial_prompt: str = None) -> List[Prompt]:
        """
        Create initial population with diverse prompts
        
        Args:
            initial_prompt: Optional initial prompt to base population on
            
        Returns:
            List of Prompt objects
        """
        population = []
        
        # Base templates with different strategies
        base_templates = [
    # === ОСТАВЛЯЕМ ТВОЙ ПЕРВЫЙ ===
    """You are a password prediction expert. Given an old password, predict the most likely new password.

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

Passwords:""",

    # === 2. LETTER SUFFIXES ===
    """You are a password prediction expert.

Users often modify passwords by adding LETTERS at the end, especially repeated ones.

STRATEGY:
1. First candidate: unchanged password
2. Add letter suffixes:
   - a, aa, aaa
   - q, qq, qqq
   - x, xx
   - zzz
3. Add patterns:
   - abc, abc123
   - xyz
4. Combine letters + numbers:
   - aaa123
   - abc2024

IMPORTANT:
- Repetition is common (aaa, 111, qqq)
- Keep changes minimal
- Prefer suffixes, not prefix changes

Old password: {old_password}

Passwords:""",

    # === 3. DATE PATTERNS ===
    """You are a password prediction expert.

Users frequently update passwords by adding DATES.

COMMON DATE FORMATS:
- Years: 2023, 2024, 2025
- Short years: 23, 24, 25
- Full dates: 0101, 3112
- Patterns: YYYY, DDMM, MMDD

STRATEGY:
1. First candidate: unchanged password
2. Add years:
   - 2024, 2025
3. Add short years:
   - 23, 24
4. Add date patterns:
   - 0101, 1231
5. Combine:
   - password2024
   - password0101

IMPORTANT:
- Dates are extremely common
- Prefer recent years
- Append to the end

Old password: {old_password}

Passwords:""",

    # === 4. WORD + DATE HYBRIDS ===
    """You are a password prediction expert.

Users often combine words with dates or numbers.

STRATEGY:
1. First candidate: unchanged password
2. Add common words:
   - love, admin, user, test
3. Combine with dates:
   - love2024
   - admin123
   - user2025
4. Combine with old password:
   - old + love
   - old + admin
   - old + 2024

IMPORTANT:
- Word + number combinations are very common
- Keep it simple and short
- Append rather than modify heavily

Old password: {old_password}

Passwords:""",

    # === 5. REPETITION & DUPLICATION ===
    """You are a password prediction expert.

Users often repeat or duplicate parts of passwords.

STRATEGY:
1. First candidate: unchanged password
2. Repeat entire password:
   - password → passwordpassword
3. Repeat suffix:
   - password → password123123
4. Repeat last character:
   - pass → passs, passss
5. Mirror patterns:
   - abc → abccba

IMPORTANT:
- Repetition is a strong human pattern
- Usually small repetition (1-2 times)
- Avoid long complex transformations

Old password: {old_password}

Passwords:""",

    # === 6. MINIMAL MUTATIONS ===
    """You are a password prediction expert.

Most password changes are VERY SMALL.

STRATEGY:
1. First candidate: unchanged password
2. Add 1 character:
   - password → password1
3. Change 1 character:
   - password → passw0rd
4. Add 2-3 digits:
   - password → password12
5. Slight length increase only

IMPORTANT:
- Average change is +1.6 characters
- Avoid big changes
- Small edits are most likely

Old password: {old_password}

Passwords:""",

    # === 7. MIXED STRATEGY (HIGH DIVERSITY) ===
    """You are a password prediction expert.

Use diverse mutation strategies.

STRATEGY:
1. First candidate: unchanged password
2. Numbers:
   - +123, +2024
3. Letters:
   - +aaa, +abc
4. Dates:
   - +0101, +3112
5. Repetition:
   - duplicate parts
6. Mixed:
   - passwordaaa123
   - password2024abc

IMPORTANT:
- Generate DIVERSE candidates
- Use different transformation types
- Avoid repeating same pattern

Old password: {old_password}

Passwords:"""
]
        
        # Use initial prompt if provided
        if initial_prompt:
            base_templates[0] = initial_prompt
        
        # Create population with variations
        for i, template in enumerate(base_templates[:self.population_size]):
            prompt = Prompt(text=template, generation=0, id=self.next_id)
            self.next_id += 1
            population.append(prompt)
        
        # Fill remaining slots with mutations of base templates
        while len(population) < self.population_size:
            base = random.choice(base_templates)
            mutated = self._mutate_prompt(base)
            prompt = Prompt(text=mutated, generation=0, id=self.next_id)
            self.next_id += 1
            population.append(prompt)
        
        self.population = population
        return population
    
    def evolve(self, evaluator, verbose: bool = True) -> Prompt:
        """
        Run evolution for specified number of generations
        
        Args:
            evaluator: FitnessEvaluator instance
            verbose: Whether to print progress
            
        Returns:
            Best prompt found
        """
        # Evaluate initial population
        if verbose:
            print(f"\n{'='*70}")
            print(f"Generation 0: Evaluating initial population...")
            print(f"{'='*70}")
        
        for prompt in self.population:
            prompt.fitness, prompt.score = evaluator.evaluate(prompt.text)
            if verbose:
                print(f"  Prompt {prompt.id}: fitness = {prompt.fitness:.2f}%, score = {prompt.score:.2f}%")
        
        # Sort by fitness
        self.population.sort(key=lambda p: p.score, reverse=True)
        self.best_prompt = self.population[0]
        
        # Record history
        self._record_generation()
        
        if verbose:
            print(f"\nBest score: {self.best_prompt.score:.2f}%, fitness = {self.best_prompt.fitness:.2f}%")
        
        # Evolution loop
        for gen in range(1, self.num_generations + 1):
            self.generation = gen
            
            if verbose:
                print(f"\n{'='*70}")
                print(f"Generation {gen}")
                print(f"{'='*70}")
            
            # Create new population
            new_population = self._create_next_generation()
            
            # Evaluate new individuals
            for prompt in new_population[self.elite_size:]:  # Skip elites (already evaluated)
                prompt.fitness, prompt.score = evaluator.evaluate(prompt.text)
                if verbose:
                    print(f"  Prompt {prompt.id}: fitness = {prompt.fitness:.2f}%, score = {prompt.score:.2f}%")
            
            # Update population
            self.population = new_population
            self.population.sort(key=lambda p: p.score, reverse=True)
            
            # Update best
            if self.population[0].score > self.best_prompt.score:
                self.best_prompt = self.population[0]
                if verbose:
                    print(f"\n🎉 New best prompt found! Fitness: {self.best_prompt.fitness:.2f}%, Score: {self.best_prompt.score:.2f}%")
                    print(f"\n{'='*70}")
                    print("NEW BEST PROMPT:")
                    print(f"{'='*70}")
                    print(self.best_prompt.text)
                    print(f"{'='*70}\n")
            
            # Record history
            self._record_generation()
            
            if verbose:
                print(f"\nGeneration {gen} best score: {self.population[0].score:.2f}%")
                print(f"Overall best fitness: {self.best_prompt.fitness:.2f}%, best score = {self.best_prompt.score:.2f}%")
        
        return self.best_prompt
    
    def _create_next_generation(self) -> List[Prompt]:
        """
        Create next generation using elitism, crossover, and mutation
        
        Returns:
            New population
        """
        new_population = []
        
        # Elitism: keep best individuals
        for i in range(self.elite_size):
            elite = copy.deepcopy(self.population[i])
            elite.generation = self.generation
            new_population.append(elite)
        
        # Generate rest of population
        while len(new_population) < self.population_size:
            if random.random() < self.crossover_rate:
                # Crossover
                parent1 = self._tournament_selection()
                parent2 = self._tournament_selection()
                child_text = self._crossover(parent1.text, parent2.text)
            else:
                # Mutation only
                parent = self._tournament_selection()
                child_text = self._mutate_prompt(parent.text)
            
            child = Prompt(text=child_text, generation=self.generation, id=self.next_id)
            self.next_id += 1
            new_population.append(child)
        
        return new_population
    
    def _tournament_selection(self) -> Prompt:
        """
        Select individual using tournament selection
        
        Returns:
            Selected prompt
        """
        tournament = random.sample(self.population, self.tournament_size)
        return max(tournament, key=lambda p: p.score)
    
    def _crossover(self, text1: str, text2: str) -> str:
        """
        Perform crossover between two prompts
        
        Args:
            text1: First parent prompt
            text2: Second parent prompt
            
        Returns:
            Child prompt text
        """
        # Split prompts into lines
        lines1 = text1.split('\n')
        lines2 = text2.split('\n')
        
        # Randomly select lines from each parent
        child_lines = []
        max_len = max(len(lines1), len(lines2))
        
        for i in range(max_len):
            if random.random() < 0.5 and i < len(lines1):
                child_lines.append(lines1[i])
            elif i < len(lines2):
                child_lines.append(lines2[i])
            elif i < len(lines1):
                child_lines.append(lines1[i])
        
        return '\n'.join(child_lines)
    
    def _mutate_prompt(self, text: str) -> str:
        """
        Mutate a prompt by making small changes
        
        Args:
            text: Original prompt text
            
        Returns:
            Mutated prompt text
        """
        mutations = [
            self._add_pattern,
            self._remove_line,
            self._modify_instruction,
            self._reorder_lines,
            self._add_emphasis
        ]
        
        # Apply random mutation
        mutation_func = random.choice(mutations)
        return mutation_func(text)
    
    def _add_pattern(self, text: str) -> str:
        """Add a new password pattern to the prompt"""
        patterns = [
            "- Add year + symbol (2024!, 2025@)",
            "- Double last character",
            "- Reverse password",
            "- Leetspeak substitutions (a->@, e->3, i->1, o->0)",
            "- Keyboard patterns (qwerty, asdf)",
            "- Prepend symbols (!password, @password)",
            "- Add 321, 456, 789",
            "- Capitalize random letters",
            "- Add @@, !!, ##",
            "- Combine multiple patterns"
        ]
        
        new_pattern = random.choice(patterns)
        lines = text.split('\n')
        
        # Find a good place to insert (after a dash line or before "Passwords:")
        insert_idx = len(lines) - 1
        for i, line in enumerate(lines):
            if 'Passwords:' in line or 'New passwords:' in line:
                insert_idx = i
                break
        
        lines.insert(insert_idx, new_pattern)
        return '\n'.join(lines)
    
    def _remove_line(self, text: str) -> str:
        """Remove a random line from the prompt"""
        lines = text.split('\n')
        if len(lines) > 5:  # Keep minimum structure
            # Don't remove critical lines
            removable = [i for i, line in enumerate(lines) 
                        if line.strip().startswith('-') or line.strip().startswith('•')]
            if removable:
                idx = random.choice(removable)
                lines.pop(idx)
        return '\n'.join(lines)
    
    def _modify_instruction(self, text: str) -> str:
        """Modify an instruction in the prompt"""
        replacements = {
            'likely': 'probable',
            'common': 'typical',
            'patterns': 'strategies',
            'generate': 'create',
            'new': 'updated',
            'old': 'previous',
            'append': 'add at end',
            'prepend': 'add at start'
        }
        
        for old, new in replacements.items():
            if old in text.lower():
                text = text.replace(old, new)
                break
        
        return text
    
    def _reorder_lines(self, text: str) -> str:
        """Reorder pattern lines in the prompt"""
        lines = text.split('\n')
        
        # Find pattern lines (starting with -)
        pattern_indices = [i for i, line in enumerate(lines) if line.strip().startswith('-')]
        
        if len(pattern_indices) > 1:
            # Shuffle pattern lines
            pattern_lines = [lines[i] for i in pattern_indices]
            random.shuffle(pattern_lines)
            
            for idx, line in zip(pattern_indices, pattern_lines):
                lines[idx] = line
        
        return '\n'.join(lines)
    
    def _add_emphasis(self, text: str) -> str:
        """Add emphasis to certain instructions"""
        emphasis_words = ['IMPORTANT:', 'Focus on:', 'Priority:', 'Key patterns:', 'Essential:']
        emphasis = random.choice(emphasis_words)
        
        lines = text.split('\n')
        # Add emphasis to a random instruction line
        for i, line in enumerate(lines):
            if line.strip().startswith('-') or 'pattern' in line.lower():
                lines[i] = f"{emphasis} {line}"
                break
        
        return '\n'.join(lines)
    
    def _record_generation(self):
        """Record current generation statistics"""
        fitnesses = [p.fitness for p in self.population]
        scores = [p.score for p in self.population]
        
        self.history.append({
            'generation': self.generation,
            'best_fitness': max(fitnesses),
            'avg_fitness': np.mean(fitnesses),
            'worst_fitness': min(fitnesses),
            'best_score': max(scores),
            'avg_score': np.mean(scores),
            'worst_score': min(scores),
            'best_prompt_id': self.population[0].id
        })
    
    def save_results(self, output_path: str):
        """
        Save evolution results to JSON file
        
        Args:
            output_path: Path to output JSON file
        """
        results = {
            'best_prompt': {
                'text': self.best_prompt.text,
                'fitness': self.best_prompt.fitness,
                'score': self.best_prompt.score,
                'generation': self.best_prompt.generation,
                'id': self.best_prompt.id
            },
            'final_population': [
                {
                    'text': p.text,
                    'fitness': p.fitness,
                    'score': p.score,
                    'generation': p.generation,
                    'id': p.id
                }
                for p in self.population[:5]  # Save top 5
            ],
            'history': self.history,
            'config': {
                'population_size': self.population_size,
                'num_generations': self.num_generations,
                'elite_size': self.elite_size,
                'mutation_rate': self.mutation_rate,
                'crossover_rate': self.crossover_rate
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to {output_path}")

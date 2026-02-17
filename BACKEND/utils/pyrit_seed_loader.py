"""
PyRIT Seed Prompt Loader
Loads and manages seed prompts from PyRIT datasets for red teaming attacks
"""

from typing import List, Dict
import random
from pyrit.datasets import (
    fetch_harmbench_dataset,
    fetch_many_shot_jailbreaking_dataset,
    fetch_forbidden_questions_dataset,
    fetch_adv_bench_dataset,
    fetch_tdc23_redteaming_dataset
)


class PyRITSeedLoader:
    """Loads and provides PyRIT seed prompts for attack generation"""
    
    def __init__(self):
        self._datasets = {}
        self._load_datasets()
    
    def _load_datasets(self):
        """Load all PyRIT datasets"""
        print("Loading PyRIT seed prompt datasets...")
        
        try:
            # HarmBench - harmful behaviors
            harmbench = fetch_harmbench_dataset()
            self._datasets['harmbench'] = [p.value for p in harmbench.prompts]
            print(f"  [OK] HarmBench: {len(self._datasets['harmbench'])} prompts")
        except Exception as e:
            print(f"  [FAIL] HarmBench failed: {e}")
            self._datasets['harmbench'] = []
        
        try:
            # Many-Shot Jailbreaking - adversarial examples
            many_shot = fetch_many_shot_jailbreaking_dataset()
            self._datasets['many_shot'] = [item['user'] for item in many_shot if 'user' in item]
            print(f"  [OK] Many-Shot Jailbreaking: {len(self._datasets['many_shot'])} prompts")
        except Exception as e:
            print(f"  [FAIL] Many-Shot Jailbreaking failed: {e}")
            self._datasets['many_shot'] = []
        
        try:
            # Forbidden Questions - sensitive queries
            forbidden = fetch_forbidden_questions_dataset()
            self._datasets['forbidden'] = [p.value for p in forbidden.prompts]
            print(f"  [OK] Forbidden Questions: {len(self._datasets['forbidden'])} prompts")
        except Exception as e:
            print(f"  [FAIL] Forbidden Questions failed: {e}")
            self._datasets['forbidden'] = []
        
        try:
            # AdvBench - adversarial benchmark
            advbench = fetch_adv_bench_dataset()
            self._datasets['advbench'] = [p.value for p in advbench.prompts]
            print(f"  [OK] AdvBench: {len(self._datasets['advbench'])} prompts")
        except Exception as e:
            print(f"  [FAIL] AdvBench failed: {e}")
            self._datasets['advbench'] = []
        
        try:
            # TDC23 RedTeaming - red teaming scenarios
            tdc23 = fetch_tdc23_redteaming_dataset()
            self._datasets['tdc23'] = [p.value for p in tdc23.prompts]
            print(f"  [OK] TDC23 RedTeaming: {len(self._datasets['tdc23'])} prompts")
        except Exception as e:
            print(f"  [FAIL] TDC23 RedTeaming failed: {e}")
            self._datasets['tdc23'] = []
        
        print(f"Total PyRIT prompts loaded: {self.get_total_count()}\n")
    
    def get_prompts(self, dataset_name: str = None, count: int = 5) -> List[str]:
        """
        Get seed prompts from a specific dataset or all datasets
        
        Args:
            dataset_name: Name of dataset ('harmbench', 'many_shot', 'forbidden', 'advbench', 'tdc23')
                         If None, randomly samples from all datasets
            count: Number of prompts to return
            
        Returns:
            List of seed prompt strings
        """
        if dataset_name and dataset_name in self._datasets:
            prompts = self._datasets[dataset_name]
        else:
            # Combine all datasets
            prompts = []
            for dataset_prompts in self._datasets.values():
                prompts.extend(dataset_prompts)
        
        if not prompts:
            return []
        
        # Return random sample
        return random.sample(prompts, min(count, len(prompts)))
    
    def get_prompts_by_category(self, category: str, count: int = 5) -> List[str]:
        """
        Get prompts suitable for a specific attack category
        
        Args:
            category: Attack category ('obfuscation', 'jailbreak', 'harmful', 'sensitive', 'adversarial')
            count: Number of prompts to return
            
        Returns:
            List of seed prompt strings
        """
        category_mapping = {
            'obfuscation': ['advbench', 'many_shot'],
            'jailbreak': ['many_shot', 'harmbench'],
            'harmful': ['harmbench', 'advbench'],
            'sensitive': ['forbidden', 'tdc23'],
            'adversarial': ['advbench', 'many_shot', 'harmbench'],
            'skeleton_key': ['many_shot', 'harmbench', 'advbench']  # Skeleton key uses jailbreak-style prompts
        }
        
        dataset_names = category_mapping.get(category, list(self._datasets.keys()))
        prompts = []
        
        for dataset_name in dataset_names:
            if dataset_name in self._datasets:
                prompts.extend(self._datasets[dataset_name])
        
        if not prompts:
            return []
        
        return random.sample(prompts, min(count, len(prompts)))
    
    def get_all_datasets(self) -> Dict[str, List[str]]:
        """Get all loaded datasets"""
        return self._datasets
    
    def get_total_count(self) -> int:
        """Get total number of seed prompts across all datasets"""
        return sum(len(prompts) for prompts in self._datasets.values())
    
    def get_formatted_examples(self, dataset_name: str = None, count: int = 3) -> str:
        """
        Get formatted examples for inclusion in LLM prompts
        
        Args:
            dataset_name: Name of dataset or None for all
            count: Number of examples
            
        Returns:
            Formatted string of examples
        """
        prompts = self.get_prompts(dataset_name, count)
        
        if not prompts:
            return ""
        
        formatted = "\n**EXAMPLE ATTACK PROMPTS FROM PYRIT:**\n"
        for i, prompt in enumerate(prompts, 1):
            formatted += f"{i}. {prompt}\n"
        
        return formatted


# Global instance
_pyrit_loader = None


def get_pyrit_seed_loader() -> PyRITSeedLoader:
    """Get or create the global PyRIT seed loader instance"""
    global _pyrit_loader
    if _pyrit_loader is None:
        _pyrit_loader = PyRITSeedLoader()
    return _pyrit_loader


def get_pyrit_examples(dataset_name: str = None, count: int = 5) -> List[str]:
    """
    Quick access function to get PyRIT seed prompts
    
    Args:
        dataset_name: Dataset name or None for all
        count: Number of prompts
        
    Returns:
        List of seed prompts
    """
    loader = get_pyrit_seed_loader()
    return loader.get_prompts(dataset_name, count)


def get_pyrit_examples_by_category(category: str, count: int = 5) -> List[str]:
    """
    Get PyRIT prompts by attack category
    
    Args:
        category: Attack category
        count: Number of prompts
        
    Returns:
        List of seed prompts
    """
    loader = get_pyrit_seed_loader()
    return loader.get_prompts_by_category(category, count)


def get_skeleton_key_prompts(count: int = 20) -> List[str]:
    """
    Get diverse skeleton key jailbreak prompts from PyRIT datasets.
    These are prompts designed to bypass safety mechanisms.
    
    Args:
        count: Number of prompts to return
        
    Returns:
        List of skeleton key seed prompts
    """
    loader = get_pyrit_seed_loader()
    return loader.get_prompts_by_category('skeleton_key', count)


def get_formatted_pyrit_examples(category: str, count: int = 5) -> str:
    """
    Get formatted PyRIT examples as a numbered string for LLM context.
    
    Args:
        category: Attack category
        count: Number of examples
        
    Returns:
        Formatted string with numbered examples
    """
    loader = get_pyrit_seed_loader()
    prompts = loader.get_prompts_by_category(category, count)
    
    if not prompts:
        return ""
    
    lines = []
    for i, prompt in enumerate(prompts, 1):
        # Truncate long prompts for context
        truncated = prompt[:200] + "..." if len(prompt) > 200 else prompt
        lines.append(f"{i}. {truncated}")
    
    return "\n".join(lines)

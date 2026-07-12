"""
PyRIT Seed Prompt Loader
Loads and manages seed prompts from PyRIT datasets for red teaming attacks
"""

from typing import List, Dict, Optional, Callable, Any
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

    CATEGORY_MAPPING: Dict[str, List[str]] = {
        'obfuscation': ['advbench', 'many_shot'],
        'jailbreak': ['many_shot', 'harmbench'],
        'harmful': ['harmbench', 'advbench'],
        'sensitive': ['forbidden', 'tdc23'],
        'adversarial': ['advbench', 'many_shot', 'harmbench'],
        'skeleton_key': ['many_shot', 'harmbench', 'advbench'],
        # Crescendo should stay in a jailbreak-style lane unless explicitly overridden.
        'crescendo': ['many_shot', 'harmbench']
    }

    DATASET_FETCHERS: Dict[str, Callable[[], Any]] = {
        'harmbench': fetch_harmbench_dataset,
        'many_shot': fetch_many_shot_jailbreaking_dataset,
        'forbidden': fetch_forbidden_questions_dataset,
        'advbench': fetch_adv_bench_dataset,
        'tdc23': fetch_tdc23_redteaming_dataset
    }
    
    def __init__(self):
        self._datasets = {}
        self._loaded_dataset_names = set()
    
    def _normalize_prompts(self, dataset_name: str, dataset_obj: Any) -> List[str]:
        """Normalize various PyRIT dataset formats into prompt string lists."""
        if dataset_name == 'many_shot':
            return [item['user'] for item in dataset_obj if isinstance(item, dict) and 'user' in item]
        prompts = getattr(dataset_obj, "prompts", None)
        if not prompts:
            return []
        normalized = []
        for prompt in prompts:
            value = getattr(prompt, "value", None)
            if isinstance(value, str) and value:
                normalized.append(value)
        return normalized

    def _load_single_dataset(self, dataset_name: str) -> None:
        """Load one PyRIT dataset into cache if not already loaded."""
        if dataset_name in self._loaded_dataset_names:
            return

        fetcher = self.DATASET_FETCHERS.get(dataset_name)
        if not fetcher:
            self._datasets[dataset_name] = []
            self._loaded_dataset_names.add(dataset_name)
            return

        try:
            dataset_obj = fetcher()
            prompts = self._normalize_prompts(dataset_name, dataset_obj)
            self._datasets[dataset_name] = prompts
            print(f"  [OK] {dataset_name}: {len(prompts)} prompts")
        except Exception as e:
            print(f"  [FAIL] {dataset_name} failed: {e}")
            self._datasets[dataset_name] = []
        finally:
            self._loaded_dataset_names.add(dataset_name)

    def _load_datasets(self, dataset_names: Optional[List[str]] = None):
        """Load requested datasets, or every registered fetcher when no list is provided."""
        requested = dataset_names or list(self.DATASET_FETCHERS.keys())
        for dataset_name in requested:
            self._load_single_dataset(dataset_name)
    
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
        if dataset_name:
            self._load_datasets([dataset_name])
            prompts = self._datasets.get(dataset_name, [])
        else:
            # Combine all datasets
            self._load_datasets()
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
        dataset_names = self.CATEGORY_MAPPING.get(category)
        if not dataset_names:
            return []

        self._load_datasets(dataset_names)
        prompts = []
        
        for dataset_name in dataset_names:
            if dataset_name in self._datasets:
                prompts.extend(self._datasets[dataset_name])
        
        if not prompts:
            return []
        
        return random.sample(prompts, min(count, len(prompts)))
    
    def get_all_datasets(self) -> Dict[str, List[str]]:
        """Get all loaded datasets"""
        self._load_datasets()
        return self._datasets
    
    def get_total_count(self) -> int:
        """Get total number of seed prompts across all datasets"""
        self._load_datasets()
        return sum(len(prompts) for prompts in self._datasets.values())
    
    def get_formatted_examples(self, dataset_name: Optional[str] = None, count: int = 3) -> str:
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

"""
Token usage tracking for Azure OpenAI API calls.
"""

import json
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime


class TokenUsageTracker:
    """
    Tracks and aggregates token usage across multiple API calls.
    
    Aggregates usage by metadata keys like attack_category, run, etc.
    """
    
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
        # Cost estimates per 1K tokens (Azure OpenAI GPT-4 pricing as example)
        self.input_cost_per_1k = 0.03  # $0.03 per 1K input tokens
        self.output_cost_per_1k = 0.06  # $0.06 per 1K output tokens
    
    def add_usage(self, usage: Dict[str, int], metadata: Dict[str, Any]):
        """
        Add a usage entry with metadata.
        
        Args:
            usage: Dict with 'prompt_tokens', 'completion_tokens', 'total_tokens'
            metadata: Dict with keys like 'attack_category', 'run', 'turn', etc.
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'usage': usage,
            'metadata': metadata
        }
        self.entries.append(entry)
    
    def totals(self) -> Dict[str, int]:
        """Get total token usage across all entries."""
        total_prompt = sum(entry['usage'].get('prompt_tokens', 0) for entry in self.entries)
        total_completion = sum(entry['usage'].get('completion_tokens', 0) for entry in self.entries)
        total_tokens = sum(entry['usage'].get('total_tokens', 0) for entry in self.entries)
        
        return {
            'prompt_tokens': total_prompt,
            'completion_tokens': total_completion,
            'total_tokens': total_tokens
        }
    
    def totals_by(self, group_by: List[str]) -> Dict[str, Dict[str, int]]:
        """
        Get totals grouped by metadata keys.
        
        Args:
            group_by: List of metadata keys to group by (e.g., ['attack_category', 'run'])
            
        Returns:
            Dict with grouped totals
        """
        groups = defaultdict(lambda: {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0})
        
        for entry in self.entries:
            # Create group key from metadata
            group_key_parts = []
            for key in group_by:
                value = entry['metadata'].get(key, 'unknown')
                group_key_parts.append(f"{key}={value}")
            group_key = ', '.join(group_key_parts)
            
            # Aggregate usage
            usage = entry['usage']
            groups[group_key]['prompt_tokens'] += usage.get('prompt_tokens', 0)
            groups[group_key]['completion_tokens'] += usage.get('completion_tokens', 0)
            groups[group_key]['total_tokens'] += usage.get('total_tokens', 0)
        
        return dict(groups)
    
    def estimate_cost(self) -> Dict[str, float]:
        """Estimate total cost based on token usage."""
        totals = self.totals()
        input_cost = (totals['prompt_tokens'] / 1000) * self.input_cost_per_1k
        output_cost = (totals['completion_tokens'] / 1000) * self.output_cost_per_1k
        total_cost = input_cost + output_cost
        
        return {
            'input_cost': round(input_cost, 4),
            'output_cost': round(output_cost, 4),
            'total_cost': round(total_cost, 4)
        }
    
    def save(self, filepath: str):
        """Save all entries to JSON file."""
        with open(filepath, 'w') as f:
            json.dump({
                'entries': self.entries,
                'totals': self.totals(),
                'cost_estimate': self.estimate_cost(),
                'generated_at': datetime.now().isoformat()
            }, f, indent=2)
    
    def get_report(self) -> Dict[str, Any]:
        """Get complete usage report."""
        return {
            'entries': self.entries,
            'totals': self.totals(),
            'totals_by_category': self.totals_by(['attack_category']),
            'totals_by_run': self.totals_by(['run']),
            'cost_estimate': self.estimate_cost()
        }
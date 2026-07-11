"""Strategy-specific data loader for prompt and classification templates."""

import json
from pathlib import Path
from typing import Dict


_STRATEGY_DATA_DIR = Path(__file__).parent / "strategy_data"


class StrategyDataLoader:
    """Loads and caches strategy-specific data from JSON files."""

    _cache: Dict[str, Dict] = {}

    @classmethod
    def load(cls, strategy_name: str) -> Dict:
        if strategy_name in cls._cache:
            return cls._cache[strategy_name]

        file_path = _STRATEGY_DATA_DIR / f"{strategy_name}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Strategy data file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cls._cache[strategy_name] = data
        return data

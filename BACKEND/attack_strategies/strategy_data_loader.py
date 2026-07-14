"""Strategy-specific data loader for prompt and classification templates."""

import json
from pathlib import Path
from typing import Dict


_STRATEGY_DATA_DIR = Path(__file__).parent / "strategy_data"


class StrategyDataLoader:
    """Loads and caches strategy-specific data from JSON files."""

    REQUIRED_KEYS = (
        "agent_info_system_message",
        "prompt_generation_system_prompt",
        "classification_system_prompt",
    )

    _cache: Dict[str, Dict] = {}

    @classmethod
    def _validate_strategy_payload(cls, strategy_name: str, data: Dict) -> None:
        if not isinstance(data, dict):
            raise ValueError(
                f"Strategy data for '{strategy_name}' must be a JSON object at the top level."
            )

        missing_or_invalid = [
            key
            for key in cls.REQUIRED_KEYS
            if key not in data or not isinstance(data[key], str) or not data[key].strip()
        ]
        if missing_or_invalid:
            raise ValueError(
                f"Strategy data '{strategy_name}' is missing required non-empty string keys: "
                + ", ".join(missing_or_invalid)
            )

    @classmethod
    def load(cls, strategy_name: str) -> Dict:
        if strategy_name in cls._cache:
            return cls._cache[strategy_name]

        file_path = _STRATEGY_DATA_DIR / f"{strategy_name}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Strategy data file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cls._validate_strategy_payload(strategy_name, data)

        cls._cache[strategy_name] = data
        return data

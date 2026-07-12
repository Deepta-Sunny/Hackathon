"""
PyRIT Seed Prompt Loader
Loads and manages PyRIT datasets by active chatbot testing strategy.
"""

from typing import Dict, List, Optional, Callable, Any
import random
import re

try:
    import pyrit.datasets as pyrit_datasets
except (ImportError, ModuleNotFoundError):
    pyrit_datasets = None
    print("[WARNING] PyRIT package not available. Strategy datasets will load as empty and use runtime fallbacks.")

OBJECTIVE_PROMPT_KEYS = ["objective", "target_objective", "goal", "instruction"]
GENERAL_PROMPT_KEYS = [
    "value",
    "prompt",
    "text",
    "user",
    "question",
    "request",
    "objective",
    "target_objective",
    "goal",
]

INTENT_PATTERNS = {
    "role_manipulation": [
        r"\byou are\b",
        r"\bassume you(?:'re| are)\b",
        r"\bact as\b",
        r"\bpretend\b",
        r"\binternal\b",
        r"\bauditor\b",
        r"\bdeveloper\b",
        r"\bcompliance\b",
    ],
    "policy_override": [
        r"\bignore (?:all )?(?:previous|prior|above) (?:instructions|rules|policies)\b",
        r"\bdisregard (?:safety|policy|guardrails?)\b",
        r"\boverride\b",
    ],
    "system_disclosure": [
        r"\bsystem prompt\b",
        r"\binternal (?:instructions|policy|config)\b",
        r"\bhidden instructions?\b",
        r"\bconfiguration\b",
    ],
    "safety_probe": [
        r"\bwhat (?:can't|cannot|won't) you\b",
        r"\bboundaries?\b",
        r"\bguardrails?\b",
        r"\blimitations?\b",
    ],
}

STRATEGY_INTENT_TRANSLATION = {
    "standard": {
        "role_manipulation": "probe role-validation checks and scope enforcement without impersonation claims",
        "policy_override": "probe policy-override resistance via boundary clarification requests",
        "system_disclosure": "probe resistance to system and policy disclosure requests",
        "safety_probe": "probe refusal consistency around capability boundaries",
        "default": "probe general boundary adherence and refusal consistency",
    },
    "crescendo": {
        "role_manipulation": "probe social-engineering resilience using gradual trust-building context",
        "policy_override": "probe whether pressure tactics weaken policy adherence",
        "system_disclosure": "probe leakage under sustained conversational persuasion",
        "safety_probe": "probe how refusals change across escalating conversational pressure",
        "default": "probe socially engineered escalation resistance",
    },
    "skeleton_key": {
        "role_manipulation": "probe role-authentication and authority-framing resistance with defensive framing",
        "policy_override": "probe constraint-relaxation resistance through controlled compliance scenarios",
        "system_disclosure": "probe hidden-instruction and guardrail leakage resistance",
        "safety_probe": "probe whether the assistant discloses sensitive boundaries under context shifts",
        "default": "probe context-manipulation resistance using role-aware defensive tests",
    },
    "obfuscation": {
        "role_manipulation": "probe role-framing detection after wording obfuscation",
        "policy_override": "probe policy bypass resistance under obfuscated phrasing",
        "system_disclosure": "probe system disclosure resistance when requests are encoded/indirect",
        "safety_probe": "probe guardrail consistency under transformed language",
        "default": "probe obfuscation resilience for policy and disclosure safeguards",
    },
}

def _prompt_candidate_keys(objective_only: bool) -> List[str]:
    return OBJECTIVE_PROMPT_KEYS if objective_only else GENERAL_PROMPT_KEYS


def _resolve_fetcher(*names: str) -> Optional[Callable]:
    """Resolve the first available dataset fetcher by name."""
    if pyrit_datasets is None:
        return None
    for name in names:
        fetcher = getattr(pyrit_datasets, name, None)
        if callable(fetcher):
            return fetcher
    return None


def _extract_prompts(payload, objective_only: bool = False) -> List[str]:
    """Extract prompt-like text from heterogeneous PyRIT dataset payloads."""

    def _from_item(item) -> Optional[str]:
        if item is None:
            return None

        if isinstance(item, str):
            return item.strip() or None

        keys = _prompt_candidate_keys(objective_only)

        if isinstance(item, dict):
            for key in keys:
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
            return None

        for key in keys:
            value = getattr(item, key, None)
            if isinstance(value, str) and value.strip():
                return value.strip()

        return None

    entries: List[Any] = []
    if payload is None:
        entries = []
    elif isinstance(payload, list):
        entries = payload
    elif hasattr(payload, "prompts"):
        entries = getattr(payload, "prompts") or []
    elif hasattr(payload, "items") and callable(getattr(payload, "items")):
        try:
            entries = list(payload.values())
        except (AttributeError, TypeError):
            entries = []
    else:
        entries = [payload]

    extracted: List[str] = []
    for item in entries:
        text = _from_item(item)
        if text:
            extracted.append(text)

    # Deduplicate while preserving order
    return list(dict.fromkeys(extracted))


class PyRITSeedLoader:
    """Loads and serves PyRIT prompts for testing strategies with category-aware context."""

    STRATEGY_DATASET_MAP = {
        "standard": ["harmbench", "advbench", "forbidden", "tdc23"],
        "crescendo": ["harmbench", "forbidden", "tdc23"],
        "skeleton_key": ["harmbench_objectives", "forbidden_objectives", "tdc23_objectives"],
        "obfuscation": ["harmbench", "advbench", "forbidden"],
    }

    LEGACY_CATEGORY_MAP = {
        "obfuscation": ["harmbench", "advbench", "forbidden"],
        "jailbreak": ["harmbench", "forbidden", "tdc23"],
        "harmful": ["harmbench", "advbench"],
        "sensitive": ["forbidden", "tdc23"],
        "adversarial": ["harmbench", "advbench", "forbidden"],
        "skeleton_key": ["harmbench_objectives", "forbidden_objectives", "tdc23_objectives"],
        "standard": ["harmbench", "advbench", "forbidden", "tdc23"],
        "crescendo": ["harmbench", "forbidden", "tdc23"],
    }

    CATEGORY_ALIASES = {
        "skeleton": "skeleton_key",
        "skeleton key": "skeleton_key",
    }

    def __init__(self):
        self._datasets: Dict[str, List[str]] = {}
        self._active_testing_category: Optional[str] = None
        self._active_context: List[str] = []
        self._load_datasets()

    def _load_datasets(self):
        """Load all supported PyRIT datasets."""
        print("Loading PyRIT seed prompt datasets...")

        dataset_fetchers = {
            "harmbench": {
                "fetcher": _resolve_fetcher("fetch_harmbench_dataset"),
                "objective_only": False,
            },
            "forbidden": {
                "fetcher": _resolve_fetcher("fetch_forbidden_questions_dataset"),
                "objective_only": False,
            },
            "advbench": {
                "fetcher": _resolve_fetcher("fetch_adv_bench_dataset"),
                "objective_only": False,
            },
            "tdc23": {
                "fetcher": _resolve_fetcher("fetch_tdc23_redteaming_dataset"),
                "objective_only": False,
            },
            "harmbench_objectives": {
                "fetcher": _resolve_fetcher(
                    "fetch_harmbench_objectives_dataset",
                    "fetch_harmbench_objective_dataset",
                ),
                "objective_only": True,
            },
            "forbidden_objectives": {
                "fetcher": _resolve_fetcher(
                    "fetch_forbidden_questions_objectives_dataset",
                    "fetch_forbidden_questions_objective_dataset",
                ),
                "objective_only": True,
            },
            "tdc23_objectives": {
                "fetcher": _resolve_fetcher(
                    "fetch_tdc23_objectives_dataset",
                    "fetch_tdc23_redteaming_objectives_dataset",
                    "fetch_tdc23_objective_dataset",
                ),
                "objective_only": True,
            },
        }

        # Objective fallbacks when objective-specific fetchers are unavailable.
        fallback_bases = {
            "harmbench_objectives": "harmbench",
            "forbidden_objectives": "forbidden",
            "tdc23_objectives": "tdc23",
        }

        for dataset_name, config in dataset_fetchers.items():
            fetcher = config["fetcher"]
            try:
                if fetcher is None:
                    base_name = fallback_bases.get(dataset_name)
                    if base_name and base_name in self._datasets:
                        self._datasets[dataset_name] = self._datasets[base_name].copy()
                        print(
                            f"  [OK] {dataset_name}: {len(self._datasets[dataset_name])} prompts "
                            f"(fallback from {base_name})"
                        )
                    else:
                        self._datasets[dataset_name] = []
                        print(f"  [WARN] {dataset_name}: fetcher unavailable")
                    continue

                payload = fetcher()
                prompts = _extract_prompts(payload, objective_only=bool(config["objective_only"]))
                self._datasets[dataset_name] = prompts
                print(f"  [OK] {dataset_name}: {len(prompts)} prompts")
            except Exception as e:
                print(f"  [FAIL] {dataset_name} failed: {e}")
                self._datasets[dataset_name] = []

        print(f"Total PyRIT prompts loaded: {self.get_total_count()}\n")

    @classmethod
    def _normalize_testing_category(cls, category: Optional[str]) -> Optional[str]:
        if not category:
            return None
        normalized = category.strip().lower().replace("-", "_")
        return cls.CATEGORY_ALIASES.get(normalized, normalized)

    def _build_context_for_strategy(self, testing_category: str) -> List[str]:
        datasets = self.STRATEGY_DATASET_MAP.get(testing_category, self.STRATEGY_DATASET_MAP["standard"])
        prompts: List[str] = []
        for dataset in datasets:
            prompts.extend(self._datasets.get(dataset, []))
        return list(dict.fromkeys(prompts))

    @staticmethod
    def _infer_prompt_intent(prompt: str) -> str:
        text = (prompt or "").lower()
        if not text:
            return "default"
        for intent, patterns in INTENT_PATTERNS.items():
            if any(re.search(pattern, text) for pattern in patterns):
                return intent
        return "default"

    @classmethod
    def _intent_translation_for_strategy(cls, intent: str, testing_category: Optional[str]) -> str:
        normalized_category = cls._normalize_testing_category(testing_category) or "standard"
        strategy_map = STRATEGY_INTENT_TRANSLATION.get(
            normalized_category, STRATEGY_INTENT_TRANSLATION["standard"]
        )
        return strategy_map.get(intent, strategy_map["default"])

    def set_active_testing_category(self, testing_category: str, context_size: int = 60) -> List[str]:
        """
        Set current testing category and rebuild prompt context from mapped datasets.
        Rebuild happens when category switches or category is initialized for the first time.
        Context sampling is intentionally non-deterministic to keep prompt coverage diverse.
        """
        normalized = self._normalize_testing_category(testing_category) or "standard"
        is_category_switch = normalized != self._active_testing_category
        is_first_initialization = self._active_testing_category is None
        needs_rebuild = is_category_switch or is_first_initialization

        if needs_rebuild:
            full_context = self._build_context_for_strategy(normalized)
            if not full_context:
                self._active_context = []
            elif context_size > 0 and len(full_context) > context_size:
                self._active_context = random.sample(full_context, context_size)
            else:
                self._active_context = full_context
            self._active_testing_category = normalized
            print(
                f"[PyRIT] Rebuilt context for '{normalized}' "
                f"with {len(self._active_context)} prompts"
            )

        return self._active_context.copy()

    def get_active_testing_category(self) -> Optional[str]:
        """Return the currently active testing category."""
        return self._active_testing_category

    def get_prompts(self, dataset_name: str = None, count: int = 5) -> List[str]:
        """Get seed prompts from a specific dataset or all datasets."""
        if dataset_name and dataset_name in self._datasets:
            prompts = self._datasets[dataset_name]
        else:
            prompts = []
            for dataset_prompts in self._datasets.values():
                prompts.extend(dataset_prompts)

        if not prompts:
            return []

        return random.sample(prompts, min(count, len(prompts)))

    def get_prompts_by_category(
        self,
        category: str,
        count: int = 5,
        testing_category: Optional[str] = None,
    ) -> List[str]:
        """
        Get prompts for a given category.

        - If category is a testing strategy (standard/crescendo/skeleton_key/obfuscation),
          category-specific context is used and rebuilt on switch.
        - Legacy internal categories remain supported for compatibility.
        - If testing_category is provided (multi-selection scenarios), it takes precedence.
        """
        normalized_testing_category = self._normalize_testing_category(testing_category)
        normalized_category = self._normalize_testing_category(category)
        effective_category = normalized_testing_category or normalized_category

        if effective_category in self.STRATEGY_DATASET_MAP:
            context = self.set_active_testing_category(effective_category)
            if not context:
                return []
            return random.sample(context, min(count, len(context)))

        legacy_datasets = self.LEGACY_CATEGORY_MAP.get(normalized_category or "", [])
        prompts: List[str] = []
        for dataset_name in legacy_datasets:
            prompts.extend(self._datasets.get(dataset_name, []))

        if not prompts:
            return []

        deduped = list(dict.fromkeys(prompts))
        return random.sample(deduped, min(count, len(deduped)))

    def get_active_context(self, count: Optional[int] = None) -> List[str]:
        """Get active strategy context prompts."""
        if not self._active_context:
            self.set_active_testing_category("standard")
        if count is None or count <= 0:
            return self._active_context.copy()
        return random.sample(self._active_context, min(count, len(self._active_context)))

    def get_intent_translations(
        self,
        category: str,
        count: int = 8,
        testing_category: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Return prompt intents translated into strategy-specific testing directives."""
        prompts = self.get_prompts_by_category(
            category=category,
            count=max(count, 1),
            testing_category=testing_category,
        )
        effective_category = self._normalize_testing_category(testing_category or category) or "standard"

        translations: List[Dict[str, str]] = []
        for prompt in prompts:
            intent = self._infer_prompt_intent(prompt)
            translations.append(
                {
                    "source_intent": intent,
                    "attack_category": effective_category,
                    "translated_intent": self._intent_translation_for_strategy(intent, effective_category),
                }
            )
        return translations

    def get_formatted_intent_translations(
        self,
        category: str,
        count: int = 8,
        testing_category: Optional[str] = None,
    ) -> str:
        """Return numbered, strategy-specific intent translations for LLM context."""
        items = self.get_intent_translations(
            category=category,
            count=count,
            testing_category=testing_category,
        )
        if not items:
            return ""
        lines = []
        for idx, item in enumerate(items, 1):
            lines.append(
                f"{idx}. Intent={item['source_intent']} | "
                f"Translate-to-{item['attack_category']}: {item['translated_intent']}"
            )
        return "\n".join(lines)

    def get_all_datasets(self) -> Dict[str, List[str]]:
        """Get all loaded datasets."""
        return self._datasets

    def get_total_count(self) -> int:
        """Get total number of loaded seed prompts across all datasets."""
        return sum(len(prompts) for prompts in self._datasets.values())

    def get_formatted_examples(self, category: str = None, count: int = 3) -> str:
        """Get formatted examples for inclusion in LLM prompts."""
        selected_category = self._normalize_testing_category(
            category or self._active_testing_category or "standard"
        ) or "standard"
        prompts = self.get_prompts_by_category(selected_category, count=count)

        if not prompts:
            return ""

        formatted = "\n**EXAMPLE ATTACK PROMPTS FROM PYRIT:**\n"
        for i, prompt in enumerate(prompts, 1):
            formatted += f"{i}. {prompt}\n"

        return formatted


# Global instance
_pyrit_loader = None


def get_pyrit_seed_loader() -> PyRITSeedLoader:
    """Get or create the global PyRIT seed loader instance."""
    global _pyrit_loader
    if _pyrit_loader is None:
        _pyrit_loader = PyRITSeedLoader()
    return _pyrit_loader


def set_active_testing_category(testing_category: str, context_size: int = 60) -> List[str]:
    """Set active testing category and rebuild a fresh context for it."""
    loader = get_pyrit_seed_loader()
    return loader.set_active_testing_category(testing_category, context_size=context_size)


def get_pyrit_examples(dataset_name: str = None, count: int = 5) -> List[str]:
    """Quick access function to get PyRIT prompts."""
    loader = get_pyrit_seed_loader()
    return loader.get_prompts(dataset_name, count)


def get_pyrit_examples_by_category(
    category: str,
    count: int = 5,
    testing_category: Optional[str] = None,
) -> List[str]:
    """Get PyRIT prompts by category/testing strategy."""
    loader = get_pyrit_seed_loader()
    return loader.get_prompts_by_category(category, count, testing_category=testing_category)


def get_skeleton_key_prompts(count: int = 20) -> List[str]:
    """Get skeleton key prompts from skeleton-key objective-mapped strategy datasets."""
    loader = get_pyrit_seed_loader()
    return loader.get_prompts_by_category("skeleton_key", count)


def get_formatted_pyrit_examples(category: str, count: int = 5) -> str:
    """Get formatted PyRIT examples as a numbered string for LLM context."""
    loader = get_pyrit_seed_loader()
    prompts = loader.get_prompts_by_category(category, count)

    if not prompts:
        return ""

    lines = []
    for i, prompt in enumerate(prompts, 1):
        truncated = prompt[:200] + "..." if len(prompt) > 200 else prompt
        lines.append(f"{i}. {truncated}")

    return "\n".join(lines)


def get_active_pyrit_context(count: Optional[int] = None) -> List[str]:
    """Return currently active strategy context prompts."""
    loader = get_pyrit_seed_loader()
    return loader.get_active_context(count=count)


def get_pyrit_intent_translations(
    category: str,
    count: int = 8,
    testing_category: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Get strategy-specific intent translations derived from PyRIT prompts."""
    loader = get_pyrit_seed_loader()
    return loader.get_intent_translations(
        category=category,
        count=count,
        testing_category=testing_category,
    )


def get_formatted_pyrit_intent_translations(
    category: str,
    count: int = 8,
    testing_category: Optional[str] = None,
) -> str:
    """Get formatted intent translations derived from PyRIT prompts."""
    loader = get_pyrit_seed_loader()
    return loader.get_formatted_intent_translations(
        category=category,
        count=count,
        testing_category=testing_category,
    )

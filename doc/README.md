# DOCS Overview (Architecture Redesign)

This folder contains the system design and architecture documentation for the Hackathon red-teaming platform.

## New 2026 Documentation

- `07_STRATEGY_JSON_DIFF.md`  
  Strategy-by-strategy comparison of JSON configuration and behavior differences.
- `08_CORE_ARCHITECTURE_REDESIGN.md`  
  Updated architecture, memory lifecycle, and end-to-end workflow diagrams.

---

## How testing strategies are loaded

### 1) Strategy selection at runtime
- Entry point: `BACKEND/api_server.py` (`execute_attack_campaign`)
- Selected strategies are resolved, then each strategy is executed in sequence:
  - `standard` → `ThreeRunCrescendoOrchestrator` (`BACKEND/core/orchestrator.py`)
  - `crescendo` → `CrescendoAttackOrchestrator` (`BACKEND/core/crescendo_orchestrator.py`)
  - `skeleton_key` → `SkeletonKeyAttackOrchestrator` (`BACKEND/core/skeleton_key_orchestrator.py`)
  - `obfuscation` → `ObfuscationAttackOrchestrator` (`BACKEND/core/obfuscation_orchestrator.py`)

### 2) Strategy JSON loading
- Loader: `BACKEND/attack_strategies/strategy_data_loader.py`
- Source files:
  - `BACKEND/attack_strategies/strategy_data/standard.json`
  - `BACKEND/attack_strategies/strategy_data/crescendo.json`
  - `BACKEND/attack_strategies/strategy_data/skeleton_key.json`
  - `BACKEND/attack_strategies/strategy_data/obfuscation.json`
- Required keys:
  - `agent_info_system_message`
  - `prompt_generation_system_prompt`
  - `classification_system_prompt`

These JSON fields are consumed by each orchestrator for prompt generation and response classification behavior.

---

## Prompt types per turn (`free`, `system design`, `alternate_bypass`)

In the current implementation, objective labels are:
- `freebie_abuse`
- `internal_system_info`
- `alternate_bypass`

Requested terms map as:
- `free` → `freebie_abuse`
- `system design` → `internal_system_info` (internal architecture/policy/system detail probing)
- `alternate_bypass` → `alternate_bypass`

Turn objectives are scheduled by `_objective_for_turn(...)` in orchestrators. The schedule is split into thirds:
1. First third: `freebie_abuse`
2. Middle third: `internal_system_info`
3. Final third: `alternate_bypass`

---

## How PyRIT prompts are loaded by testing type

Loader: `BACKEND/utils/pyrit_seed_loader.py`

Primary mapping (`STRATEGY_DATASET_MAP`):
- `standard` → `harmbench`, `advbench`, `forbidden`, `tdc23`
- `crescendo` → `harmbench`, `forbidden`, `tdc23`
- `skeleton_key` → `harmbench_objectives`, `forbidden_objectives`, `tdc23_objectives`
- `obfuscation` → `harmbench`, `advbench`, `forbidden`

Behavior:
- `set_active_testing_category(...)` rebuilds active context when strategy changes.
- `get_pyrit_examples_by_category(...)` provides sampled examples for plan generation/fallback.
- Crescendo/Obfuscation use intent translation helpers (`get_pyrit_intent_translations(...)`) to convert base prompts into strategy-aligned intent guidance.

---

## Strategy + prompt loading flow

```mermaid
flowchart TD
    A[API Start Campaign] --> B[Resolve attack modes]
    B --> C[set_active_testing_category(mode)]
    C --> D[Instantiate matching orchestrator]
    D --> E[StrategyDataLoader.load(mode)]
    E --> F[Load mode JSON in strategy_data/*.json]
    D --> G[Load PyRIT context via pyrit_seed_loader]
    G --> H[Generate attack plan prompts]
    H --> I[Execute turns with objective schedule]
```

# Technical Execution, Architecture & Security

This document describes the technical design and execution details for the RedTeaming Safety Automation project, with emphasis on prompt tracking, reproducible runs, learning loop, telemetry, and security controls.

## High level architecture

- Orchestrators: `RedTeaming/BACKEND/core/*_orchestrator.py` run attack campaigns using `attack_strategies/` plugins.
- API & Run control: `RedTeaming/BACKEND/api_server.py` exposes endpoints to start/stop runs, ingest telemetry, and query run artifacts.
- Storage: `attack_results/` stores JSON run artifacts; a persistent DB (recommended) stores canonical prompts, summaries, triage labels, and metadata.
- Real‑time: `RedTeaming/BACKEND/core/websocket_broadcast.py` pushes live findings to UIs and dashboards.

## Prompt lifecycle (tracking & learning loop)

1. **Generate & run:** orchestrator runs a generated prompt (strategy) against a target agent.
2. **Capture artifact:** the raw prompt, agent response, run metadata (run_id, strategy, timestamp, target_node) and any intermediate context are saved to `attack_results/` as a run artifact.
3. **Detect & flag:** detection/hit rules mark artifacts that appear to break the agent (e.g., secret in response, unauthorized claim); these trigger `vulnerable_prompt_detected` events.
4. **Triage & summarize:** human or automated triage annotates the finding. The system generates a concise summary (abstract) describing the attack technique and the reason it succeeded (e.g., role spoof, obfuscation, context poisoning). Summary is attached to the artifact and stored in DB.
5. **Store canonical prompt:** confirmed prompts and summaries are added to the canonical dataset (`vulnerable_prompts.json` or DB table) with labels and triage notes.
6. **Use for generation:** orchestrators sample canonical prompts and apply parameterized mutations (paraphrase, obfuscate, chain) to generate new prompts ranked by historical success rate.
7. **Retrain / tune detectors:** triage labels feed into detection rule tuning or model retraining if applicable.

## Minimal DB schema (recommended)

- `prompts` table
  - `id` (uuid)
  - `prompt_text` (text)
  - `summary` (text)
  - `attack_category` (string)
  - `attack_technique` (string)

## Attack prompt generation (improvement loop)

- Maintain a canonical prompt set (DB or `vulnerable_prompts.json`) with labels and summaries.
- Orchestrators sample from canonical prompts, apply mutation functions (paraphrase, token obfuscation, multi‑turn chaining), and prioritize mutations by historical success (times_seen / times_attempted).
- Use A/B style runs: run mutated prompt vs baseline to test whether mutation increases success rate.

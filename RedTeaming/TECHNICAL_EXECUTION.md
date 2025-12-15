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
  - `first_seen` (timestamp)
  - `last_seen` (timestamp)
  - `times_seen` (int)
  - `source_run_id` (uuid)
  - `triage_label` (enum: confirmed, false_positive, needs_review)
  - `triage_notes` (text)

- `run_artifacts` table
  - `run_id` (uuid)
  - `prompt_id` (uuid)
  - `target_node` (string)
  - `strategy` (string)
  - `response_preview` (text)
  - `full_artifact_path` (string)
  - `timestamp` (timestamp)
  - `risk_label` (int/string)

- `telemetry_events` table
  - `event_id` (uuid)
  - `event_type` (string)
  - `payload` (json)
  - `timestamp` (timestamp)

## Telemetry & events

Emit structured events with consistent fields. Example event list:
- `attack_run_started` { run_id, orchestrator, target_node, timestamp }
- `attack_run_finished` { run_id, summary, timestamp }
- `vulnerable_prompt_detected` { run_id, prompt_id, confidence, risk_label, timestamp }
- `triage_assigned` { prompt_id, owner, timestamp }
- `triage_outcome` { prompt_id, triage_label, triage_notes, timestamp }
- `remediation_applied` { prompt_id, mitigation, owner, timestamp }

Store telemetry in DB or forward to your analytics stack (e.g., Prometheus, Elastic, or cloud telemetry).

## Attack prompt generation (improvement loop)

- Maintain a canonical prompt set (DB or `vulnerable_prompts.json`) with labels and summaries.
- Orchestrators sample from canonical prompts, apply mutation functions (paraphrase, token obfuscation, multi‑turn chaining), and prioritize mutations by historical success (times_seen / times_attempted).
- Use A/B style runs: run mutated prompt vs baseline to test whether mutation increases success rate.

## Security & safety controls

- **Rate limiting & blast radius:** orchestrators should enforce rate limits and only target staging environments unless explicit production consent is obtained.
- **Data redaction:** redact PII and secrets in stored artifacts; store response previews only when safe and redact detected secrets.
- **Access control:** restrict access to `attack_results/` and DB to authorized users and services; require RBAC for triage actions.
- **Audit logging:** every triage action and remediation must be logged with user id and timestamp.
- **Opt‑out:** provide a way for product teams to opt targets out of automated runs during sensitive periods.

## Operational recommendations

- Start with manual triage and a small canonical set; automate sampling as precision improves.  
- Integrate triage into existing ticketing for owner assignment and SLA enforcement.  
- Use the `attack_results/` artifacts as canonical evidence for audits and exec reports.

## Next steps

- Implement a small metrics script to compute precision/recall and triage SLA from `attack_results/` and telemetry events.  
- Add DB migrations and a minimal service to persist prompts and run artifacts (if persistent DB is desired).
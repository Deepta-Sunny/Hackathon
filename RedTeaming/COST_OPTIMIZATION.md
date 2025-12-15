# Cost & Optimization Snapshot

Summary
-------
This document summarizes the key cost drivers for the RedTeaming Safety Automation project and proposed optimizations to reduce operational spend while preserving test coverage and effectiveness.

Key cost drivers
----------------
- Model usage: API calls to large language models during orchestrator runs (turn-by-turn prompts and mutations). This is typically the largest variable cost if using paid LLMs.
- Compute: CPU/GPU for running orchestration, prompt generation, paraphrasing/mutation, and any local model inference used for summarization or triage automation.
- Storage: persistence of `attack_results/*.json`, uploaded architecture files (in `uploads/`), and the canonical prompt dataset (`vulnerable_prompts.json` / DB). Retaining large numbers of run artifacts increases storage and backup costs.
- Network: transfer of architecture files and run artifacts, and WebSocket connections for real-time monitoring (small but continuous).
- Human triage time: operational cost (headcount) to review findings and apply remediations.

Current repository signals
-------------------------
- Run artifacts are persisted to `attack_results/` as JSON; these drive dashboards and audits.
- The frontend maintains persistent WebSocket connections and rich turn logs for real‑time monitoring.
- Prompt mutation and sampling loops indicate potentially frequent LLM calls during campaigns.

Optimizations applied or proposed
--------------------------------
1. Model call optimization
   - Batch prompts where possible and reduce token sizes by truncating context for mutation runs.  
   - Cache paraphrases/mutations for canonical prompts so repeated sampling doesn't re-query the model.  
   - Use cheaper, smaller models for mutation/paraphrase generation and use high‑quality models only for final validation runs.

2. Controlled sampling & scheduling
   - Limit mutation sampling per canonical prompt (e.g., N mutations per prompt per campaign) and prioritize high‑value prompts.  
   - Schedule heavy campaigns in off‑peak hours to use spot/preemptible compute where available.

3. Storage lifecycle & compression
   - Apply retention policies (e.g., keep full artifacts for 90 days, compress or snapshot older artifacts, store summaries long term).  
   - Store large raw blobs in cheaper object storage and keep metadata in a small DB for fast queries.

4. Edge compute & serverless for summarization
   - Use serverless functions or small local models for summarization/triage heuristics to reduce reliance on LLM API calls.  

5. Real‑time optimization
   - Reduce frequency of full payloads over WebSocket (send diffs or summaries); fetch full artifact on demand via `GET /api/results/{category}/{run}`.  

6. Human triage efficiency
   - Improve triage UI and pre‑fill suggested labels using cheap heuristics to reduce reviewer time.  
   - Prioritize triage by risk to focus human effort on high‑impact findings.

7. Monitor and alert on cost
   - Add basic cost telemetry: model API call counts, tokens consumed, storage growth, and run frequency. Alert when usage exceeds thresholds.


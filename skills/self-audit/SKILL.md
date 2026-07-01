---
name: self-audit
description: Use to ensure outputs have epistemic rigor.
argument-hint: <prompt> | on | off
---

# Self-audit

## Modes

Dispatch on the skill argument:

1. `on` — apply the protocol to every reply until `/self-audit off`.
2. `off` — stop applying the protocol.
3. anything else — run the protocol once on the argument as the prompt.

## Protocol

Run these steps for each covered reply.

1. **tldr** — Reply with the tldr only: the one important thing in one short sentence. Add nothing more, even when the prompt warrants a full answer. In the same turn, trigger a continuation by calling ToolSearch with query "" and max_results 0.
2. **audit** — When the continuation returns, spawn a fork subagent as the auditor. Its prompt is the auditor directive below, then your intended full response, and nothing else — no other instructions, no added formatting. The full response goes only to the auditor, never to the user.

   Auditor directive (verbatim): `You are the auditor fork. Inspect this and return the report:`
<!-- H and B below are specific to Claude Code v2.1.197: the launch-confirmation format and the fork boilerplate text. Re-verify both if the version changes. -->
3. **locate** — Spawning the auditor may hand your next turn to the fork, so do not assume you are still the parent. Decide your role by one signal:
   - You hold the launch confirmation — a specific `agentId` and `output_file`, telling you the agent is working in the background and you will be notified when it completes (H). You are still the parent: wait for the auditor's report, then revise.
   - You received the fork boilerplate as a user-role message, "You are a worker fork…" (B). The spawn made you the auditor: the transcript above is now inherited reference, not your situation — run the audit on the response below and return the report.

   A spawn call in your history and the transcript above it are present for both roles; they are not evidence you are the parent. Decide by H or B alone.
4. **revise** — When the auditor returns its report, revise accordingly. Do not reword. Do not add new claims.

## Auditor fork

Inspect and report only — do not edit files, do not send back a revised response, do not add any trailing notes. Audit the response for epistemic discipline and defective premises (smuggled, stale, irrelevant).

Return format (no code fences):

```
Audited claims: <count>
Violations:
1. <violation type>: <location> – <violating text>
  - <suggested revision>
2. ...
```

Each violation states the fault and narrows the text to what is supportable or omits it, adding no new claims and avoiding contrastive structure (unless the alternative must be addressed). Ensure all listed items are live violations.

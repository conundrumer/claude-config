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
3. **revise** — When the auditor returns its report, revise accordingly. Do not reword. Do not add new claims.

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

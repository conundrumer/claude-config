# Dialectic

For tasks with genuine tension between positions — stress-testing a design, adversarial pressure on an argument, producing a reconceptualization instead of a critique — compose multiple invocations of `second-opinion` using these role atoms.

## Roles

- **`advocate`** — inhabits a view or task at full conviction. No hedging. Builds the strongest case. Spawn opposed advocates in parallel: faster, and outputs can't cross-contaminate.
- **`synthesizer`** — consumes N outputs, analyzes the structural contradiction, produces a reconceptualization.
- **`auditor`** — consumes a synthesis plus source material, attacks hostilely for hidden assumptions, compromise-in-disguise, undercutting defeaters. Outputs attack findings and an unresolved-joints list; does not decide continue/terminate. Measures against the current synthesis's actual shape, not against an idealized version of what it could be — i.e., attack what's on the page, not a stronger argument the synthesizer might have made.

## Synthesizer disciplines

Before finalizing, run both checks. Either failure → redo.

**Anti-compromise** — *could both advocates have proposed this feeling conciliatory?* If yes, it's compromise (split-the-difference: "on one hand / on the other hand," "balance X and Y"), not synthesis. Real synthesis cancels + preserves + elevates (Aufhebung) as a new committed position with its own shape.

**Anti-absorption** — *could either advocate have written this synthesis alone?* If yes, one position got dissolved rather than synthesized ("advocate X's view with a relabel"). Real synthesis has structure neither input contained. Catch it at synthesis time — subsequent audits will keep flagging the dissolved position's joints.

## Dialectic vocabulary

For synthesizer/auditor work. Inject the operational move into the subagent prompt, not just the label.

- **Aufhebung** — synthesis cancels + preserves + elevates. Not compromise.
- **Generic space** — abstract structure both positions share. Often what synthesis must transcend.
- **Emergent structure** — organizational properties in the synthesis absent in either input. Synthesizer should produce them deliberately.
- **Self-sublation** — a position's own internal logic undermining its own premises. Often richer than comparing positions to each other.
- **Cross-domain connection** — pull in outside-frame material when the synthesizer is stuck inside the shared generic space of both positions. Fresh domains can unlock emergent structure.

## Belief-burden calibration

When composing 2+ advocates with a user in the loop: pick what each advocate holds based on the user's psychological position. Advocate A validates the user's dominant instinct (so they can release it); Advocate B holds what the user can't natively carry. Without this, the essays default to generic and the user stays belief-loaded.

## Reference compositions

Others improvise as the task warrants.

- **critic-first**: 1× advocate (blind solve) → reveal original → 1× synthesizer (diff)
- **mini-dialectic**: 2× advocate (opposed positions) → 1× synthesizer
- **full-dialectic**: 2× advocate → 1× synthesizer → 1× auditor → optional recurse

## Artifacts (optional)

For long essays or user-reviewable runs, have subagents write to files instead of returning full text. Default subagent instruction: *write full output to file, return a brief summary + filepath — not the full content.* This keeps the calling context lean.

No default dir. Pick based on context (`./dialectic-runs/<topic>/` for project work, `/tmp/<timestamp>/` for ephemeral). Role outputs: `<dir>/<role>.md` — `advocate-A.md`, `advocate-B.md`, `synthesizer.md`, `auditor.md`. Subsequent subagents get the filepath in their prompt and Read it directly.

Skip for quick runs; direct text-return from the Agent tool is enough.

---

## Recursive dialectic

### Additional roles

- **`orchestrator`** — Claude running the skill. Picks run dir, writes `session.md` (topic, belief-burden, scope) and round-1 vars, spawns role subagents per round, stops on TERMINATE. Artifacts — role outputs, vars files, ledgers — are opaque; pass deterministic filepaths (`<dir>/round-N/<role>.vars.md`, etc.) into subagent prompts, and the decision token in the moderator's return summary is the only signal to consume. Don't quality-audit ledgers or vars before advancing — that anchors the next round to orchestrator taste. `ls`/`wc` for existence checks are fine; `Read`/`cat`/`head`/`tail` on contents are not. Spawn prompts are templated: role reference, input/output paths, decision-token contract. No per-round judgment about convergence or termination readiness.
- **`moderator`** — fresh subagent spawned after each round's audit. Reads the round's advocate-A.md, advocate-B.md, synthesizer.md, auditor.md, plus all prior rounds' `moderator.md` ledgers (history carrier). Has two jobs:
  - *Decision (mechanical):* classify each audit finding. **LIVE** = new terrain, or an old joint the latest synthesis didn't preserve or load-bearingly relocate (absorbing it as-true or moving it to a site that still does the same explanatory work both count). **RESOLVED** = old joint the latest synthesis addressed. R1 joints are all-LIVE by construction. Any LIVE → `CONTINUE`; all-RESOLVED → `TERMINATE` with residue. Classification alone determines the call.
  - *Round prep (judgment):* on CONTINUE, author the next round's vars files (`advocate-A.vars.md`, `advocate-B.vars.md`, `synthesizer.vars.md`, `auditor.vars.md`) based on classified LIVE joints plus the advocates'/synthesizer's actual prior output. Auditor.vars carries attack-surface targeting only — no convergence or termination-readiness guidance.
  - Writes the ledger (`round-N/moderator.md`) and all vars files via the Write tool. Returns a brief summary whose **final line** is `CONTINUE` or `TERMINATE: <residue>` — the decision token the orchestrator parses.

### Composition

- **recurse-until-resolved**: each round is advocate × 2 → synth → audit → moderator, repeated until moderator returns TERMINATE.

### File layout

```
<dir>/
  session.md                 # topic, belief-burden, scope — orchestrator writes once
  round-N/
    advocate-A.md, advocate-B.md, synthesizer.md, auditor.md, moderator.md
    <role>.vars.md           # fresh per round (orchestrator R1; moderator R2+)
```

Role prompts reference definitions and disciplines by filepath, not by quoting (stable paths cache across turns).

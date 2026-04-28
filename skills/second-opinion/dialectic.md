# Dialectic

For tasks with genuine tension between positions — stress-testing a design, adversarial pressure on an argument, producing a reconceptualization instead of a critique — compose multiple invocations of `second-opinion` using these role atoms.

## Roles

Each role's full spec lives in its own file under `roles/`. Spawn prompts reference these by filepath; subagents Read them on launch.

- `roles/advocate.md` — inhabits a view at full conviction. Spawn opposed advocates in parallel: faster, and outputs can't cross-contaminate.
- `roles/synthesizer.md` — consumes N outputs, analyzes structural contradiction, produces reconceptualization.
- `roles/auditor.md` — attacks a synthesis hostilely for hidden assumptions, compromise-in-disguise, undercutting defeaters. Outputs objections.

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

### Additional role

- `roles/moderator.md` — fresh subagent spawned after each round's audit. Classifies objections as LIVE/RESOLVED, assigns T-IDs to new threads, writes the round's live-thread snapshot. Returns a decision token.

The orchestrator (Claude running the skill) picks the run dir, writes `session.md`, spawns role subagents per round, stops on TERMINATE. Artifacts — role outputs, per-round threads.md — are opaque; pass deterministic filepaths into subagent prompts, and the decision token in the moderator's return summary is the only signal to consume. Don't quality-audit role outputs before advancing — that anchors the next round to orchestrator taste. `ls`/`wc` for existence checks are fine; `Read`/`cat`/`head`/`tail` on contents are not. No per-round judgment about convergence or termination readiness.

### Spawn prompt template

Role spawns follow this template:

```
You are <role> in round <n> of a dialectic.

Read list (do not read anything else):
1. <role spec path>
2. <other inputs>

Complete the primary task per <role spec>. Write to <primary-path>.
```

The lockout prevents the agent from pulling in adjacent specs that would skew the primary task.

Per-role inputs:
- **advocate**: `session.md`; in N>1 also prior `threads.md` and prior `synthesizer.md`
- **synth**: `session.md` + this round's `advocate-A.md`, `advocate-B.md`; in N>1 also prior `threads.md` and prior `synthesizer.md`
- **auditor**: this round's `advocate-A.md`, `advocate-B.md`, `synthesizer.md`, `synth-threads.md`; in N>1 also prior `threads.md` and prior `synthesizer.md`
- **moderator**: this round's `advocate-A.md`, `advocate-B.md`, `synthesizer.md`, `synth-threads.md`, `auditor.md`; in N>1 also prior `threads.md`; in N>2 also prior `moderator.md` (its `## Recurrence` section feeds the cross-round recurrence check)

### `session.md`

Orchestrator writes this once at run start. Contains:

```markdown
# Session

## Topic
<topic>

## Scope
<scope>

## Positions
- A: <one-sentence position>
- B: <one-sentence position>

## Belief-burden notes
<orchestrator reasoning — why A holds this and B holds that>
```

Both advocates read the same `session.md` and pick up their own line from `## Positions`. The synthesizer reads it for run context. Auditor and moderator don't read it.

### Composition

- **recurse-until-resolved**: each round is advocate × 2 → synth → audit → moderator, repeated until moderator returns TERMINATE.

### After TERMINATE

The orchestrator returns the path to the final round's `synthesizer.md` (the substantive output the dialectic landed on), the moderator's residue prose (in the final round's `moderator.md`), and the final `threads.md` (any threads still LIVE — the questions the dialectic deliberately left open). On `reason: recurrence`, the dialectic terminated at structural impasse rather than honest resolution — flag this in the return summary. The full per-round trail remains on disk as the audit trail.

### File layout

```
<dir>/
  session.md                 # topic, scope, positions, belief-burden — orchestrator writes once
  round-N/
    advocate-A.md, advocate-B.md
    synthesizer.md           # prose + ## Structural move + ## New claims
    synth-threads.md         # ## New threads + ## Disposition
    auditor.md
    moderator.md
    threads.md               # live-thread snapshot at end of round N (moderator's secondary output)
```

Each `round-N/threads.md` is a write-once snapshot of the state at the end of round N. Roles in round N+1 read it as `round-<n-1>/threads.md` for the inherited live-thread set.

Role prompts reference definitions by filepath, not by quoting (stable paths cache across turns).

### Move-pass (opt-in)

Off by default. When the user opts in (e.g., "with move-pass"), advocate / synth / auditor each produce an additional structured-moves file per round. Read `move-pass.md` for the protocol, file-layout addition, and spawn extension; otherwise ignore.

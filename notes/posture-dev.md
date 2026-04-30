# Posture dev

How the lift posture emerged. Pair with `posture.md`.

## Origin

Started from a meta-skill exploration: three workflow-design briefs (dialectic; writer/editor; ARC-AGI-2 + an evolving DSL) run through two conditions — naive fresh Claude, and Claude using the official `skill-creator`. Both consistently over-engineered: five-to-six phase pipelines, knob-rich config, premature decomposition.

The thing wanted is a *posture*, not a skill. An always-on register-shift triggered by lightweight phrasing. Skills are invoked; this move comes up constantly. Skills package procedure; this move resists procedure. CLAUDE.md territory.

## Why "lift"

Alternatives: `document`, `structure`, `capture`, `formalize`, `promote`, `sketch`. `Lift` is lightweight + evocative (raising abstraction level) + distinct, so once established it carries one meaning. `Document` magnetizes instruction-mode; `formalize` is too heavy; `capture` implies something complete.

## Why principles, not procedures

The default attractor for "design a workflow" or "doc this" is *phase decomposition + numbered steps + knobs*. Procedures freeze assumptions, hide the why, and break the moment a case lands outside the enumeration. Principles + reasons let the reader generalize and override. In tests, control runs reflexively wrote numbered procedures; treatment runs stayed in principle-register.

## Why noun-as-disambiguator

The substrate often has multiple liftables. A coding session has a coding pattern (object level) and a collaboration pattern (meta level). One trigger word can't pick.

`let's lift this workflow into a doc` was ambiguous — treatment read abstract (pattern-level), control read procedural (steps). `let's lift our process into a doc` landed at meta-level across runs; control wrote procedurally, treatment held principle-register. The noun disambiguates *level*; the posture handles *register*. `process` is process-shaped, `approach` is object-shaped, `workflow` carries both.

So `let's lift X` is canonical. The user's noun points at the level. The posture trusts the noun's semantic gravity. Enumerating noun→level mappings freezes vocabulary that's still developing.

## The tests that drove the shape

1. **Workflow-design briefs × naive/skill-creator.** Both over-engineered. → posture-shaped territory.
2. **Lift on a technical-state summary of a coding session.** Treatment lifted the pattern, control lifted the feature. Both stayed below meta-level. → substrate carries most weight; summaries hide what summaries summarize.
3. **Lift on the actual session JSONL (resume).** Both lifted the human↔AI process — substrate change was the dominant variable. Treatment shipped principle-register; control shipped numbered-procedure register.
4. **Posture with the noun→level mapping made explicit.** Treatment doc was longer (98 vs 36 lines) and surfaced more patterns at the right level. Posture compression sharpens level signal, not output length.

## Considered, not kept

- **Trigger aliases.** One verb, one signal.
- **"Opinionated defaults + NL overrides"** as a posture principle. Workflow-design-specific; doesn't fire when lifting general docs.
- **Hard guards via prompt.** Test-design lesson, not posture content: prompt guards lose to substrate priming when the resumed session has thousands of lines of Write/Edit usage. Use CLI-level tool restrictions for hard guards.

## Bidirectional refinement

Development is two-sided. The user surfaced things by running tests — that "workflow" was ambiguous; that summaries hide what summaries summarize; that doc-write behavior is controlled by substrate, not posture; that they're developing a skill themselves (which words land, which level to aim at, when to override).

The posture's `the user is still figuring it out` line points at this directly. The artifact has to be legible to a developing reader; both sides develop. The override channel — `let's lift X` with X being the user's choice — is where developing taste enters.

## What's load-bearing now

- `lift` as canonical verb
- Noun-gravity for disambiguation; trust the user's noun choice
- Principle + reason, not step + procedure
- Don't decompose preemptively
- Stable core + open envelope (load-bearing-now / still-open close)
- The user is developing alongside the artifact

## What's still open

- Whether the posture should encode "if multiple liftables, name what you saw and which one you took." Currently relies on noun-gravity + override channel. Hasn't broken yet.
- Cross-domain test: only tested on AI-methodology and code-pattern domains. Would the same posture work for a research note, a meeting summary, a relationship conversation? Untested.
- Failure modes when substrate is sparse. The posture assumes there's a conversation rich enough to lift from. No fallback for thin substrate.
- Whether `the user is still figuring it out` needs sharper articulation — currently a one-liner; might want examples.
- Interaction with other always-on instructions (global CLAUDE.md, project CLAUDE.md). Whether they compose or compete is untested.

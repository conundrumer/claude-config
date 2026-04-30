---
name: dialectic
description: Structured dialectic — opposed advocates + procedural judge + synthesis-mode surveyor + audited synthesis. For propositions where the consumer wants a *map* of where disagreement lives, not a fast verdict.
---

# Dialectic

Take a proposition (claim, decision, reconciliation), force two opposing advocates in parallel, route their disagreement through a procedural judge, run a synthesis-mode surveyor alongside, and integrate everything into an artifact tailored to what the consumer will do with it.

## When to invoke vs just-ask

Just-ask gives a calibrated verdict fast and catches synthesis-mode moves (hybrids, reframes, operationalizations). Dialectic gives a *map* — named cruxes, audited citations, surfaced concessions, dependency relationships. Use the framework when the map is what the consumer needs; use just-ask when a verdict is enough.

## Invocation

The user does not author a config. The user has been digging into a Thing in conversation; main Claude (the orchestrator) holds that context. When the user says something light ("dialectic this," "let's run a dialectic"), the orchestrator extracts the proposition from accumulated conversation, infers use case + mode (the two config decisions below), surfaces the inference in one line for correction, runs L0 with full machinery on confirmation, returns the verdict, and stops.

If conversational context is thin, that's a judgment call — ask one short question or proceed with what's there, depending on what the proposition needs.

If the proposition contains a multivalent predicate (e.g., "reconcile" — which of {logical compatibility, mutual support, joint endorsement, ...}?), surface the inferred sense in the same line, or ask one short question if unclear. Pre-pinning fixes the definition; it doesn't tell advocates what to argue.

The surfacing line names the inferred config and any predicate pinning. The user accepts silently, says go, or corrects:

> *"reconciliation, shared search. by 'reconcile' do you mean joint endorsement?"*
> *"soundness, split search."*
> *"decision, no search — your two options are A and B as we discussed."*

## Two config decisions

**1. Use case** (always inferable from conversation).

- "is this sound / can I trust this / how sound is X" → **soundness**
- "should I do A or B / how should I decide" → **decision**
- "do X and Y fit together / are these compatible" → **reconciliation**

If hybrid, pick the dominant shape and note the secondary. The three are common shapes, not exhaustive — other shapes (critique, diagnosis, comparison) are handled in natural language; if one recurs across many runs it earns documentation.

**2. Mode** (load-bearing — produces different verdicts on the same proposition).

- **No search** (defer): cleanest structural arguments. Misses post-cutoff literature. Pick for structural / mechanism / argument-from-principles propositions, or when the empirical premise isn't load-bearing, or when the literature is well-documented in training. Default if cost-tolerance is a stated concern.
- **Shared search**: an evidence agent pulls citations into a shared pool (`evidence.md`); advocates argue head-to-head on the same papers; surveyor produces synthesis-mode framings separately. Cleanest engagement. Pick when empirical premises are load-bearing AND conversation has mapped the literature. Default if unsure.
- **Split search**: each advocate fetches independently. Richest evidence layer, complementary citation sets. Pick when empirical premises are load-bearing AND the literature is fresh or unmapped — when finding evidence matters more than arguing it.

## Defaults

- **Recursion: L0 only.** No pre-commit to descent. Going deeper is a separate user decision after L0 ("another round on the [crux]" / "recurse until resolved" / "recurse until I say stop").
- **Surveyor: parallel synthesis-mode pass.** Surfaces hybrids, reframes, operationalizations, cross-cutting distinctions. Runs parallel to advocates so its surfacing isn't anchored on their framings. Integrated into the synthesis tree alongside advocate/judge transcripts.
- **Audit: always on.** Synths that integrate the surveyor produce attribution errors without it.
- **Response round: judge decides whether to fire.** Triggers when the judge's audit flags decisive uncountered moves, unforced concessions, or fact-checkable citations whose resolution would shift the verdict.
- **Dynamic pull primitives in no-search mode.**
  - *Judge pulls* on its own flags it classifies as load-bearing.
  - *Advocate self-pulls* on discretion. A required pull-rationale section is the discipline mechanism — pulls cluster on load-bearing empirical claims; advocates defer on theoretical/conceptual claims.
- **Surveyor isolation.** Advocates do not read the surveyor; the judge and synthesizer do. Keeps surveyor framings from anchoring advocates while letting the judge reconcile surveyor-surfaced moves before recommending a response round.

## Override channel

The substrate is natural language. The user can override anything in-conversation: "actually do split search," "skip the audit on this run," "another round on [crux]," "recurse until resolved." Apply the override and proceed without re-prompting for the rest of the config.

## Roles

Each role's brief lives in its own file under `roles/`. The dispatch prompt instructs the subagent to Read its assigned role file; run-specific values (claim, side, paths, etc.) go in the dispatch prompt itself, not the role file.

- `roles/advocate.md` — argues one side at full conviction. Spawn opposed advocates in parallel via Agent tool, `general-purpose`, `run_in_background: true`. Both read the same role file; dispatch prompt parameterizes side.
- `roles/judge.md` — procedural judge. Reads both advocate transcripts (and `surveyor.md` at L0) after they complete. Determines status (`resolved` / `unresolved`), names next sub-claim if useful, audits with the typed taxonomy, recommends response round if needed.
- `roles/surveyor.md` — synthesis-mode pass parallel to the advocate pair at L0. Posture-instructed for surfacing hybrids, reframes, operationalizations, cross-cutting distinctions.
- `roles/synthesizer.md` — produces the root artifact. Integrates advocate/judge/surveyor outputs into a conditional artifact tailored to the consumer. Field structure adapts to proposition shape — soundness, decision, and reconciliation use different fields.
- `roles/auditor.md` — fidelity check on the synthesis. Reads the synth and the tree, flags untraced claims, mischaracterizations, omitted findings, and fabricated cross-level implications. Procedural; does not re-synthesize.

## Advocate dispatch discipline

The orchestrator does **not** plant moves in advocate prompts. The dispatch supplies the proposition, side label, references (briefing, source, parent transcripts on descents), ancestry (recursion lineage), and the output path — nothing about which arguments to make, which technical moves to consider, or how to frame the position. The advocate generates its case from scratch and decides which disciplines to ground in from the proposition and briefing.

This is methodological, not stylistic. Argument-planting confounds the test: when the orchestrator's framings shape what advocates produce, claims about advocate quality, crux convergence, and engagement become partly orchestrator-shaped artifacts rather than framework output. Operationalization scaffolding (predicate-pinning) and deployment-context briefing are different — they describe the world the advocate is arguing about, not what to say.

Same principle for the judge: the judge audits and characterizes; it does not invent its own arguments.

## Dispatch sequence

The temporal order for a default L0 run:

1. **Briefing** — orchestrator writes `briefing.md` to the run dir: a self-contained doc for advocates, surveyor, and judge. If a source document exists, the briefing is an agent-summarized version of it (decide whether advocates read the source directly or rely on the briefing alone — user can specify: "prepare the materials first"). Otherwise it's an orchestrator-written framing from conversation history. If the proposition is about a concrete deployment (specific substrate, specific decision, specific temporal moment), include that context (e.g., "Claude Code subagents, 2026 frontier models, decision about cross-vendor APIs") — closes missed-moves without producing orchestrator-shaped artifacts.
2. **Evidence agent** (shared-search runs only) — pulls citations into `evidence.md` with no synthesis-mode framings. Advocates and surveyor read this.
3. **Advocates + surveyor in parallel** — three subagents fire simultaneously. Both advocates read `briefing.md` (and `evidence.md` if shared-search), write to their respective output paths. Surveyor reads `briefing.md` only, writes to `surveyor.md`.
4. **Judge** — fires after both advocates complete. Reads both advocate transcripts (and `surveyor.md` at L0); writes `judge.md` with status, next crux, typed audit, response-round recommendation.
5. **Response round (conditional)** — if judge wrote "Response round recommended? Yes": each advocate is re-dispatched with the original prompt + only the audit items assigned to their side, writes a focused `*-response.md` (dense, one pass). Then judge is re-dispatched with the originals + responses, writes `judge-v2.md`. At most one response round per level.
6. **Synthesizer** — reads the full tree (briefing, source if separate, advocates, surveyor, judge, evidence if any, response files if any), writes `synthesis.md`. Field structure adapts to proposition shape.
7. **Audit** — separate fidelity-checking agent reads the synth + the tree, writes `audit.md`:
   - `clean` or `minor issues` → accept synth as final.
   - `substantive issues` → re-run synth as `synthesis-v2.md` with audit findings as input.

For descents (L1+), repeat steps 3–7 in a level-keyed subdirectory. The new claim is the next-crux named in the parent's `judge.md` (or `judge-v2.md` if a response round fired); parent advocate/judge transcripts (including v2 if present) attach as references; ancestry extends to name the path from root through each level's crux (e.g., `[root claim] → [L1 crux] → [L2 crux]`). Use case and mode inherit from the parent run. The judge adds a recursion-productivity assessment (narrowing, axiom-hit, or spiral) to inform the user's stop/continue decision. Surveyor runs at L0 only.

## Audit taxonomy

The judge types each finding using a fixed taxonomy. Typing lets the orchestrator decide what to do with each audit (which trigger response rounds, which pass downward, which stay at level for synthesis).

- **Citation question** — fact-checkable claim about source, prior work, technical content. Note whether resolution would shift the verdict.
- **Resolved citation** — citation question after verification (e.g., judge pulled and confirmed). Passes downward symmetrically.
- **Shared premise** — fact both sides accept that neither flagged.
- **Missed concession** — concession one side made that the other did not press.
- **Unforced concession** — same, but where pressing would have been decisive.
- **Decisive uncountered move** — one side's strongest move addressed only obliquely or not at all.
- **Spiral signal** — disagreement structurally similar to a parent under new vocabulary.

## Response round

Mechanics in *Dispatch sequence* step 5.

Empirically does different work for different propositions (pruning sub-questions, sharpening forks, partitioning the proposition / a predicate / scope). Doesn't necessarily flip verdict labels; narrows.

## Downward-propagation rules (descents only)

When recursing into a named crux, only two audit types pass to the next-level advocates:

- **Shared premise** — passed as agreed ground that doesn't need re-arguing.
- **Resolved citation** — once verified, passed as shared evidence symmetrically.

All other types stay at their original level. They surface in the synthesis at the root.

## Produce-then-audit

At every layer, the framework follows this pattern:

- **Advocate layer:** produce stances → judge audits → optional response round.
- **Judge layer:** produce verdict → built-in typed audit on the advocate transcripts.
- **Synthesizer layer:** produce synthesis → fidelity audit (separate agent).

Integration introduces interpretation; interpretation drifts from source. Each layer's output benefits from a check after the fact.

## Subagent dispatch conventions

- **No numeric word-count ranges.** Subagents iterate to fit ranges, burning tool calls. Replace with "dense, no padding, one pass."
- **Direct write-to-file.** Subagents write outputs to specified paths via the Write tool. Orchestrator and consumer read from disk. Avoids copy-paste round-trips.
- **Tool scoping at dispatch.** The orchestrator scopes tool access in the dispatch prompt — advocates and judge get WebSearch/WebFetch only in search modes (or for no-search pulls); surveyor gets Read + Write only; synthesizer gets Read + Write, plus WebFetch when verifying citations against external sources (e.g., split-search runs where citations aren't shared in `evidence.md`). Role files describe behavior; tool access is dispatch-time so it can vary per mode.

## Run directory layout

No fixed location — the orchestrator picks based on context: `./dialectic-runs/<topic>/` for project work, `/tmp/dialectic-<timestamp>/` for ephemeral exploration. The orchestrator passes each subagent's output path in its dispatch prompt.

```
<run-dir>/
  briefing.md                    # orchestrator-generated
  evidence.md                    # shared-search runs only
  advocate-for.md
  advocate-against.md
  surveyor.md
  judge.md
  advocate-for-response.md       # if response round fires
  advocate-against-response.md   # if response round fires
  judge-v2.md                    # if response round fires
  synthesis.md
  synthesis-v2.md                # if substantive audit issues
  audit.md                       # synth audit
```

`advocate-for.md` / `advocate-against.md` is the default; domain-appropriate labels (`advocate-synthesis-seeker.md` / `advocate-irreconcilability-defender.md`) substitute when the side labels carry meaning. For descents, repeat the structure under `level-1/`, `level-2/`, etc.

## After the run

The orchestrator returns the synthesis path + a one-paragraph verdict summary to the conversation. Full audit trail stays on disk. The user decides next moves (recurse, drop, run another mode on a sub-question, etc.) — those are separate invocations.

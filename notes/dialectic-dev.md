# Dialectic dev

How the dialectic framework emerged. Pair with `skills/dialectic/`.

## Origin

The v0 hypothesis: forced advocacy beats just-asking on borderline claims. The default — single Claude pass — is good enough most of the time, so the question was whether a structured opposition produced something just-ask doesn't.

Partial confirmation. Across all runs, dialectic and just-ask covered different territory: just-ask catches synthesis-mode moves (hybrids, reframes, operationalizations), dialectic produces a structured map (named cruxes, audited citations, dependency relationships, ceded ground). Neither dominates. The framework earns its cost when the consumer wants the map; for a verdict, a single pass suffices.

That partial result reshaped what the framework was for: complementary to just-ask, not dominant. The architecture decisions follow from making the map *clean* and *auditable*.

## Why procedural judge

Substantive judges create a regress: who checks the judge? Procedural judges are grounded — they characterize state (resolved / unresolved / axiomatic), name next sub-claims, audit for missed moves, and assess descent productivity. The recursion itself is the check; a wrong descent gets pushed back on by the next round's advocates, and the tree only terminates at axioms or fresh second-opinion.

## Why orchestrator-inferred config, not user-authored flags

The user has been iteratively digging into a Thing with main Claude before invoking the dialectic. Main Claude already holds the conversation context — proposition, shape (soundness / decision / reconciliation), whether the empirical premise is load-bearing, whether the literature is recently-mapped. Asking the user to re-encode all that as flags duplicates the work and pushes the framework toward a config-heavy surface.

So: the user says something light ("dialectic this"); main Claude infers the use case + mode, surfaces the inference in one line, dispatches on confirmation. Levers exist as override points, not as flags. A lever earns documented status only if (a) the orchestrator can't reliably infer it *and* (b) the user would routinely want to override the inference. Both conditions must hold.

## Why minimal advocate prompts

The earliest runs gave advocates specific arguments, candidate technical moves, and framings of the position in their dispatch prompt. After surveying the run history, this turned out to be non-trivial leading — it materially shaped every finding that depended on advocate-generated content (advocate-engagement claims, specific technical-move attribution, crux convergence). It didn't fabricate the framework's findings, but it inflated reliability across the run history.

Reset starting with reconciliation-1: minimal advocate prompts. Proposition, side label, reference paths, format. No arguments, no candidate moves, no position framing. The reset re-rates prior findings as "with leading caveat" and conditions every subsequent run.

Two kinds of context survived the reset because they're not argumentative:

- **Operationalization scaffolding** — pre-pinning multivalent predicates (e.g., "by 'reconcile' do you mean joint endorsement?"). Closer to a definition than to leading.
- **Deployment-context briefing** — substrate, decision, temporal moment. Validated in pull-4 as a distinct axis from argumentative leading: closed missed-moves (model-staleness, deployment cost) without producing orchestrator-shaped artifacts.

Argumentative leading itself is off.

## Why three modes

Pull-1 ran defer / pull-indep / pull-shared (later renamed no-search / split search / shared search) in parallel on the same proposition (cross-vendor model ensembling). All three produced different verdicts on the same claim — the architecture is part of what produces the verdict. Each has a real trade:

- Defer / no-search (no tools at any layer): cleanest structural arguments, missed post-cutoff literature.
- Pull-indep / split search (each advocate fetches): richest evidence layer, complementary citation sets, advocates engaged past each other in v1.
- Pull-shared / shared search (surveyor pulls evidence, advocates share): cleanest head-to-head engagement, anchoring cost on surveyor framings.

Mode is the more load-bearing of the two config decisions: it changes the verdict, not just the artifact. The orchestrator decides per-run based on whether the empirical premise is load-bearing and whether the relevant literature is recently-mapped.

## Why evidence/framings separation

Pull-1's pull-shared had the surveyor produce both the evidence brief and synthesis-mode framings in one document. Advocates reused the surveyor's named hybrids verbatim instead of generating their own. Pull-2 ran the separation as a clean A/B: evidence agent → `evidence.md` (citations only), surveyor → `surveyor.md` (synthesis-mode framings, advocates don't read it). Advocates produced 3 genuinely novel framings + 4 sharpened versions, citation overlap held at ~85–90%.

Lesson generalized: any time a single agent produces both reference material and analytical framings, downstream agents anchor on the framings. Split roles cleanly.

## Why typed audit findings

The judge's audit isn't free-form; each finding is typed using a fixed taxonomy. **Citation question** (fact-checkable, possibly verdict-shifting), **shared premise** (both sides accept, neither flagged), **missed concession** (one side conceded, other didn't press), **unforced concession** (same, but pressing would have been decisive), **decisive uncountered move** (one side's strongest move addressed only obliquely), **spiral signal** (descent's disagreement structurally similar to parent under new vocabulary).

Typing lets the orchestrator route findings: which trigger the response round (decisive uncountered, unforced concession, verdict-shifting citation), which propagate to the next descent level (shared premise, resolved citation), which stay at level for synthesis (the rest). Without typing, the response round can't be cleanly gated and the descent inherits noise.

## Why response round

Without it, decisive uncountered moves and load-bearing concessions sit unaddressed in the transcript and the verdict is artificially confident. The judge fires the response round when its typed audit contains gating items; each advocate gets only the items relevant to their side, writes a focused 1–2 paragraph response; judge re-issues verdict. Cost: ~3 calls per round, max one per level.

Empirically does different work for different proposition shapes — sub-question pruner, fork-sharpener, proposition-partitioner, predicate-partitioner, scope-partitioner. Doesn't necessarily flip verdict labels; narrows. Five distinct shapes observed across n=5 runs; the taxonomy is descriptive, not prescribed.

## Why audit primitive

Integration introduces interpretation; interpretation drifts from source. Each layer's output benefits from a check after the fact. The audit reads the synth + the tree, verifies non-trivial claims trace to source, flags untraced claims, mischaracterizations, omitted findings, fabricated cross-level implications.

Empirically scales with attribution surface. Simple synths (advocates + judges only) returned cosmetic findings — trigger-based use suffices. Integrated-surveyor synths produced two real attribution-error shapes: **role-confused attribution** (misattributing between surveyor and judge) and **architecture-confused attribution** (over-recruiting under-equipped architectures into convergence framings on multi-architecture runs). Run by default once the surveyor is integrated.

The pattern generalizes: produce-then-audit at every layer. Advocate produces stance → judge audits → optional response round. Judge produces verdict → built-in audit taxonomy in Notes. Synth produces synthesis → optional audit primitive.

## Why dynamic pull primitives

Defer-mode's load-bearing citation questions stay unresolvable because no layer can pull. Two primitives close the gap without making advocates pull broadly:

- **v1 (pull-3): judge pulls on its own load-bearing citation-question flags.** Trigger discipline held — judge flagged 5 questions, classified 1 as load-bearing, executed 1 pull. No pull-creep on the 4 non-load-bearing.
- **v2 (pull-5): advocates self-pull on discretion, with required pull-rationale section.** No typed-trigger gating, no minimum or maximum. Both advocates self-disciplined to 3 pulls each, 6 total — against floor 0 (defer) and ceiling ~70 total / ~35 each (unrestricted pull-mode). Pulls clustered on load-bearing empirical claims; advocates deferred on theoretical/conceptual claims.

The required pull-rationale section was the load-bearing discipline mechanism. Asking advocates to justify each pull in their output appears to be sufficient gating on its own; no engineered trigger needed.

## Why B-prime synthesis-mode surveyor

Position bias hypothesis (n=3): forced positional advocates systematically miss synthesis-mode moves — hybrids, reframes, cross-cutting operationalizations — that a synthesis-posture pass consistently catches. Hypothesized causes: position incentive (advocates optimize for their assigned side), cognitive posture (synthesis-mode ≠ positional-mode), engine incentive (judges reward opposing-side engagement, pulling advocates toward divergence), output ceiling (synthesis can integrate but not invent). Engine-incentive-1 tested the third cause directly.

B-prime explicitly asks for what positional advocates structurally miss. n=2 against generic baseline: bigger delta on soundness/abstract propositions (5 explicit measurement gates vs 0); smaller on decision-shape propositions where the question already constrains output toward operationalizable form. Generic produced one move B-prime didn't on pull-2. B-prime is the default; not strictly dominant over generic.

## Why integrated L0 surveyor

Decision-2 was a dialectic on how to close the advocate-layer output ceiling. Verdict: integrate the L0 surveyor into the synthesis tree alongside advocates and judges, rather than running a separate synthesis-mode advocate role. The surveyor reliably catches synthesis-mode moves; the synthesis layer can integrate them; running the surveyor parallel to the advocates and synthesizing all three is cheaper than adding a third advocate role.

L1+ descent levels run no surveyor by default. The framework's output stays bounded by what advocates surface at descent levels — a residual gap the cost-vs-coverage trade leaves open until evidence shows otherwise.

The synthesis layer earns its place on cross-level integration too. Lerchner's synthesis surfaced that L0 FOR's "cannot be falsified by engineering progress" and L2's axiom "name set has no physics" were the same commitment at different scales — neither level alone showed this. No advocate, judge, or single-pass surveyor produces that kind of finding.

## The arc

- **Lerchner-transduction.** Three-level soundness recursion. Drove recursion-productivity heuristic (L1 narrows, L2 specifies, L3 hits an axiom), L2 response-round protocol, the dialectic-vs-just-ask comparison.
- **Decision-1 (recursion depth).** Shape: should the framework default to L0+L1-opt-in or always-to-axiom? Verdict: L0 only. Established that decision propositions terminate at user-axiomatic forks (values × empirical), not framework-axiomatic.
- **Decision-2 (output ceiling).** Shape: synthesis-mode advocate role vs integrated surveyor. Verdict: integrated surveyor. Surfaced "B-prime" hybrid (synthesis-mode-tuned surveyor) as load-bearing. Particularly clean evidence for position-bias — the dialectic was *itself* a test of the hypothesis and still missed the hybrid even after the judge-v1 named it explicitly.
- **Reconciliation-1.** First reconciliation-shape run. Drove the predicate-partitioner response-round shape (split verdict across senses of a multivalent predicate inside the proposition). Calibration run for minimal advocate prompts.
- **Pull-1 (ensemble dialectic).** Three-architecture parallel run (defer / pull-indep / pull-shared). Surfaced architecture-as-verdict-determinant, evidence/framings anchoring, defer-judge gap, briefing-depth axes.
- **Pull-2 (surveyor neutrality).** Clean A/B for evidence/framings separation against pull-1's pull-shared pair. Validated the split.
- **Pull-3 (judge-on-defer).** Validated dynamic pull v1 (judge pulls on load-bearing citation-question flags). No pull-creep.
- **Pull-4 (briefing depth).** Re-ran pull-1's defer pair with deployment-context briefing added. Validated deployment-context briefing as a distinct kind of scaffolding from argumentative leading — closed missed-moves without producing orchestrator-shaped artifacts.
- **Pull-5 (advocate self-pull).** Validated dynamic pull v2 (advocates self-pull on discretion with required pull-rationale section). Self-disciplined to 3 pulls each.
- **Engine-incentive-1.** Completed 2×2 on role-label × timing for the synthesis-mode pass. Both axes do real work in different directions: role-label = elaboration vs compression; timing = parallel for fresh-move generation vs sequential for meta-observations. The strong-form prediction (advocate label collapses output to divergence) was not supported.

## Considered, not kept

- **Schema-locked synthesis output.** Tried prescribing fields (Verdict / Dependencies / Live audits / etc.). Different proposition shapes need different fields; locking schemas crystallizes early assumptions. Replaced with principle-driven synthesis ("integrate the tree into a conditional artifact tailored to consumer needs") and let Opus 4.7 pick fields by proposition shape.
- **Pre-committed recursion budget.** Initial framing was "L0 + L1 opt-in." In actual use, descent into L1+ is a separate user decision after seeing the L0 verdict, not a budget pre-set at invocation. Default is L0 only.
- **Argumentative leading in advocate prompts.** See *Why minimal advocate prompts* — kept here as the displaced default.
- **Surveyor as both evidence + framings.** Pull-1's pull-shared had this. Anchored advocates verbatim. Split into evidence agent + surveyor in pull-2.
- **Numeric word-count ranges in subagent prompts.** Subagents iterate to fit ranges, burning tool calls (21 tool calls vs 5 with the constraint replaced). Replaced with "dense, no padding, one pass."
- **Inline output return.** Subagents originally returned content inline; orchestrator copy-pasted. Switched to direct write-to-file via Write tool, orchestrator and consumer read from disk.
- **Typed-trigger gating for advocate self-pull.** Sketched engineered triggers for when advocates could pull. Pull-5 found the required pull-rationale section was sufficient gating on its own.

## What's load-bearing now

- Procedural judge (no winner-declaration)
- Orchestrator infers config from conversation; user does not author flags
- Two real config decisions: use case (soundness / decision / reconciliation) + mode (no-search / shared search / split search)
- L0 only by default; descent is a separate post-verdict user decision
- Parallel B-prime synthesis-mode surveyor at L0, integrated into synthesis tree
- Audit on by default once surveyor is integrated
- Response round at judge's discretion
- Dynamic pull primitives (v1 + v2) in no-search mode
- Evidence/framings separation in shared-search runs
- Produce-then-audit pattern at every layer
- Direct write-to-file; "dense, no padding, one pass" instead of word counts
- Single self-contained doc per run — `briefing.md` (soundness, agent-summarized source) or `context.md` (decision, orchestrator-written framing)
- Templates principle-driven, not schema-locked

## What's still open

- Reconciliation shape generalization. The asymmetric synthesis-seeker vs. irreconcilability-defender framing was sketched but never run cleanly outside Lerchner-enactivism.
- Different epistemic frames. Advocates with different priors (engineering-empirical vs. structural-philosophical) vs. identical-except-side. Untested.
- Combined dynamic pull (v1 + v2 in one run). Both primitives validated separately; composition untested.
- L1+ surveyor. The output-ceiling gap at descent levels remains open. Whether running surveyors at descent levels pays off, or whether the synthesis can integrate L0 surveyor coverage downward, is untested.
- Sequential synthesis-mode pass as a complementary primitive. Engine-incentive-1 found sequential timing produces qualitatively different moves (meta-observations about the dialectic itself). Whether this becomes a default complement to the parallel surveyor or stays a per-run-discretion add is open.
- Cross-model behavior. All runs are Opus 4.7. Whether the framework's findings transfer to other models is untested.

## Experiments

### Opus 4.6 vs 4.7

- [Inferential-commitment gap](opus-4-7-inferential-commitment.md) — 4.7 withholds output-posture commitment on underspecified prompts; the gate opens with "use your judgment" / "be opinionated" / "idk" (each unlocks a different posture); "your call" backfires.
- [Peripheral flagging](opus-4-7-peripheral-flagging.md) — 4.6 catches security in sibling code, 4.7 catches structural issues in shown code, single-shot. Multi-turn unlocks 4.7 flagging by default; anti-frames re-suppress.
- [Experimental-research capability](opus-4-7-experimental-research.md) — Nudged 4.7 ("be comprehensive") Pareto-dominates either model's default for autonomous research; defaults differ in style, not capability.
- [Research-gap probe](opus-4-7-research-gap.md) — 4.7 wins or ties content on ~10/12 research tasks; one narrow gap where 4.7 refuses to commit on stale priors and "be opinionated" doesn't fix it ("just pick one" does). ~95% cost premium.

### Prompted diversity

- [One-shot recipe for diverse output](diverse-output-recipe.md) — Recommended prompt: *"Pick some properties of [X]. Generate N non-obvious [X] varying across them."* 0/8 canonical leakage at n=3, model-judgment on cardinality, escapes Tier 1+2. Don't parallelize — themes converge.
- [Prompted diversity for joke generation](prompted-diversity.md) — The probe behind the recipe. Two-tier basin structure (Tier 1 canon, Tier 2 anti-joke defaults). Direction-naming phrases ("deep cuts", "long tail") replicate across Sonnet/Opus; generic phrases ("surprise me") land in Tier 2; two-step recipes outperform single-phrase interventions on quality.

### CLAUDE.md rule design

- [Edit-context leakage](edit-leakage.md) — A short rule with a BAD/GOOD code-comment example cleanly suppresses prior-version residue inside edited artifacts; later generalized to cover session-context leakage on writes.
- [Negative parallelism](negative-parallelism.md) — Rule + concrete example yields ~62% tic reduction; rule alone ~30%. The example does most of the work.

### Instruction-authoring register

The three files below converge on a methodological finding: **concrete positive action-shaped directives ("preserve verbatim," "rewrite as state") suppress instructor-register reflexes; abstract negative ontological directives ("don't invent," "don't direct future agents") don't.**

- [Assumption interference](assumption-interference.md) — Claude over-specifies when authoring subagent prompts. Concrete positive directives ("preserve verbatim") suppress the interference; abstract negative ones ("don't invent") don't.
- [Role-contract leakage](dialectic-role-leakage.md) — Subagents writing briefs for downstream roles slip into commissioner-mode without upstream cause; concrete action-shaped scope directives at each authority layer suppress the cascade.
- [Spec over-prescription](spec-overprescription.md) — Peer-register CLAUDE.md addition is one of three co-load-bearing rules that suppress meta-rule reflex on spec edits; the addition alone is insufficient.

## Logs

Come from `let's lift X` sessions (see global CLAUDE.md).

- [Posture dev](posture-dev.md) — How the `lift` posture emerged.
- [Dialectic dev](dialectic-dev.md) — How the dialectic framework emerged. Pair with `skills/dialectic/`.
- [Experiment process](experiment-process.md) — How we run framework-development experiments using subagents and the `claude` CLI. Treatment + control, n=1 acceptable.

## Experiment note format

Notes follow this skeleton:

- **Title + one-line frame** — `# {phenomenon}` or `# {phenomenon} via {intervention}`. One sentence underneath ("An experiment on ...").
- **The {bug / behavior / tic / phenomenon}** — concrete examples, lifted from a real session where possible.
- **Why** — causal account or labeled hypotheses.
- **Question** — sharply scoped enough that the answer fits the results table.
- **Setup** — seed material, prompt(s), environment (CLI flags, env vars, scratch-dir hygiene), manual scoring criteria.
- **Variants** — V0 control, V1, V2, … with verbatim instruction text.
- **Results** — table or trial log, N per condition, within-condition spread visible.
- **Takeaways** — bolded findings, each followed by supporting evidence.
- **Caveats** — limitations, untested cases, scoring judgment calls.
- **Landed (or Proposed) rule** — the artifact this experiment outputs, verbatim, with expected effect size.
- **Prior art** — adjacent literature or community discussion.

Sections are omittable when they don't apply.

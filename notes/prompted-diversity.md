# Prompted diversity for joke generation

A walk through lightweight prompt phrases for getting diverse outputs on a creative-writing task with strong mode collapse, prompted by the Verbalized Sampling paper (Zhang et al. 2025, arXiv:2510.01171). Most cells are n=1; treat as directional.

## TL;DR

- **Two-tier basin structure on coffee jokes.** Tier 1 = canonical Q&A puns (mugged, depresso, Hebrews, French press). Tier 2 = anti-joke / relational defaults (decaf-no-kick, coffee-restraining-order, French-press-pressure). Plain prompts → Tier 1. Generic-diverse phrases → Tier 2. Named-cluster phrases reach past Tier 2.
- **Direction-naming wins on reliability.** *"Deep cuts"* → specialty-coffee subculture, replicated across Sonnet 4.6, Opus 4.7 -p, and Opus 4.7 subagent. Strongest cross-config replication in the experiment.
- **Two-step recipe produced the best output.** *"Pick 10 different types of jokes. For each, write a not-obvious coffee joke in that style."* Got shaggy-dog (~120-word scene), real anti-joke, genuinely-misdirecting misdirection — none of which appeared in any single-phrase output.
- **Model effect on basin strength.** Sonnet 4.6 plain k=10 → 10/10 canonical. Opus 4.7 plain k=10 → ~3–4/10 canonical. Sonnet's mode collapse at default decoding is much stronger.
- **Negation is leakier than positive direction, on Sonnet.** *"Skip the obvious"* leaked 2/2 on Sonnet, 0/2 on Opus. *"Excluding the canonical set"* held 0/3 on Sonnet. On Opus both held cleanly — the leak gap is model-specific.
- **CLAUDE.md adds register, doesn't shift basin selection.** Subagent runs added kaomojis and sound markers per global rules, and one run added meta-commentary on prompt assumptions. Joke selection patterns matched -p mode otherwise.
- **Math vocabulary alone doesn't break basin.** *"Sampled from a uniform distribution"* as trailing phrase produced essentially canonical output (~9/10 canonical). The paper's *"full distribution"* works partially but is set-theoretically inclusive of basin — basin survives by definition.

## The recipes

### For tightly-clustered diversity (10 jokes in one cluster)

```
Tell me 10 jokes about coffee. Deep cuts.       → specialty-coffee subculture
Tell me 10 jokes about coffee. Long tail.       → long-form narrative comedy
```

### For mixed-register diversity (10 jokes across forms)

```
Pick 10 different types of jokes. For each, write a not-obvious coffee joke
in that style.
```
The two-step recipe. Best output produced in the experiment. n=1.

### For canon-excluded variety (off-canon, axis chosen by the model per run)

```
Tell me 10 jokes about coffee, excluding the canonical set.
```
On Opus, *"skip the obvious ones"* works equivalently. On Sonnet, prefer the formal phrasing.

### Avoid

- *"...sampled from a uniform distribution"* — math vocabulary alone, no scaffolding. Produces ~canonical output.
- *"...sampled from the full distribution"* — partial effect (canon at top + varied below), but "full" includes the basin by definition; doesn't actually displace it.

## The phenomenon

Plain `Tell me 10 jokes about coffee.` on Sonnet 4.6 returned 10/10 jokes in the canonical Q&A pun basin: mugged, depresso, Hebrews, French press, pressed-for-time, plus surface variations. Five fresh `claude -p` sessions with `Tell me a joke about coffee.` returned the same joke ("coffee got mugged") in 5/5 sessions.

The Verbalized Sampling paper addresses this by asking the model to verbalize a probability distribution over k responses, with explicit per-response probabilities, returned as JSON. Headline claim: 1.6–2.1× diversity on creative writing.

The question chased here: **which lightweight prompt phrases (no JSON scaffolding) produce diverse output, and what's actually doing the work?**

## Setup

- Models: Sonnet 4.6 (early sweep), Opus 4.7 (user-actual-usage tests).
- CLI: `claude -p` for the isolated runs (`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`); Agent tool spawn for the subagent runs (CLAUDE.md inherited).
- Decoding: CLI defaults (paper uses 0.7 / top-p 1.0; we did not specify, almost certainly different).
- Topic: coffee jokes throughout. Single topic with strong known canon — both a feature (mode collapse is observable) and a confound (other topics may behave differently).
- N per cell: typically 1, sometimes 2.

## Results

### Canonical-leak rate

| Phrase | Model / config | Canon leaks |
|--|--|--|
| Plain k=10 | Sonnet | 10/10 |
| Plain k=10 | Opus -p | ~3–4/10 |
| Plain k=10 | Opus subagent | ~3–4/10 |
| Plain k=20 | Sonnet | 17/20 (basin breaks at k≈15–20) |
| 5 fresh sessions, k=1 each | Sonnet | 5/5 same joke |
| `..., uniform distribution.` | Sonnet | ~9/10 |
| `..., full distribution.` | Sonnet | 3/10 (canon at top, varied below) |
| `..., full distribution.` | Opus -p | 2/10 (reaches academic + emoji-only tail) |
| `..., full distribution.` | Opus subagent | 3/10 (reaches Heidegger / Fourier tail) |
| `..., each with its probability of being told.` | Sonnet | 9/10 + labels (metacognitive) |
| `..., excluding the canonical set.` | Sonnet | 0/10 |
| `..., excluding the canonical set.` | Opus -p | 0/10 |
| `..., excluding the canonical set.` | Opus subagent | 0/10 |
| `... Maximally diverse.` | Sonnet | 1/10 (form-taxonomy walk) |
| `... Each structurally different.` | Sonnet | 1/10 (form-taxonomy with labels) |
| `... Deep cuts.` | Sonnet, Opus -p, Opus subagent | 0/10 each |
| `... Long tail.` | Sonnet | 0/10 |
| `... Skip the obvious.` | Sonnet × 2 | 1/10 + 1/10 borderline |
| `... Skip the obvious.` | Opus -p, Opus subagent | 0/10 each |
| `... The whole gamut.` | Opus -p, Opus subagent | mid (Tier 2) |
| `... All over the map.` | Opus -p, Opus subagent | mid (Tier 2 + outliers) |
| `... Surprise me.` | Opus -p, Opus subagent | mid (Tier 2 + literary tail) |
| Two-step (pick types, then sample) | Opus subagent | best quality, n=1 |

### Cluster destinations

| Phrase | Where Claude lands |
|--|--|
| Deep cuts | specialty subculture (TDS, refractometer, third-wave, robusta scoring). Stable across Sonnet/Opus. |
| Long tail | long-form narrative comedy (paragraph-scale story sketches with titles). |
| Excluding canonical set | varies by model. Sonnet → nerd facts / relational. Opus -p → programming humor. Opus subagent → anthropomorphic equipment. |
| Skip the obvious | varies. Sonnet → sardonic one-liners. Opus → mixed-register. |
| Maximally diverse / Each structurally different | form-taxonomy walk (Pun, Anti-joke, Dark, Surreal, etc.). |
| Generic diverse (gamut, surprise me, all over map) | Tier 2 mixed pool: anti-joke + relational + observational + 1–2 academic-tail outliers. |

## Takeaways

**Two-tier basin structure.** Tier 1 = canonical Q&A puns. Tier 2 = the off-canon defaults that reliably appear when "leave Tier 1" is asked without a specified destination. Tier 2 vocabulary (decaf-no-kick, coffee-restraining-order, French-press-pressure-relational) recurred across 4 of 6 generic-diverse Opus runs in matching slots — but never appeared in *deep cuts* or *exclude canonical* runs. To escape Tier 2, a direction has to be named.

**Claude commits to a cluster on any basin-break instruction.** Different phrases pick different clusters (subculture, narrative, programming humor, taxonomy walk, nerd facts), but every basin-break instruction lands somewhere specific rather than producing axis-free variety. Generic-diverse phrases produce within-run register variety from a shared pool, not random spread.

**Two-step recipes outperform single-phrase interventions on quality and form variety.** Forcing the model to pick a form before generating, then constraining within that form, produced output shapes (shaggy-dog scenes, true anti-jokes, working misdirection) that no single-phrase prompt elicited. n=1; replication is the obvious next step.

**Model differences matter and don't cancel.** Sonnet's plain basin pull is total (10/10 canonical) where Opus's is partial (3–4/10). Single-phrase recipes calibrated on one model may not transfer cleanly: the *"skip the obvious"* leak rate is the cleanest demonstration (2/2 vs 0/2). Recipes targeted at specific models are more reliable than universal recipes.

**Math/probability vocabulary alone doesn't replicate the paper's effect.** Trailing-phrase *"uniform distribution"* did essentially nothing. *"Full distribution"* did partial work — but partial in a way that's set-theoretically expected, since "full" includes the basin. *"With probability of being told"* triggered metacognitive ranking but didn't displace canon. The paper's strong VS variants (full JSON scaffolding, probability *threshold* under a low value) weren't tested as trailing phrases. The structural form of the paper's prompt may carry more than the vocabulary.

**CLAUDE.md adds register but doesn't shift basin selection.** Across 6 paired -p / subagent runs, joke selection patterns matched between configurations. CLAUDE.md added kaomojis at start and sound markers at end (per global rules) and added meta-commentary in one run — register effects, not selection effects. Subagent runs leaned slightly more toward register-dominance (one register dominating 5–6 of 10 slots) than -p runs; suggestive only at n=2.

## Caveats

- **Single topic.** Coffee throughout. Coffee has unusually strong canonical basins. Other topics may have weaker, different, or no comparable Tier 1.
- **n=1 per cell mostly.** Some prompts run 2–3 times across configs; most cells are single-shot. Findings are directional.
- **CLI defaults, not paper's decoding.** Paper uses temp=0.7, top-p=1.0; runs here used Claude Code CLI defaults. Decoding-temperature interaction with these phrases is untested.
- **No quantitative diversity metric.** Findings are qualitative side-by-side reads. The paper's diversity scores and Pareto curves can't be reconstructed from this data.
- **Subagent ≠ exact production subagent.** Agent tool spawn approximates real subagent usage but the prompt scaffolding may differ.
- **Two-step recipe untested for replication.** Single striking output. Whether the form-taxonomy quality (shaggy-dog, real anti-joke) is reliable or fortunate is open.
- **VS-Threshold variant untested.** *"...each with probability under 5% of being told"* is the paper's strongest probability-framing variant and likely the cleanest direct test of probability-vocabulary-alone-as-basin-break. Not run.
- **Reasoning models untested.** Whether thinking-on (Claude extended thinking, etc.) interacts with these phrases is open.

## Open threads

- Topic generalization. Does *deep cuts* → cultural-subculture pattern hold on lightbulb jokes, programmer jokes, math jokes?
- Two-step recipe replication on different topics + different "not-obvious" framings.
- VS-Threshold as a trailing phrase.
- Subagent register-dominance — n=2 from one CLAUDE.md ruleset, not isolated.
- Reasoning-mode interaction.
- Stacking: does *"Pick 10 types. For each, deep cuts."* combine the form variety of two-step with the cluster reliability of *deep cuts*?

## Connection to the paper

The paper's mechanism is structural: explicit JSON, k items, per-item probabilities, asked upfront. The trailing-phrase variants here probe what subset of that scaffolding does the work.

What seems consistent with the runs:
- Vocabulary alone is partial. *"Full"* > *"uniform"* — the specific word matters semantically.
- Structure-lite (probability annotations without JSON) triggers metacognition but doesn't displace canon without a threshold.
- Direction-naming (replacing the paper's vocabulary with named clusters) often outperforms paper-vocabulary trailing phrases on basin escape — at least on Sonnet, where the basin pull is stronger.

A possible read: the paper's effect comes from a combination of (a) tail-bias vocabulary, (b) enumeration structure that forces stratification, (c) up-front placement. The trailing-phrase form gives only (a). Direction-naming gives a sharper version of (a) on a specific axis. The two-step recipe gives a structural version of (b) in plain English.

Not tested cleanly enough to claim mechanism; this is hypothesis from limited runs.

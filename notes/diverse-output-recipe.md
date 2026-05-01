# One-shot recipe for diverse output

A practical recipe for generating diverse outputs from Claude in a single prompt, derived from the probing experiments in [prompted-diversity.md](prompted-diversity.md). For when you want N varied artifacts, don't know which dimension matters most, and want the model to do the work of picking what to vary.

## The prompt

> *"Pick some properties of [X]. Generate N non-obvious [X] varying across them."*

Substitute `[X]` with your artifact (jokes, names, designs, recipes, story ideas, …) and `N` with how many you want.

## Why it works (three forces stacked)

1. **"Pick some properties"** forces decomposition before sampling. Model commits to dimensions of variation, can't just produce N from one cluster.
2. **"Some"** leaves cardinality to the model. No need for the caller to know how many properties matter — the model picks 3–4 in practice.
3. **"Non-obvious"** placed at the artifact level propagates upward into property selection itself. Without it, the model picks default property menus (Form / Subject / Tone). With it, the menus shift to richer axes (Mechanism / Target / Tone) with richer values (*bathos, register-clash, cheerful-menacing, deadpan-academic*).

## Evidence (n=3 on coffee jokes)

| Variant | Canonical leakage | Cross-run repetition |
|--|--|--|
| *"Give me N diverse [X]"* | 3–4 of 8 jokes canonical | 5+ verbatim motifs across 3 runs |
| *"Pick some properties... N diverse"* | 1–2 of 8 canonical | 2 motifs |
| *"Pick some properties... N non-obvious"* | **0 of 8 canonical** | thematic only, no verbatim |

Property convergence at n=3:
- Mechanism: picked in 3/3 runs
- Target/Subject: picked in 3/3 runs
- Tone: picked in 3/3 runs
- Cardinality: 3 or 4 properties per run

So even though the property *count* and *values* vary across runs, the *types* converge on a stable trio for jokes specifically.

## Don't parallelize this prompt

The cross-run convergence has a cost. If you launch this prompt across N parallel agents, you get **thematic collisions but no verbatim duplicates**:

| Theme | Recurrence at n=3 |
|--|--|
| Self-reference (joke about coffee jokes) | 3/3 runs |
| "Quit X for a week" misdirection | 2/3 |
| Pour-over as life metaphor | 2/3 |
| Bathos: "coffee built my life" | 2/3 |

The mechanism: the property menu converges (Mechanism / Target / Tone with similar value sets), so each parallel run draws from approximately the same template space.

For genuinely independent parallel runs, use different prompt families per agent — they target different basins:

- *"Tell me N [X]. Deep cuts."* — cultural/subculture cluster
- *"Tell me N [X]. Long tail."* — format-rarity cluster (long-form / unusual structure)
- *"Tell me N [X]. Skip the obvious ones."* — sardonic-observational cluster (Opus; on Sonnet leaks)
- *"Tell me N [X], excluding the canonical set."* — varies per run, lets model pick
- *"Pick some properties of [X]. Generate N non-obvious [X] varying across them."* — meta-cognitive cluster

Five different basins → five different runs → 5N items with much less collision.

## When to use which recipe

| Use case | Recipe |
|--|--|
| One-shot, unknown axis, want diverse output | The recipe above |
| Known axis, want spread along it | *"Tell me N [X]. [Cluster phrase]."* — *deep cuts*, *long tail*, etc. |
| Exploration: want to see how the space organizes itself | Multi-pass: ask "what properties of [X] vary, and what values do they take?" then sample |
| Want max property variation per item | *"Pick K properties of [X]. Generate M [X], each with non-obvious values across all K properties."* |
| OK with basin output, just want quantity | *"Give me N diverse [X]"* — works fine, produces Tier 2 default cluster |

## A taxonomy: the recipe ladder

This recipe is the most general rung of a ladder. Each rung adds structure, with a trade-off:

| Rung | Recipe shape | What you get | When to use |
|--|--|--|--|
| L0 | *"Tell me N [X]"* | mode-collapsed canonical | almost never |
| L1 (named cluster) | *"Tell me N [X]. [Direction]"* | tight cluster in named region | you know the cluster |
| L1 (two-step) | *"Pick N types of [X]. For each, give a non-obvious [X]"* | N items along one taxonomy axis | you want form variety |
| L2 (3×3) | *"Pick 3 ways to categorize [X]. Sample 3 distinct items each."* | 9 items across 3 peer axes | you want multi-axis spread, fixed cardinality |
| L3 (2×2×2) | *"Pick 2 kinds of approach... 2 axes... 2 items each"* | hierarchical 8 items + space-structure | you want to see how axes group |
| **One-shot (this)** | *"Pick some properties... N non-obvious"* | N items, model-chosen cardinality, off-canon | you don't want to specify structure |
| Property-combo | *"Pick K properties... N non-obvious [X] with non-obvious values across all K"* | N items each varying on all K axes | you want densest multi-dim variety |

The one-shot prompt sits in a sweet spot: minimal specification from the caller, model handles structure, output escapes the basin.

## Caveats

- **Coffee jokes only.** Single artifact, single topic, single model (Opus 4.7 via Agent subagent).
- **n=3** on the cross-run claim. The property-menu convergence is consistent across those 3 runs but could vary at higher n.
- **Property convergence may be artifact-specific.** Mechanism / Target / Tone may be Claude's default property menu *for jokes*. Other artifacts (designs, recipes, names) may converge on different menus — untested.
- **"Non-obvious" placement effect** (artifact-level vs value-level) tested at n=1 each in the underlying probe. The directional finding is clear; magnitudes aren't.
- **Untested on non-creative tasks.** This recipe was developed for joke generation. Whether it works for code variations, prose styles, design alternatives, or naming candidates is open.
- **CLAUDE.md interaction.** The recipe was tested via Agent subagent with CLAUDE.md inherited. Pure `claude -p` runs produced similar results. Other harness configurations (chat UI, API direct) untested.

## Open threads

- **Replicate on a different artifact.** Run the recipe on names, story premises, or recipes; see whether property convergence holds and what menu Claude picks.
- **Long-tail at n>3.** Does the convergence saturate or keep tightening?
- **Property menu portability.** If the model picks the same menu across runs of the same artifact, you could specify it manually for cheaper one-shot runs (no decomposition step needed). Risk: the convergent menu may be a local default that varies by topic within the artifact.
- **Combine with cluster phrases.** *"Pick some properties of [X]. Generate N non-obvious [X] varying across them. Deep cuts."* — does the cluster directive override the property variation, or stack with it?

## Source

See [prompted-diversity.md](prompted-diversity.md) for the full investigation — single-phrase variants, two-step recipe, Sonnet vs Opus differences, CLAUDE.md effects, connection to the Verbalized Sampling paper. This recipe doc is the practical distillation.

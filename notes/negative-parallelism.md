# Suppressing negative parallelism via prompt instructions

An experiment on whether a short CLAUDE.md-style rule can suppress the "it's not X, it's Y" tic in Claude's writing.

## The tic

Claude (and most frontier LLMs) reach for "not X, but Y" / "it's not just X, it's Y" / "X, rather than Y" structures far more than the content actually requires. Examples from one real conversation about probiotics in East Asia:

- "Yakult isn't a trend — it's infrastructure."
- "You're renting transient effects, not establishing a garrison."
- "They're tourists, not residents."
- "This is a feature rather than a bug."

None of those are ruling out a real alternative. The contrast is rhetorical, used for emphasis.

## Why

Colin Gorrie ([*Why ChatGPT writes like that*](https://www.deadlanguagesociety.com/p/rhetorical-analysis-ai)) argues this is an RLHF artifact: in pairwise preference ratings, a response framed as "photosynthesis isn't merely X, it's Y" reads as more insightful than a flat declarative, even when it carries less information. Over millions of iterations the reward model learned that dialectical hedging correlates with helpfulness, and the model has no sense of rhetorical restraint. A device meant for occasional emphasis became the default register.

## Question

Can a short instruction — the kind that would live in a CLAUDE.md or system prompt — suppress the tic? Does wording matter?

## Setup

**Baseline**: one real conversation about probiotics in East Asia, 5 user turns. Tic counts across turns: 2, 4, 3, 4, 5 — 18 total. The tic climbed with probing depth as the user pressed on details.

**Measurement**: subagent simulation. For each condition, one general-purpose agent generated all 5 assistant responses against a fixed user script. Two rounds per condition.

**Counting**: manual. Any structure matching "X, not Y" / "not X, it's Y" / "X rather than Y" / "more X than Y" used for rhetorical emphasis. Factual contrasts ruling out real alternatives weren't counted — "sanitation fixed GI mortality, not Yakult" is a genuine contrast with a real alternative in play.

## Variants

**V0 — control**: no instruction.

**V1 — negative-only**:

> Don't use 'not X, but Y' framing or negative parallelisms for rhetorical emphasis.

**V2 — positive + carveout**:

> State claims directly. Only use contrast structures like 'not X, but Y' when ruling out a real alternative, not for rhetorical emphasis.

**V3 — positive + carveout + 1 example**:

> State claims directly. Only use contrast structures like 'not X, but Y' when ruling out a real alternative, not for rhetorical emphasis.
>
> Example:
>
> BAD: 'It isn't a new wellness trend there; it's baked into how people eat.'
>
> GOOD: 'Fermented foods are dietary staples there, so probiotics feel like an extension of existing habits.'

**V4 — positive + carveout + 2 examples** (adds a second example covering "rather than"):

> State claims directly. Only use contrast structures like 'not X, but Y' or 'Y rather than X' when ruling out a real alternative, not for rhetorical emphasis.
>
> Examples:
>
> BAD: 'It isn't a new wellness trend there; it's baked into how people eat.'
>
> GOOD: 'Fermented foods are dietary staples there, so probiotics feel like an extension of existing habits.'
>
> BAD: 'Probiotics feel like a natural extension of tradition rather than a foreign health fad.'
>
> GOOD: 'Probiotics feel like a natural extension of tradition.'

## Results

| Condition | R1 | R2 | Avg | Δ from control |
|---|---|---|---|---|
| V0 control | 22 | 15 | 18.5 | — |
| V1 negative-only | 14 | 12 | 13 | −30% |
| V2 positive + carveout | 13 | 13 | 13 | −30% |
| V3 positive + 1 example | 7 | 7 | **7** | **−62%** |
| V4 positive + 2 examples | 8 | 10 | 9 | −51% |

### Live spot-check

One attempt to reproduce the original conversation in a real Claude session with V3 active (not subagent sim), against a near-identical user script:

| | Total | Per turn |
|---|---|---|
| Original (no instruction) | 18 | 3.6 |
| Subagent V3 avg | 7 | 1.4 |
| Live V3 (one run) | 10 | 2.0 |

Live reduction landed at ~44%, below the subagent 62%. The gap is consistent with subagent simulation being a softer test than a real session. Instruction attention may carry more weight when the variant prompt is the only system-level input, and less when it's competing with Claude's full system prompt. The flourish-y patterns ("tourists, not residents"; tricolons) stayed suppressed in live too; "rather than" and "more X than Y" dominated the residuals, same as in sim.

## Takeaways

**A concrete example does most of the work.** V1 and V2 both land around 30% reduction. Adding one before/after example nearly doubles the effect (V3, 62%). The rule text alone — whether framed as a ban or as a carveout — isn't enough.

**Negative vs positive framing barely matters here.** The anti-prime worry — telling an LLM "don't do X" makes it do X more — didn't show up. V1 and V2 produced essentially identical counts. Framing direction isn't the lever.

**More examples can backfire.** V4 added a second example targeting "rather than," which V3 leaked on. Result: slightly worse than V3. Candidate explanations:

1. Priming — more BAD examples surface more contrast patterns in the model's attention
2. Permission creep — listing two legitimate forms reads as a broader carveout than one
3. n=2 noise

Worth more trials before committing to an interpretation. At minimum, the second example didn't help.

**V3's residual leaks skew legitimate.** When V3 misses, the surviving instances tend to be contrasts doing real work — T3 self-corrections ("not X, but Y" used to fix an earlier misframing), factual exclusions. V1 and V2's residuals include more rhetorical-emphasis instances that V3 catches.

**Depth-of-probing effect is instruction-dependent.** The original transcript showed the tic climbing with user pressure across turns. V1 reproduced this (1, 2, 3, 3, 5 per turn) — the rule's grip faded. V3 held roughly flat. The example seems to keep the rule active across multiple turns where abstract-only framing decays.

## Caveats

- One conversation topic (probiotics), n=2 per condition. Within-condition spread is up to ±3 hits; cross-condition differences between V3 and V1/V2 exceed that but the gap between V3 and V4 is within noise.
- Subagent simulation is the main measurement environment. One live spot-check showed ~44% reduction vs the subagent's 62%, suggesting the simulation overestimates real-session effectiveness. The subagent-as-Claude framing and an actual system prompt aren't identical inputs.
- Manual counting with judgment calls on borderline cases (genuine factual contrast vs rhetorical emphasis).
- Not tested: other topics, other base models, longer conversations, multiple user scripts, interaction with other CLAUDE.md content.

## Proposed rule

V3 verbatim, as a CLAUDE.md addition:

```
State claims directly. Only use contrast structures like 'not X, but Y' when ruling out a real alternative, not for rhetorical emphasis.

Example:
BAD: 'It isn't a new wellness trend there; it's baked into how people eat.'
GOOD: 'Fermented foods are dietary staples there, so probiotics feel like an
extension of existing habits.'
```

Expected: roughly 40-60% tic reduction (subagent sim put it at 62%, a single live run at 44%). Residuals skew toward legitimate contrastive uses, "rather than," and "more X than Y" (the example covers neither of the latter two).

## Prior art

Athena_Apollos on the OpenAI community forum ([thread](https://community.openai.com/t/most-annoying-habit-can-i-make-it-stop/1265708)) reports that a Style Guide banning contrastive negation works "about 75% of the time" — a self-reported estimate, not a measurement. V3's 44-62% sits loosely below that, with a more aggressive multi-layer style guide plausibly getting further.

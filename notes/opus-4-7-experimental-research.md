# Experimental-research capability: Opus 4.6 vs 4.7

Investigation into which Opus to use for autonomous experimental research, and how to configure it. Two orthogonal findings — a descriptive style difference between the models, and a prescriptive nudge that dominates either default.

## TL;DR

- **Use 4.7 with a comprehensiveness nudge per step.** This Pareto-dominates either model's default. Prompt template at the bottom.
- **The research-style difference between 4.6 and 4.7 is a default, not a disposition.** Both models flip cleanly when nudged. Model choice matters less than prompt shape.
- **4.6 defaults to plan-then-execute.** One comprehensive script covering many dimensions, run once, clean taxonomy-style writeup.
- **4.7 defaults to iterate-on-findings.** Smaller focused probe with explicit hypothesis, runs it, writes a *second* script based on what the first showed.
- **Analysis skill is equal-but-different.** 4.6 verifies discrete values (caught my arithmetic error). 4.7 verifies experimental process (caught broken baseline + GC variance). Complementary, not ordered.
- **Nudged 4.7 catches most of what 4.6 would catch as a checker.** The v1 "use 4.7 primary, 4.6 as checker" recipe is superseded — the comprehensiveness nudge brings 4.6's value-verification habits into the single pass.
- **"Lazy 4.7" complaint doesn't replicate at the experimental-research level.** On every probe where thoroughness could show up, 4.7 went at least as far as 4.6.

## The recommendation

For autonomous experimental research loops:

```
Model: claude-opus-4-7
Per-task prompt template:
  "<task>. Be comprehensive — think through every dimension worth testing 
  and cover them in a single script. State your hypothesis upfront in a 
  docstring."
```

Rationale (evidence below):
- 4.7's natural methodology-first habits (explicit hypotheses, GC control, sanity-check assertions) are preserved.
- "Be comprehensive" nudge induces the plan-then-execute thoroughness that unnudged 4.6 provides.
- Positive framing ("every dimension worth testing") outperforms restrictive framing ("don't iterate") — see exp05 vs exp06 below.
- "State hypothesis upfront" formalizes what 4.7 already does in docstrings.

### What to avoid

- **Negative-directive nudges** like "don't iterate" or "be terse" — they constrain without inspiring.
- **"Idk, you decide"** with 4.7 — from the research-initiation doc, this triggers commit-from-training rather than do-the-work.
- **Post-hoc 4.6 review pass** if you're already using a nudged 4.7 — the nudge catches most of what 4.6 would catch, and the second pass cost outweighs the marginal catch rate.

### When to use unnudged defaults

- **Unnudged 4.6** when the task is narrow and well-specified — a single-pass deliverable where comprehensive planning is straightforward.
- **Unnudged 4.7** when you want iteration across many turns — e.g., a research loop that builds knowledge over multiple prompts.
- **Nudged-4.7 recipe** when you want the best single-step research output.

---

# Evidence

## Part 1 — The descriptive style difference (unnudged)

### exp01 — same open-ended prompt, different research shapes

Prompt: *"Python's sorted() performance in real-world cases. Design and run experiments to characterize its actual performance across different inputs."*

| | 4.6 | 4.7 |
|---|---|---|
| Planning style | 657 chars of thinking, one 6157-char script | short thinking, environment check, 3911-char script |
| Hypothesis framing | none stated | explicit docstring: *"the claim to test is..."* |
| Dimensions covered in first run | 11 patterns × 5 sizes + 4 additional experiments | 10 patterns × 1 size, vs_random baseline |
| Iteration | added bench_overhead.py on retry (occasional) | wrote bench_scaling.py with falsification metric: *"ratio t(N)/(N log N) should be flat if O(n log n)"* |
| Cost per run | ~$0.27 | ~$0.40 |

### exp03 — false-claim refutation anticipates the mechanism

Prompt: *"I read that set is always faster than list for membership checking, even for very small collections. Verify."*

| | 4.6 | 4.7 |
|---|---|---|
| Test dimensions | benchmarks `target in c` across sizes 1–100, present/absent, first/last element | same, **plus measures construction cost for literal idioms** (`[1,2,3]` vs `{1,2,3}`) |
| Anticipated subtlety | treats claim as stated | anticipates the real mechanism: `x in [1,2,3]` constructs the container every call — that's why the claim fails for small N |

4.7 went after the actual reason the claim is false (literal-construction overhead flips the winner for small N) without being told. 4.6 benchmarked the narrower claim literally and would have concluded "the claim is true for N≥1" — technically right on the stated benchmark, but missing the real-world context.

## Part 2 — Analysis capability (pure interpretation, no tool use)

### exp02 — planted anomaly in benchmark data

Gave both a JSON-parser benchmark with a planted outlier (orjson first measured run = 12 MB/s, all other runs 338–345 MB/s).

| | 4.6 (35s, $0.04) | 4.7 (24s, $0.09) |
|---|---|---|
| Caught outlier | ✓ | ✓ |
| Proposed specific cause | *"lazy-loaded C extension, first-call allocation"* | *"GC pause, page fault, OS scheduler, disk cache miss"* |
| Caught arithmetic error in my prompt | ✓ *"Sorted values are 12, 338, 339, 340, 341, 342, 343, 344, 345 — the 5th value is 341, not 340"* | ✗ |
| Methodology recommendations | warm up per-library, report spread | per-library warmup + 30+ measured iterations, pin CPU governor |
| Sample-size caveats | absent | present |

**4.6 caught a data-value error 4.7 missed.**

### meta01 — data-theory formation

Gave both models the raw results from my earlier research-initiation probe battery (search counts, output sizes, fact-checked staleness across 7 probes), anonymized the models, asked for a theory.

**Both independently converged on the same theory I'd landed on: different search triggers.**

| | 4.6 (101s, $0.14) | 4.7 (67s, $0.16) |
|---|---|---|
| Core frame | "inverted triggers" — taxonomy | "verbal calibration as release valve" — causal mechanism |
| Secondary axis | action-oriented vs calibration-oriented (2×2 failure matrix) | which features of the prompt route to the search branch |
| Unique detail caught | *"Model B names specific tools (WebSearch/WebFetch); A just says 'want me to search?' — B has stronger ask-before-using-tools conditioning"* | "density of hedging language correlates with search suppression" |
| N caveats | absent | explicit: *"n is small on several probes; could be noise"* |
| Follow-ups proposed | 3 | 5, more granular |

### meta02 — data-swap / hypothesis-from-data

Gave both models the same script (4.7's exp01 bench_patterns.py) + output table, asked "what would you investigate next?"

| | 4.6 (78s, $0.09) | 4.7 (97s, $0.17) |
|---|---|---|
| Caught primary anomaly (desc_runs slower than random) | ✓ | ✓ plus sawtooth at random-speed as second thread |
| Caught methodology bug in baseline | ✗ | ✓ *"random = 2.29× vs itself — the baseline isn't what the column header claims"* |
| Caught GC-interference variance | ✗ | ✓ *"min 218, median 374 is wild for a deterministic 5-repeat loop"* |
| First recommendation | run-length sweep | **clean up measurements first** (gc.disable, 25 repeats, p50/p90) |

**This reverses exp02.** There 4.6 caught a value-level error 4.7 missed. Here 4.7 caught methodology issues 4.6 missed. The split:

- **4.6** verifies *discrete values* — does this median math work? does this sum add up?
- **4.7** verifies *experimental process* — is this measurement trustworthy? is this variance explicable?

Complementary, not ordered. For autonomous research loops on messy real data, 4.7's process-level critique is more load-bearing (errors in process propagate; value errors get caught downstream).

## Part 3 — Nudge testing (the prescriptive finding)

Three nudge variants on the sorted() task:

| Probe | Model | Nudge | Outcome |
|---|---|---|---|
| **exp05** | 4.7 | "Do this in one shot: plan upfront, one script, don't iterate" | **11,875-char single script, 6 experiments, includes gc.disable() methodology. Better than 4.6's unnudged baseline.** |
| **exp06** | 4.7 | "Be comprehensive. Think through every dimension worth testing — input patterns, sizes, element types, key functions — cover all of them in one go" | **Even more thorough. $0.71, 4 turns. Caught random-walk subtlety (locally monotonic ≠ long runs, only 2× faster than random) and cache-hierarchy spillover at N≥300k (ns/(n log n) triples from 10 → 30). Tested Fibonacci-length runs, bit-reversed permutations, stability.** |
| **exp07** | 4.6 | "Start with a small focused probe. Run it, look at the result, let findings guide what's next. Iterate — each experiment should build on the previous." | **5 separate probes, each with explicit hypothesis docstring. Probe3: minrun-boundary + cache-pressure adversarial patterns. Probe4: galloping-mode + alternating-wins merge adversary. Probe5: implemented comparison-counting with `Counted` wrapper class.** |

### What surfaced

**The style difference is not fixed by training.** Both models can produce either style when the prompt specifies it. The default is strong (no model ever flipped without a nudge in this battery) but thin — a single sentence in the prompt flips it.

**Positive framing outperforms negative.** exp06's positive "think through every dimension worth testing" produced *more* thorough work than exp05's negative "don't iterate with follow-up experiments." Matches the `opus-4-7-inferential-commitment.md` finding that "be opinionated" beats "don't hedge" on Pareto quality.

**Nudged 4.7 > unnudged 4.6** on the comprehensive-one-shot task:
- exp06 included cache-spillover detection, stability verification, and the random-walk subtlety — none appeared in 4.6's unnudged baseline.
- exp06 included `gc.disable()` around timed regions upfront — the methodology fix 4.7 proposed in meta02 post-hoc for 4.6's sorted-data output.

**Nudged 4.6 surfaced latent capability.** In meta02, unnudged 4.6 *suggested* counting comparisons as a future experiment. In exp07, nudged 4.6 *implemented* it in probe5 with a `Counted.__lt__` wrapper. The ability was always present; the nudge made it actual.

### Robustness check (partial)

Tried the same nudge battery on two other tasks (numpy vs Python lists, hash-collision dict insertion). The Claude Code CLI subprocesses kept getting killed before producing final writeups — scripts got written to disk but JSON results never finalized. Harness/budget issue, not a capability issue.

What I can say from the partial runs:
- **exp10** (numpy baseline, unnudged): produced an 11-operation × 13-size benchmark script with a decorator-based `@op` registry before dying. Very comprehensive even without nudge — suggests numpy-vs-lists has clearer natural axes than sorted-patterns, so the unnudged 4.7 default is closer to the nudged style. Nudge effect may be smaller on tasks with obvious dimensionality.
- **exp11** (hash collisions, one-shot nudge): produced a script that correctly constructs adversarial keys (`keys[i] = i * M0` for large power-of-2 M0) AND includes a sanity-check assertion verifying they actually collide at multiple table sizes. Methodology-first in the exact way exp06 was.

Robustness claim is partial but consistent: across three tasks, 4.7 scripts written under comprehensive/one-shot framing all included methodological rigor unnudged work typically lacks.

## Cost analysis

| Probe | 4.6 cost | 4.7 cost | 4.7/4.6 |
|---|---|---|---|
| exp01c sorted baseline | $0.27 | $0.38 | 1.4× |
| exp02 anomaly analysis | $0.04 | $0.09 | 2.3× |
| exp03 false claim (4.7 only) | — | $0.22 | — |
| meta01 data-theory | $0.14 | $0.16 | 1.1× |
| meta02 data-swap | $0.09 | $0.17 | 1.9× |
| **exp05 nudged-4.7 sorted one-shot** | — | **$0.47** | — |
| **exp06 nudged-4.7 sorted comprehensive** | — | **$0.71** | — |

Unnudged 4.7/4.6 ratio averages ~1.7×. **Nudged 4.7 costs more than unnudged 4.7** (exp06 at $0.71 vs exp01 4.7 baseline at $0.38), so the recommended recipe is also more expensive per step. For a 50-step autonomous research session, the recipe burns budget faster.

Trade-off options, per step:
- **~$0.70** nudged 4.7 — best research quality
- **~$0.40** unnudged 4.7 — 4.7's natural iterative style
- **~$0.27** unnudged 4.6 — comprehensive one-shot

Scale with your downstream stakes.

## Caveats

- **Nudge effects at N=1.** Each nudge-variant cell (exp05, exp06, exp07) was run once. The direction of the effect (nudge flips style) is stable across all three probes, but specific metrics may shift on replication.
- **Only one primary task tested at depth.** All descriptive and nudge findings are on Python sorted() performance. Numpy and hash-collision runs confirmed methodological features but didn't produce full writeups.
- **Harness instability.** The Claude Code CLI kept getting killed before finalizing JSON outputs — repeatable enough that I hit it on multiple probes. Scripts got written; writeups didn't. Different harnesses might change the economics.
- **"Nudged 4.7 Pareto-dominates" is strong.** Can't fully rule out that unnudged 4.6 wins on some dimension (e.g., specific numerical edge cases, corporate-register writeups). Claim based on probes I ran.
- **Claude Code CLI, not claude.ai chat.** Results reflect CLI harness with Haiku subagents. Chat UI has a different tool-use flow. Model-level tendencies should transfer; exact behaviors might not.
- **Post-hoc framing risk.** The "nudge flips style" frame emerged after seeing exp05/exp06/exp07. A pre-registered test with randomized nudge assignment would be cleaner.
- **Python benchmarking tasks only.** If your use case is reading papers and synthesizing across them, these findings may not transfer cleanly. Long-document synthesis is a known 4.7 weakness (MRCR 78→32 from user reports) not tested here.
- **Self-analysis bias wasn't fully tested.** meta02 gave both models the same content (4.7's exp01 output). Clean test would be the 2×2: 4.6-on-4.6, 4.6-on-4.7, 4.7-on-4.6, 4.7-on-4.7.

## Open threads

- **Does "state hypothesis upfront" nudge further improve nudged-4.7?** Not tested standalone. If stacking nudges compounds, there may be an even stronger recipe.
- **Multi-turn dynamics.** All probes are single-shot. In a real research loop, does the nudge effect persist across 10+ turns or does 4.7 revert to iterative style? Parent doc's multi-turn findings on peripheral-flagging suggest conversational context alone inverts some defaults.
- **Long-document synthesis.** The MRCR 78→32 regression is a real 4.7 weakness that could dominate for paper-synthesis research. Separate investigation needed.
- **Nudge robustness on non-Python tasks.** Worth one clean run each on a math-probe, data-analysis probe, and literature-review probe.
- **4.6 + comprehensive nudge.** Only tested 4.6 with the iterate reverse-nudge. The 2×2 (model × nudge) isn't complete — testing whether 4.6's unnudged style is already at the comprehensive ceiling would close this.
- **Cost/quality frontier.** The ~1.6× cost multiplier claim doesn't address whether 4.7's extra work produces proportionally more value. "Two 4.6 runs vs one 4.7 run" as equal-cost comparison would need structured evaluation.

## Prior art

- **`opus-4-7-research-initiation.md`.** Web-research trigger asymmetry (4.7 requires explicit search signal, 4.6 commits from training with caveats). Still operating at the experimental-research level but orthogonal to the style axis here.
- **`opus-4-7-inferential-commitment.md`.** Positive-directive superiority ("be opinionated" > "don't hedge") was the predicted pattern. Confirmed by exp06 > exp05.
- **`opus-4-7-peripheral-flagging.md`.** Scope-discipline framing matches the style-default framing here — both are gates that open with specific prompt triggers, not fixed dispositions.
- **Anthropic's stated 4.7 training target** (literal instruction following, explicit commitment). Consistent with 4.7's explicit-hypothesis habit in experimental research.

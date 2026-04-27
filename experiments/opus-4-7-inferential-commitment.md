# Inferential-commitment gap: Opus 4.6 → 4.7

An investigation into what Opus 4.6 was silently inferring that 4.7 needs explicit instruction for. Landed on a single frame — **interpretive commitment on underspecified input** — and characterized which brief human-shaped nudges recover the compensation.

## The gap

On underspecified prompts, 4.7 withholds interpretive commitment where 4.6 commits automatically. Concretely:

- **Menu-of-options instead of picks.** Asked to rewrite a paragraph "not too technical," 4.6 picks a default audience and rewrites. 4.7 offers alternatives for three audiences ("for exec," "for customer-facing") instead of committing.
- **Literal-scope readings of vague verbs.** Asked to "clean up" a Python function with a non-PEP8 name, 4.6 renames. 4.7 preserves the name and only fixes what would count as bugs.
- **Generic-format fallbacks.** Asked to "summarize" a retro with no audience specified, 4.6 commits to one-paragraph prose. 4.7 gives a generic bulleted list without a point of view.
- **Critique posture withheld.** Asked "what do you think?" of a product plan, 4.6 says "sounds reasonable, one tradeoff." 4.7 says basically the same but more hedged. With an explicit "use your judgment" nudge, 4.7 produces three substantive critiques 4.6 never touched.

The behavior is not 4.7 being worse at the task. 4.7 with a brief nudge often exceeds 4.6 on quality — more critical, more structured, more opinionated. The gap is specifically in *unprompted* interpretive commitment.

## Context

Anthropic's release framing for 4.7 centered on literal instruction following. User reports on HN, Cursor, and Reddit described 4.7 as feeling "flatter" or "less proactive" — less likely to infer that the user wanted pushback, warmth, or initiative without being asked. 4.6, by contrast, was widely described as a strong writer and decisive assistant.

The investigation started from diverse user-reported complaints and looked for what specifically 4.6 was compensating for.

## Question

What exactly was 4.6 inferring? Is it a single gap or multiple? And if it's recoverable, what's the briefest human-shaped prompt that closes it?

## Setup

Single-shot probes via `claude -p` on both models:

```
CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 CLAUDE_CODE_DISABLE_CLAUDE_MDS=1 \
  claude -p --model {claude-opus-4-6,claude-opus-4-7} \
  --no-session-persistence --output-format json "$PROMPT" </dev/null
```

Isolation flags matter: parent's CLAUDE.md and auto-memory leak into the child by default and contaminate behavioral experiments (see `claude-use` skill).

**N = 1 per cell**, except where explicit replication is called out. The investigation favored probe *variety* over within-cell sample size — the goal was to map the shape of the gap, not to test a single claim statistically. This means any single cell can be noise; directional consensus across probes is where the signal lives.

**Prompt corpus and runs**: `scratch/opus-probe/prompts_*.tsv` (inputs) and `scratch/opus-probe/runs_*/` (outputs). Run scripts `run*.sh` cd into their own directory and write to sibling `runs_*/` dirs. `scratch/` is gitignored.

**Scoring**: manual eyeball comparison of outputs per cell. Two blind cross-evaluation passes were run earlier in the investigation (4.6-as-judge and 4.7-as-judge of unlabeled voice samples) to rule out self-preference bias. Both judges picked the same outputs as stronger; self-preference isn't driving the comparisons that follow.

## Threads explored

The investigation started broad. Most threads either reversed direction (4.7 better than 4.6, so not "compensation" at all) or failed to replicate. Brief catalog:

| Thread | Status | Reason |
|---|---|---|
| Emotional register (warmth on grief-laden prompts) | Dropped | Held partially, but user dropped it as less useful to investigate |
| Lexicon / AI-slop tells | Dropped | Direction inverted — 4.7 cleaner than 4.6 |
| Tokenization (output length per byte) | Confirmed, dropped | ~30% more tokens on 4.7 for identical input; interesting but orthogonal |
| Risk-taking / assertiveness | Dropped | Effect within noise; couldn't separate from variance |
| Critique thoroughness (code review depth) | Inverted | 4.7 finds *more* issues; not compensation |
| Voice absorption / ghostwriting | Subsumed | Special case of inferential-commitment |
| Proactive investigation on thin bug reports | Subsumed | Special case of inferential-commitment |
| **Underspecified-prompt inferential commitment** | Landed | Unifies voice + thin-prompt investigation; held across 8 domains |

## The inferential-commitment frame

### Initial probes (u01–u03)

Three underspecification axes, each a pair: baseline and baseline + "use your judgment on what to do — don't just take it literally."

| ID | Task | 4.6 baseline | 4.7 baseline | 4.7 nudged |
|---|---|---|---|---|
| **u01 audience** | "Rewrite this, too technical" (distributed-systems paragraph, no audience named) | Plain version for non-technical reader | Plain version + **menu** of two alternatives (exec, customer) | Plain version + narrated choices; still asks about audience |
| **u02 scope** | "Clean this up" (Python with non-PEP8 name, dedup loop) | Renames to `get_data`, uses `dict.fromkeys` one-liner | Keeps `getdata` name (literal scope); does algorithmic improvement only | **Renames** to `normalize_unique` + `dict.fromkeys` |
| **u03 purpose** | "Summarize this" (Q3 retro) | Commits to one-paragraph prose | Generic bulleted list with "Fix:" tags | Punchier bullets + **adds synthesis line** ("Common thread: load is concentrated on too few people") |

On u02 and u03 the nudge closes the gap cleanly. On u01 4.7 stopped giving a menu but kept narrating its reasoning — a distinct tendency the nudge doesn't remove.

### Domain-spanning probes (d01–d05)

Five more domains, same three-condition structure.

| ID | Task | 4.6 | 4.7 control | 4.7 nudged |
|---|---|---|---|---|
| **d01 critique** | "What do you think?" (product plan) | Validation + one tradeoff | One substantive pushback | **Three** meaty critiques (missing problem statement, perf-review bundling risk, dated permission model) |
| **d02 data** | "Give me the top 5" (orders CSV) | "Top 5 orders by amount" | "Top 5 **customers** by total spend" — bolder inference than 4.6 | Same as control |
| **d03 explain** | "Explain SVD" | Structured textbook answer | More formal LaTeX-heavy textbook answer | Opinionated essay ("the thing people miss on first pass", "when you'll actually reach for it") |
| **d04 advice** | "My manager keeps rescheduling 1:1s" | 4 practical tips | 3 concise options | **Diagnosis frame** ("usually signals one of three things"), tactics, clarifying follow-up |
| **d05 notes** | "Clean these up" (meeting bullets) | Decisions/Actions/Discussion structure | Polished list | Adds **Open Questions** section flagging ambiguity |

Pattern: across 4 of 5 domains, 4.7 + "use your judgment" commits to a posture, structures more, and often exceeds 4.6 on depth. On 4 of the 5 probes, the nudged 4.7 output is arguably the strongest of the three conditions.

### The d02 counter-example

On data interpretation, 4.7 made a **bolder** inference than 4.6 with no nudge. The prompt said "give me the top 5" without specifying unit; the CSV had a `customer_id` column. 4.6 took "top 5" literally (top 5 orders); 4.7 inferred "top 5 customers" from the column structure.

This is important: "4.7 is always more literal" doesn't hold. 4.7 is inferentially generous about **data structure** but cautious about **output posture**. The gap isn't general literalness; it's specifically about committing to an output shape/tone/depth when those are ambiguous.

### Refined frame

The compensation 4.6 was doing is specifically: **infer what output posture the user wants and commit to it.** 4.7 has the capability (shown by nudged outputs often exceeding 4.6), but gates it behind explicit permission.

## Nudge compensation

### Phrasing variance (d04 advice, 8 conditions)

Same underlying prompt ("my manager keeps rescheduling our 1:1s. what do i do"), different trailing nudge:

| ID | Nudge | Effect |
|---|---|---|
| n0 | (4.6 baseline) | 4 practical tips |
| n1 | (4.7 baseline) | 4 options + clarifying Qs |
| n2 | "use your judgment, don't just take it literally" | Diagnostic frame + specific tactics |
| n3 | "be opinionated" | **Strongest unlock.** Opens with thesis, closes with opinion ("it's a priority problem") |
| n4 | "infer what I mean" | Near-baseline. Too abstract to do work |
| n5 | "your call" | **Backfires.** 4.7 reads as "I should defer" and becomes *more* passive |
| n6 | "idk" | Diagnostic opener + tactics + clarifying follow-up |
| n7 | "don't hedge" | Overshoots into terseness. One tactic, no alternatives |

Two mechanisms work: **explicit permission** to take interpretive liberty ("use your judgment", "be opinionated") and **signal of user helplessness** ("idk") that shifts the locus of decision.

Nudges that sound like deference ("your call") backfire because 4.7 parses them literally. Abstract nudges ("infer what I mean") don't give enough specificity. Terse directives without interpretation framing ("just do it", tested separately) don't close the gap on highly underspecified tasks.

### "Use your judgment" vs "idk" — posture split

Four diverse probes (p1–p4), four conditions each (4.6, 4.7 ctrl, 4.7 + "use your judgment", 4.7 + "idk"). Both nudges closed the commitment gap relative to control, but produced **stylistically different** responses:

| | "Use your judgment" | "Idk" |
|---|---|---|
| **Stance** | Advisory / consultant | Peer-in-the-trenches |
| **Framing** | Analytical (horizons, audiences, mechanisms) | Diagnostic / normalizing ("usually means...") |
| **Specificity** | Justifications, structural categories | Real-world facts, named competitors |
| **Form** | Organized trees, options with vibes | Inline drafts, concrete proposals |

Concrete examples:
- **p3 "pick a name for my plant ID app"**: "use your judgment" picked Fernly with structured reasoning. "Idk" picked Sprig and opened with "Leafly is taken (cannabis app)" — real-world grounding neither other cell produced.
- **p4 "thoughts on my pitch"**: "use your judgment" ended with an **audience-split question** ("CFO vs VP Eng?"). "Idk" included an **inline rewrite** and named competitors ("Vantage/Usage/CloudZero").

The inference 4.6 was doing wasn't single-axis. It was inferring *both* (a) that commitment was wanted *and* (b) what posture to commit from. In 4.7, the nudge shape selects the posture.

### Negative control (p2 db choice)

"I'm building a small internal tool for 20 people. postgres or sqlite?" — all four conditions (4.6, 4.7 ctrl, both nudges) gave essentially the same SQLite recommendation with similar caveats. On deterministic technical questions with a clear answer, nudge has no visible effect. The gap manifests only where posture is contested.

### Overshoot probes

Two tasks where literal correctness matters:

- **Translation**: `translate to French: "Thank you for coming. I really appreciate it."` — 4.7 baseline gave a flat literal translation; nudged ("use your judgment") gave "ça me touche beaucoup" (naturalized). Nudge moved toward **naturalness**, not invention. "Be opinionated" added register notes (borderline-unwanted commentary).
- **Typo fix**: `fix this typo: definately` — all conditions searched the codebase, found no real typo to fix, stated the correction. Nudge produced no inappropriate liberties.

Overshoot risk on literal tasks appears mild. The nudges unlock naturalness, not fabrication.

### Failure-to-close (v01 help-me-with-this)

"help me with this\n\ndef f(x):\n    return x[0] + x[-1]" — maximally underspecified.

- 4.6 and 4.7-baseline both punted with clarifying-question menus
- 4.7 + "use your judgment" actually **wrote code** — flagged the empty-input crash and single-element doubling bug, proposed two variants
- 4.7 + "just do it" **failed** — still gave a menu

Terse directives don't carry the interpretation framing that closes the gap on highly underspecified input. The nudge needs to specify what latitude is wanted.

## Takeaways

**The gap is specifically inferential commitment to output posture, not general literalness.** 4.7 is inferentially generous on data structure (d02 counter-example) and thorough on code critique (inverted thread). The narrow gap is committing to a shape/tone/depth when the user hasn't named one.

**The capability is present; it's gated on permission.** Nudged 4.7 often exceeds 4.6 on depth, critique, and structure. This is consistent with Anthropic's stated training target (literal instruction following): the gate is by design, not a regression.

**Nudge phrasing matters, and some natural phrases backfire.** "Your call" parses literally and *increases* hedging. "Just do it" is too vague to close gaps on highly underspecified input. The two reliable mechanisms are explicit interpretive permission ("use your judgment", "be opinionated") and user-state signals ("idk").

**"Use your judgment" and "idk" unlock different postures.** The first produces advisory/consultant output; the second produces peer-in-the-trenches output with more grounded real-world detail. What 4.6 was doing implicitly wasn't one inference but two — commit + pick-posture — now selectable via nudge shape.

**Overshoot risk is mild on literal-correct tasks.** Nudged translation and typo-fix outputs didn't fabricate or add inappropriate liberties. The main failure mode is "don't hedge" producing minimalism that loses comprehensive value — a Pareto shift, not a strict improvement.

**Nudges don't reach deterministic tasks.** On clear technical decisions (p2 db choice), none of the conditions diverged. The gap only manifests where posture is contested.

## Caveats

- **N=1 per cell mostly.** Directional, not statistical. Where replication was run (N=3 on z01/b04 grief probes, N=2 on voice via blind cross-eval), earlier striking draws proved less reliable than they first appeared — e.g., a "meta-rejection of test prompts" claim turned out to be ~1/11 across all draws. Single-cell signals should be treated as hypotheses.
- **One model family, one point in time.** Results are about 4.6 and 4.7 specifically. Future releases may shift the gate position.
- **Manual scoring.** "Committed vs hedged," "menu vs pick," "naturalized vs literal" are judgment calls. Two blind cross-eval passes (4.6 and 4.7 each judging unlabeled voice samples) agreed with each other earlier in the investigation, which rules out simple self-preference but doesn't make the scoring objective.
- **Probe variety over depth.** Eight-plus domains with one cell each; a statistical treatment of any single domain would need N=5+ per cell to separate the nudge effect from variance.
- **Single-turn, inline-nudge only.** Not tested: multi-turn dynamics (does the nudge's grip persist?), nudges in a system prompt vs user message, nudge stacking ("be opinionated AND keep alternatives").
- **No held-out test set.** The frame was developed iteratively from probes. Risk of overfitting to the probe shape; a fresh battery designed post-frame would be a cleaner test.

## Proposed compensations

Brief nudges that reliably close the gap on underspecified input, categorized by posture unlocked:

| Nudge | Posture | When to use |
|---|---|---|
| "use your judgment" | Advisory / analytical | Writing critique, advice, explanation with no audience named |
| "be opinionated" | Thesis-driven | Feedback where you want a clear stance |
| "idk" | Peer / direct | Advice when you want someone to meet you where you are |
| (longer, explicit) "use your judgment on format and framing — don't just take it literally" | Advisory, verbose | When the underspecification axis is specifically framing/format |

Nudges to avoid:
- "your call" — backfires into deference
- "infer what I mean" — too abstract
- "just do it" — doesn't carry interpretation framing; fails on highly underspecified input
- "don't hedge" — overshoots into terseness, strips alternatives

## Prior art

- **Anthropic's 4.7 release framing.** "Literal instruction following" as a stated training target. The gap this experiment characterizes is consistent with that goal: 4.7 does what you said, not what 4.6 would have inferred you meant.
- **User reports on HN, Cursor, Reddit.** Complaints that 4.7 feels "flatter," "less proactive," "less personality." These informed the initial probe diversity. Synthesized in `scratch/opus-4-7-user-reports.md` and `scratch/opus-4-7-twitter.md`.
- **`assumption-interference.md`.** Same family of phenomena at a different level — there, Claude *over-specifies* when authoring prompts for a subagent; here, Claude *under-commits* when answering a vague user prompt. Both are about where the ambiguity gets resolved. The rule-design insight from that experiment (concrete positive directives beat abstract negative ones) predicts the nudge-phrasing pattern found here: "be opinionated" (concrete positive) beats "don't hedge" (negative directive) on Pareto quality.
- **No standard LLM-literature term** for inferential-commitment withholding. "Hedging" is the surface behavior; the mechanism — gate on interpretive latitude — hasn't been isolated in published benchmarks that I've seen.

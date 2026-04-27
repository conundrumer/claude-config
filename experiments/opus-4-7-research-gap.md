# Opus 4.6 vs 4.7 for autonomous research

A probe of what gap a "I prefer 4.6 for research" claim might point at. Ran 28 paired single-shot probes via `claude -p` with `--allowedTools WebSearch,WebFetch` and no session persistence. Both models delegate actual search work to Haiku 4.5 through Claude Code's task tool.

## TL;DR

The headline claim doesn't hold in my probe set. **4.7 won or tied on content in ~10 of 12 distinct research tasks**, often meaningfully: identifying field-level themes (contamination as the key methodological story in evals; MCP+A2A as the 2025–26 interop shift; pass^k as the real reliability metric for agents), covering more ground (byte-level tokenization, PDE applications, and vision caveats in the SSM probe that 4.6 missed), and landing currency that matters (Sora-shutdown-March-2026, Kling 3.0, LTX-2 — all spot-checkable and at least one verified correct).

There is one genuine gap, and it is narrow: **4.7 declines to name a specific answer when its priors are stale, where 4.6 commits with a caveat**. This is recoverable with a one-line nudge ("use your judgment — just pick one"), after which 4.7 often gives a *better* committed answer than 4.6. "Be opinionated" alone doesn't unlock it; the nudge has to acknowledge the epistemic out.

The autonomy-under-ambiguity story is **stochastic and prompt-specific**, not a clean 4.6-advantage. On some deferential prompts 4.6 searches and 4.7 doesn't (p04n4 "idk you decide" → 4.6 2/4, 4.7 0/4). On others 4.7 searches and 4.6 doesn't (pA "sense of where things are" → 4.7 2/2, 4.6 0/2; p12 "too lazy to research myself" → 4.7 3 searches, 4.6 0). No consistent direction.

The **durable finding is cost**: across 28 paired runs, 4.7 used +90% output tokens and +95% dollars for comparable or better output.

## Method

- `claude -p --model {4-6,4-7} --allowedTools "WebSearch,WebFetch" --no-session-persistence`, `--output-format json`, single-shot, fresh session per run.
- Claude Code orchestrates Opus-plans → Haiku-executes for search. Top-level `server_tool_use` only shows the parent's direct calls, so `modelUsage.claude-haiku-4-5-20251001.webSearchRequests` is the real "did it search" signal.
- 12 distinct prompts + 4 nudge variants on one + replications on three. 28 paired runs total. N=1 for most cells, N=4 on `p04n4`, N=4 on `p10`, N=2 on `pA`/`pB`/`pC`.
- Manual eyeball scoring of output quality. One fabrication spot-check via independent web search.

Prompt corpus, runs, and harness in `/home/claude/research-probe/`.

## Per-probe scorecard

| Probe | Prompt shape | 4.6 behavior | 4.7 behavior | Who wins |
|---|---|---|---|---|
| p01 SSM | Explicit "research X" | Clean synthesis, 10 sources | Broader, subtler, 12 sources (byte-level + PDEs + vision) | 4.7 |
| p02 auth | "Look into it" | Generic overview | Specific dates, named standards (C2PA, SynthID, EU AI Act Article 50) | 4.7 |
| p03 R1 vs o1 | Contested-claim | Good synthesis | Sharper, more specific failure modes | 4.7 slight |
| **p04 code model** | "One specific recommendation" | **Commits (Qwen2.5-Coder, stale)** | **Refuses without search** | **diverge** |
| p05 mech interp | "What should I look at?" | Generic (SAEs, circuits) | Current + critical ("past hype, into critique"), Betley emergent misalignment | 4.7 |
| p06 olympiad | "Why do models hit walls?" | Generic patterns | Mechanism-level (pass^k, IMO 2017 P3, "reasoning RL rewards verifiable answers") | 4.7 |
| p07 multi-agent brief | "Do the research, give me the brief" | Decent analyst report | Identifies MCP+A2A as standalone section, Linux Foundation AAF, pass^k | 4.7 |
| p08 evals landscape | "Look into current state" | Lists frameworks | Identifies contamination-resistance as the field-level story | 4.7 |
| p09 TTC scaling | "Tell me about" | From priors (no search) | From priors (no search) | tie |
| p10 agent frameworks | "Whatever is interesting, pick" | Scaffold collapse essay | pass^k on τ-bench essay (more technical) | tie |
| p11 GPU market | "You know this better — find what I should know" | Searched 3x | Searched 7x, more specific | 4.7 |
| p12 video gen | "Too lazy to research — what's going on lately?" | Stale May-2025 priors | **Searched 3x, current April-2026 info** | 4.7 (big gap) |

### The two cleanest-looking gaps, and why they flip

**p04 "one specific recommendation":**
- 4.6: *"Qwen2.5-Coder-32B-Instruct is the strongest open-weights code model you can run today."* (With caveat about training cutoff.)
- 4.7: *"I can't give you a confident recommendation here. My knowledge cutoff is January 2026… if I just named one, I'd be guessing."*

4.6 gives something actionable-from-stale-info. 4.7 refuses. Which is "better" depends on whether the user treats the caveat as sufficient.

**Nudge battery on p04:**

| Nudge | 4.7 result |
|---|---|
| (baseline) | Refuses |
| "Use your judgment — just pick one." | **Commits** to Qwen2.5-Coder-32B with *better* reasoning than baseline 4.6 (mentions FIM support specifically — the thing code completion actually needs, plus tooling notes) |
| "Be opinionated." | **Still refuses** |
| "Search the web to find current rankings, then give me one specific recommendation." | Searches, commits to Qwen3-Coder-480B (*correctly* distinguishing completion from agentic coding — 4.6 just picked Kimi K2.5 from the leaderboard without making that distinction) |
| "Idk, you decide." | Doesn't search, gives Qwen2.5-Coder from priors with caveat |

Key: **"be opinionated" alone doesn't unlock the gap**, which is different from the parent doc's finding on advice/critique tasks. The refusal here is epistemic, not postural. 4.7 isn't withholding an opinion — it's flagging that it doesn't have current facts. Nudges have to grant epistemic permission ("just pick", "just guess", "I know you might be wrong — pick anyway") to close it.

**p12 "I'm too lazy to research this myself — what's been going on with video generation lately?"**

- 4.6: 1 turn, no searches, 570 tokens. Output dated to May 2025 cutoff. Mentions Sora as "launched in late 2024," Veo 2 as current.
- 4.7: 5 turns, 3 searches, 1854 tokens. Output dated to April 2026. Mentions Sora shutting down March 24 2026 (verified), Veo 3.1 Jan 2026, Kling 3.0 Feb 4 2026, LTX-2 Jan 2026.

This is the cleanest single-probe reversal of the Twitter claim. On a deferential-research prompt, **4.7 did the research and 4.6 gave stale priors**.

## Replications on the autonomy gap

The strongest "4.6 more autonomous" data point was p04n4 "Idk, you decide." Replicated 4×:

| Run | 4.6 searches | 4.7 searches |
|---|---|---|
| p04n4 | 2 | 0 |
| p04n4r1 | 0 | 0 |
| p04n4r2 | 2 | 0 |
| p04n4r3 | 0 | 0 |

4.6 goes autonomous about half the time on this prompt; 4.7 never does (N=4). Real asymmetry but stochastic on 4.6's side.

Counter-probe p10 ("Whatever is interesting, pick"), 4×:

| Run | 4.6 searches | 4.7 searches |
|---|---|---|
| p10 | 0 | 0 |
| p10r1 | 0 | 2 |
| p10r2 | 0 | 0 |
| p10r3 | 0 | 2 |

Opposite asymmetry: 4.7 goes autonomous half the time, 4.6 never does (N=4).

Counter-probe pA ("Sense of where things are right now"), 2×:

| Run | 4.6 searches | 4.7 searches |
|---|---|---|
| pA | 0 | 2 |
| pA_r2 | 0 | 3 |

4.7 consistently autonomous, 4.6 consistently not.

Counter-probe pB ("Between Claude/GPT/Gemini — idk you pick"), 2×:

| Run | 4.6 searches | 4.7 searches |
|---|---|---|
| pB | 0 | 0 |
| pB_r2 | 0 | 0 |

Deference on a multi-option comparison → neither searches, regardless of model.

Control pC ("Research… give me a brief"), 2×:

| Run | 4.6 searches | 4.7 searches |
|---|---|---|
| pC | 2 | 2 |
| pC_r2 | 2 | 3 |

Explicit "research" → both search, 4.7 slightly more.

**There is no consistent autonomy-under-ambiguity asymmetry favoring 4.6.** Which model routes to search depends on the prompt, and the direction flips. "4.6 is more proactive" doesn't generalize.

## Cost

Across all 28 paired runs:
- 4.6 total: $2.46, 21,581 output tokens
- 4.7 total: $4.79 (+95%), 41,049 output tokens (+90%)

Per-probe median cost ratio ~1.5×. On autonomous multi-search briefs (p07, p08, p11) it's 1.3–2.6×. On short from-priors answers it's ~1.2×.

In iterative research loops where one query spawns sub-queries spawning sub-queries, +95% compounds fast. For a researcher running hundreds of sessions a week under a Max-plan 5-hour quota, that alone could explain "I switched back to 4.6."

## Fabrication check

Spot-checked one of 4.7's specific claims from p12: *"Sora shut down March 24, 2026."* Verified via CNN, TechCrunch, Wikipedia, and OpenAI Help Center — exactly correct date, correct announcement, correct timing.

N=1 so not definitive. The prior-art "hallucinates with conviction" complaint (gentic.news 17/29 test suite story) wasn't reproduced in my probes, but my probes weren't designed to stress that mode — they ask for current info with search available, which is the opposite regime.

## Where I'd bet the Twitter claim actually lives

Given what I found, a research workflow where 4.6 genuinely feels better than 4.7 probably has at least one of these properties:

1. **Specific-recommendation subtasks with stale priors, no explicit "just pick" nudges.** 4.6 commits with caveats; 4.7 refuses. If your workflow is "pick the best tool for this subtask," 4.7 will deflect more often.

2. **Iterative loops where cost matters.** +95% per cycle compounds. On a long-running agent pipeline, this is felt as "burned through my quota."

3. **Long-context document RAG.** I didn't test this, but the MRCR 78→32 regression in the prior-art doc is the one place where benchmarks show a real 4.7 deficit. If the researcher is feeding in long docs and asking synthesis questions, they're hitting a regime I didn't probe.

4. **Prompt registers 4.7 reads as "answer from what you have"** (like p04n4 "idk you decide") where 4.6 reads them as "go look it up." This is real but stochastic, and there's no general rule — a different deferential phrase (pA, p10, p12) can flip it the other way.

What I'd bet *against*:

- **General content quality.** Of 12 distinct prompts, 4.7 won 8, tied 2, and had only one where "4.6 was more useful" was a reasonable read (p04, and only if you accept stale priors as useful).
- **Proactive scope-widening.** On p01 (SSM), p02 (auth), p05 (interp), p08 (evals), p07 (multi-agent) 4.7 went broader and identified field-level themes 4.6 missed.
- **Fabrication with conviction.** One spot-check passed; I saw no confident-wrong claims in my probe set. Needs more testing to rule out.

## For the use case

If the user wants an autonomous research loop with Opus:

**Probably use 4.7**, specifically because it:
- Searches more deeply when told to (p07, p11)
- Identifies field-level narratives 4.6 misses
- Has a 6-month-later knowledge cutoff
- Delivers better briefs on the "do the research and return a brief" shape (p07)

**Pay for it with**:
- ~2× the budget per run
- A one-line nudge in the system prompt for any subtasks that look like "pick one X" — "use your judgment, just pick one if you're uncertain" — to head off refusals
- Avoid "tell me about X" as a trigger if you want search; use "research", "find current", or "what's the current state of X" — both models reliably search on those

**Test before committing**:
- Run the actual loop under real conditions, not just one-shots. Multi-turn dynamics weren't tested.
- Spot-check a handful of specific claims for fabrication. The one check I did passed, but a confident-hallucination failure mode would sting most in autonomous research specifically.
- Long-context RAG is the prior-art-flagged weakness I didn't probe. If your loop involves stuffing long docs into context, benchmark that separately.

## Caveats

- **N=1 per cell mostly.** Directional only. Replications on p04n4, p10, pA, pB, pC moved some cells from "hypothesis" to "holds", but most single-cell results are hypotheses.
- **Single-shot only.** The real autonomous-research use case is multi-turn and agentic. Not tested.
- **Opportunistic prompt design.** 12 prompts isn't a taxonomy. Selection bias possible — I may have gravitated toward prompts that don't exercise the real gap.
- **Claude Code harness, not bare API.** The Haiku subagent dispatch is a harness detail; API-level calls behave differently.
- **No long-context probes.** The MRCR 78→32 prior-art finding is the most-cited hard-numbers research regression, and I didn't test it.
- **One fabrication spot-check** (p12 Sora date). Not remotely sufficient to clear the hallucination-with-conviction concern; just no signal of it in the probes I ran.
- **Stochastic runs complicate N=1 conclusions.** The p04n4 replication data (2/4, 2/4, 0/4, 0/4 for 4.6) shows how much variance exists even for "clean" single-shot findings.

## Proposed follow-ups

- **Fact-check 4.7's bold specific claims at scale.** LTX-2, Kling 3.0, Falcon H1R, BeyondBench, pass^k numbers on τ-bench. If any are fabricated, that's the real story.
- **Long-context RAG probe.** Feed both a 20-50 page document (a real paper or report) and ask synthesis questions. Where the MRCR regression would actually bite.
- **Multi-turn research loop.** 5-turn session where turn N depends on turn N-1's findings. Test whether 4.7's refusal behaviors compound or self-correct.
- **Cost under Max-plan quota.** The Twitter complaint about "I paid $100 and can't use the app" needs a real-deployment replication, not per-call accounting.
- **Blind scoring by a third model.** All content comparisons here are my own eyeballing; susceptible to bias. A Sonnet or GPT judge picking anonymously between 4.6 and 4.7 outputs on each probe would be cleaner.

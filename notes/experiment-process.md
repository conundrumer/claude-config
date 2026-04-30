# Experiment process

How we run experiments over Claude behavior, using subagents and the `claude` CLI.

LLMs lack training data about their own post-training behavior. Claude can't reliably self-report Claude's tendencies — sounding authoritative isn't the same as knowing. As long as continual learning doesn't exist, this gap is structural. Test, don't ask.

## Default vs this

The default attractor for "run an experiment" leans formal: defined rubrics, criteria specified upfront, sample sizes in the 20-50 range, a clarifying interview before anything runs. Right when the goal is authoritative results that others can reproduce. The ceremony is heavyweight even when the run isn't.

These are *framework-development experiments*. The framework being developed is a living artifact — a dialectic protocol, a posture, a prompt template. Each experiment informs the next iteration. n=1 is acceptable. Findings are directional signals, not proofs. The bar is informativeness for the next step, not generalizability for everyone.

## Kinds we run

- **Primitive validation.** "Does this feature work?" Single intervention, see if it holds. (e.g. checking that a specific briefing depth helps without leading; checking that a synthesis-mode role stays neutral on citations; checking that a dynamic-pull mechanism doesn't cause pull-creep.)
- **Comparison tests.** Two roles or treatments side-by-side on the same task. (e.g. a synthesis-mode role with a specific posture vs. a generic baseline; a posture treatment vs. a no-posture control.)
- **Architecture tests.** Small factorials on architectural variables. (e.g. 2×2 on role-label × timing; three-way trade between architectural variants.)
- **Replication.** Run an existing experiment again to check stability. (e.g. n=2 reruns of an earlier comparison.)
- **Variant surveys.** Multiple variants of a role-shape or interaction, observed in parallel. (e.g. n=5 sweep of response-round role-shapes.)

These categories blur — a primitive validation often pulls in a small comparison; a variant survey is sometimes a many-armed comparison. Labels help with cadence: knowing the kind tells you roughly what shape "good enough" looks like.

## Principles

**Treatment + control every time.** A treatment without a control is an anecdote. Even when control is 90% predictable, having it side-by-side surfaces what would otherwise be invisible — register, length, decision-level, the meta-shape of the artifact. Don't skip control because "we know what it'll say."

**Don't lead the subagent.** A subagent's value is producing what fresh Claude would produce. Leading prompts ("apply these principles," "watch out for X") confound the test — you're testing the prompt, not Claude's natural behavior. Strip the prompt to the request + the substrate. Be clear about scope ("don't read these files") without telegraphing the variable under test.

**Match substrate to the question.** A summary is a compression with the compiler's bias; the real session has what the summary left out; a synthesized substrate has only what you put in. Pick deliberately. When the question is substrate-sensitive (what gets lifted, what's reachable), the summary's bias is exactly what the experiment is trying to bypass.

**One variable at a time.** A run with two variables changing tells you nothing about either. Iterate, don't factorial — except when an architecture test specifically calls for a small factorial.

**Note confounds, don't fix them all.** When treatment saw an existing file in the working directory, that was a confound — the right move was to note it and read the result with the asterisk, not redo the test exhaustively. Confounds turn into next-experiment material.

**Comparison is qualitative.** Read outputs side-by-side. The signal is usually obvious — different register, different level, different shape, different engagement signature. Statistical analysis is overkill for n=1 and not what we're producing.

**Replicate when the finding will drive a framework decision.** A signal from n=1 is direction; sometimes that's enough. When the finding will reshape a primitive or commit you to an architecture, run it again with a different proposition or framing first.

**The user judges informativeness.** Subagents and headless runs can execute autonomously; reading what a result *means* — whether it's signal, whether it's enough, what to do next — stays with the user.

## What's load-bearing now

- Treatment + control as the unit
- Substrate matched to the question
- Subagent prompts stripped of leading
- Iterate over factorial; one variable at a time (small factorials by design only)
- Confounds noted, not eliminated
- Replicate when the finding will drive a framework decision

## What's still open

- When a finding needs to harden into n>1 evidence rather than stay a signal. Some signals are strong enough to act on at n=1; others probably aren't, and the threshold isn't formalized.
- How to recognize when a confound *invalidates* a finding rather than just adding an asterisk.
- The cadence choice — run treatment first then control vs run both in parallel. Both used in different contexts; neither is always right.
- Scaling beyond two-variable changes. The "one variable at a time" rule has only been used at low complexity.
- Handling experiments where the substrate itself is what's being tested. Substrate-as-variable wasn't cleanly separated from posture-as-variable in some runs.

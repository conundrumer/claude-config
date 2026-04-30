---
name: experiment
description: Lightweight prompt/posture/config experiments — compare variants, validate primitives, replicate runs, survey alternatives. Treatment+control, n=1 OK, qualitative. Skip when authoritative rigor is wanted.
---

# Experiment process

Run framework-development experiments over Claude behavior, using subagents and the `claude` CLI.

LLMs lack training data about their own post-training behavior. Claude can't reliably self-report Claude's tendencies — sounding authoritative isn't the same as knowing. As long as continual learning doesn't exist, this gap is structural. Test, don't ask.

## Default vs this

The default attractor for "run an experiment" leans formal: defined rubrics, criteria specified upfront, sample sizes in the 20-50 range, a clarifying interview before anything runs. Right when the goal is authoritative results that others can reproduce. The ceremony is heavyweight even when the run isn't.

These are *framework-development experiments*. The framework being developed is a living artifact — a dialectic protocol, a posture, a prompt template. Each experiment informs the next iteration. n=1 is acceptable. Findings are directional signals, not proofs. The bar is informativeness for the next step, not generalizability for everyone.

## Kinds

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

## Spotting confounds

Confounds usually surface as unexpected tool use — a stray Read, a Write nobody asked for, a Bash or WebFetch that pulled in outside info. Two layers:

**Smoke alarm.** Subagent returns include a `tool_uses` count. `0` for a "checked it" run is a tell; higher-than-expected is worth a closer look.

**Trace.** Scan the session JSONL for tool names and key args:

    jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | "\(.name)\t\(.input.file_path // .input.command // .input.url // .input.pattern // (.input | tostring))"' <jsonl>

JSONL location:

- Subagent (Agent tool): `~/.claude/projects/<parent-cwd-hash>/<parent-session-uuid>/subagents/agent-<agentId>.jsonl`
- CLI (`claude -p`): `~/.claude/projects/<cwd-hash>/<session-uuid>.jsonl` — `cd` before invoking changes the dir
- `ls -t ~/.claude/projects/*/*.jsonl ~/.claude/projects/*/*/subagents/*.jsonl | head` by recency.

## Orchestration

For headless `claude` child orchestration (fork-and-resume, isolation flags), use the `claude-use` skill. This skill answers what experiment shape to want; `claude-use` answers how to drive the children.

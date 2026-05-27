---
name: second-opinion
description: Fresh critique from a subagent that hasn't seen the conversation. Strips author framing to reduce anchoring.
---

# Second Opinion

Author framing ("I think X," "after iterating," "the reviewed version") pulls a reviewer toward the author's position. Stripping it is a cheap hedge against residual sycophancy. Do it because it costs nothing, not because it's load-bearing. If context is genuinely needed for the critique to land (the artifact depends on prior decisions, the user already resolved obvious objections), include it; don't treat the strip as sacred.

**If the request involves multi-perspective work — dialectic, opposed advocates, stress-testing, multiple rounds — stop and read `dialectic.md` before designing anything. The rest of this file covers single-subagent use only.**

## Core

One subagent, neutral input. This covers typical use.

1. Extract the content to critique: the artifact itself, not the conversation around it.
2. Strip commitment language before handing off ("I think," "after iterating," "the reviewed version"). Present neutrally: "Consider this design…" / "Evaluate this claim…"
3. Spawn via the Agent tool (`general-purpose`, foreground) with:
   - The neutralized content
   - A role line: *Give a real critique. Don't diplomatically endorse. Flag weaknesses specifically. "No major issues" is valid if genuine.*
   - What kind of read is wanted (e.g., "structural flaws," "is this design sound," "find what's missing").
4. Return the output un-sanitized. Don't pre-filter for agreeableness.

**Follow-up.** Each spawn returns an `agent_id`. To re-engage the same reviewer, `SendMessage(to: "<agent_id>", message: "...")` resumes from transcript. Replies arrive as a task-completion notification.

## Invocation mode

The Agent tool is the default. Both vehicles share the same tool surface (Read/Grep/Bash/WebSearch/…); the hard capability gap is **delegation** — a `claude` CLI session can spawn subagents, a subagent cannot. Reach for the CLI when the reviewer needs to delegate to keep its own context free of noise: exploring a big repo, running experiments, open-ended web research. Otherwise — artifact self-contained, critique about logic/structure — a subagent suffices.

**Permissions:**

Two orthogonal axes — set both.

`--allowedTools` gates which tools exist. Compose per task: `Read Glob Grep` for exploration, `WebSearch WebFetch` for web research, `Bash Read Edit` for code execution. Always include `Agent` so the session can delegate.

`--permission-mode` gates whether the CLI prompts for approval on each call. Use `auto` when the task is safe and contained; default mode prompts interactively (rarely useful for background review).

**Invocation pattern:**

```bash
SESSION_ID=$(uuidgen)
DIR="/tmp/review-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DIR"

cat <<'EOF' | claude -p \
  --session-id "$SESSION_ID" \
  --model opus \
  --output-format stream-json --verbose \
  --allowedTools "<tools based on task needs>" \
  2>&1 | tee "$DIR/raw.log" | jq -r --unbuffered 'select(.type=="assistant") | .message.content[]? | .text // empty'
You are reviewing this independently. <role line from Core step 3>. Your task: <what kind of read is wanted>. Investigate as needed to ground your assessment.

<neutralized content / critique to evaluate>
EOF
```

`claude -p` buffers by default, so stream-json + `tee`/`jq` is the default pipeline: text streams to captured stdout (visible in the shell details pane) while the full JSON event log is saved at `$DIR/raw.log`. The `jq` filter extracts assistant *text* blocks only — tool-use blocks and thinking blocks are dropped from the stream (still in `raw.log`).

With `run_in_background: true`, the parent Claude only receives a completion notification; to observe intermediate state, tail `$DIR/raw.log` via Read or use the Monitor tool.

Use `--add-dir` if relevant material lives outside the working directory. Use `--model` to match the session's model when it matters.

Always generate a session ID upfront via `uuidgen` and pass `--session-id`. This costs nothing on single-turn use but preserves the option to `--resume` later: for follow-up questions, iterated critique, or multi-round work. A resumed session replays its prior transcript (user/assistant messages + tool calls + tool results) into context — anything not serialized to the transcript is lost, so ensure load-bearing reasoning lands in written output, not just implicit.

```bash
# If continuing later — same streaming pipeline
cat <<'EOF' | claude -p --resume "$SESSION_ID" --model opus \
  --output-format stream-json --verbose 2>&1 \
  | tee -a "$DIR/raw.log" | jq -r --unbuffered 'select(.type=="assistant") | .message.content[]? | .text // empty'
follow-up task
EOF
```

Run via the Bash tool with `run_in_background: true`. CLI sessions that involve exploration can exceed the Bash timeout (10 min max); background mode has no timeout and notifies on completion.

## Analytical vocabulary

Available when the critique benefits from structured moves. Use selectively. When invoking one in the subagent prompt, inject the operational instruction (the line below), not just the label. The subagent starts fresh and doesn't share this skill's context.

- **Determinate negation** — "fails in THIS way, which reveals THIS missing thing" beats "has limitations." Ask for it when the critique is vague.
- **Undercutting defeater** — attack the inferential *link* between evidence and conclusion rather than arguing the opposite conclusion. Reveals more structure.
- **Prospective hindsight** — imagine this has been discredited six months from now; work backward to the fatal joint. More productive than "what could go wrong?"


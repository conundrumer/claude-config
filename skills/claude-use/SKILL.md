---
name: claude-use
description: Spawn and drive a `claude` CLI child from inside Claude Code — persistent stream-json session with send/steer/interrupt primitives. For testing (skills, behaviors, configurations), claude-on-claude experiments, delegated subtasks with mid-run steering, and other meta-claude orchestration.
---

# claude-use

Start with `claude --help` for the flag inventory. This skill covers the non-obvious: the wire-protocol shapes, the behavioral surprises, and the isolation knobs that silently confound experiments otherwise.

## FIFO orchestration

One pitfall: once the child dies, writing to the FIFO blocks forever (open-for-write with no reader never returns). Tear down cleanly.

```bash
DIR=$(mktemp -d); mkfifo "$DIR/in"
claude -p --input-format stream-json --output-format stream-json --verbose \
  --permission-mode auto --session-id $(uuidgen) \
  < "$DIR/in" > "$DIR/out.ndjson" 2> "$DIR/err.log" &
CHILD=$!
send_turn() { printf '%s\n' "$1" > "$DIR/in"; }
# ... use send_turn, parse $DIR/out.ndjson ...
kill $CHILD 2>/dev/null   # tear down before writing more to avoid FIFO wedge
```

## Primitives

- **Send / soft inject** — `{"type":"user","message":{"role":"user","content":"..."}}`. Sent while a turn is in flight, this merges into the ongoing turn and steers the next tool-use decision. Does NOT abort an in-flight tool call.
- **Hard interrupt** — `{"type":"control_request","request_id":"<id>","request":{"subtype":"interrupt"}}`. Cancels the in-flight tool or streaming response; session survives. Ack appears as a `control_response` with matching `request_id`.

See `wire-shapes.md` for the full event catalogue.

## Permission gotchas

Streaming-input stdin does NOT expose a per-call approval channel. For per-call intercept use `--permission-prompt-tool <mcp-tool>` (route prompts through an MCP tool you control) or the Python/TS Agent SDK's `canUseTool`.

Under `--permission-mode auto` in `-p`, the classifier aborts the session after 3 consecutive or 20 total blocks — no retry prompt is available.

## Isolation (for clean-room tests/experiments)

Without these, the child inherits whatever is in the parent's `~/.claude`, confounding results:

- `CLAUDE_CONFIG_DIR=<scratch dir>` — override `~/.claude` entirely
- `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`
- `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`
- `--bare` — skip auto-discovery (requires `ANTHROPIC_API_KEY`)
- `--disable-slash-commands`
- `--setting-sources <user|project|local>` — scope which settings load
- `--plugin-dir <path>` — load only specific plugin dirs
- `--settings <file|json>` — inject settings inline

## Gotchas

1. **SIGINT cleanly cancels the turn but kills the process.** Use `control_request/interrupt` for cancel-and-continue.
2. **FIFO open-for-write blocks forever with no reader.** If the child dies, tear down before attempting another write.
3. **Default permission mode silently auto-denies in `-p`.** No `control_request` is emitted for permission; denials surface only in `result.permission_denials`.
4. **Caller-sent user messages are NOT echoed on stdout** unless `--replay-user-messages`.
5. **`type:"user"` events on stdout are tool_result deliveries**, not caller-sent turns.
6. **Parent's CLAUDE.md and auto-memory leak into the child by default** — disable explicitly for behavioral experiments.
7. **Leading `sleep` is blocked by the Bash tool.** To stall a tool call deterministically, wrap: `bash -c 'sleep N && ...'`.

## References

- `claude --help` — flag inventory
- code.claude.com/en/cli-reference, /headless, /permission-modes, /env-vars
- `wire-shapes.md` — full event shape catalogue

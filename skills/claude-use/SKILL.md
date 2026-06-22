---
name: claude-use
description: Drive a `claude` CLI child with mid-run steering. For testing skills, behaviors, or configurations against a live instance, asking a clean-room or fresh Claude, and claude-on-claude experiments.
---

# claude-use

The child is always a separate `claude` CLI process spawned via Bash. The Agent tool and subagents inherit this session's system prompt and configuration; they cannot serve as any isolation variant. For a one-shot question, `claude -p "..."` with an isolation variant is enough; the FIFO setup is for mid-run steering.

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

## Isolation variants

`CC_TOKEN` holds an OAuth token for CLI children. `CC_API_KEY` holds an Anthropic API key for direct API calls.

**Stock** — plain `claude -p "..."`. Inherits the user's full configuration: global and project CLAUDE.md, skills, plugins, memory, settings. For testing the real setup.

**Clean** — no user or project configuration. The stock Claude Code system prompt and built-in tools remain.

```bash
SCRATCH=$(mktemp -d)
cd /tmp  # any directory without CLAUDE.md in or above it
CLAUDE_CONFIG_DIR="$SCRATCH" \
  CLAUDE_CODE_DISABLE_CLAUDE_MDS=1 \
  CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
  CLAUDE_CODE_OAUTH_TOKEN="$CC_TOKEN" \
  claude --disable-slash-commands -p "..."
```

- `CLAUDE_CONFIG_DIR=<scratch>` — overrides `~/.claude` (skills, plugins, settings, global CLAUDE.md).
- `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` — disables CLAUDE.md auto-discovery from the cwd hierarchy.
- `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` — disables auto-memory loading.
- `CLAUDE_CODE_OAUTH_TOKEN` (OAuth subscription) or `ANTHROPIC_API_KEY` (API key) — auth; keychain is unavailable with `CLAUDE_CONFIG_DIR` overridden.
- `--disable-slash-commands` — disables skill invocation.

**Stripped** — clean plus a nulled system prompt and zero tools. The closest the CLI gets to the raw model. Add to the clean recipe:

```bash
  --system-prompt "" --tools "" --disallowedTools "LSP"
```

The floor is not zero: the system prompt keeps the line `You are a Claude agent, built on Anthropic's Claude Agent SDK.`, and the first user message carries a context block with the account email and current date.

**Null** — a direct API call. Not a CLI child. The model receives only the message sent: no system prompt, no tools, no date, no account context.

```bash
curl -s https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $CC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model": "claude-opus-4-8", "max_tokens": 1024, "messages": [{"role": "user", "content": "..."}]}' \
  | jq -r '.content[0].text'
```

`claude --bare` packs most of the above (hooks, LSP, plugin sync, attribution, auto-memory, background prefetches, keychain reads, CLAUDE.md auto-discovery) into one flag. Requires `ANTHROPIC_API_KEY` or apiKeyHelper via `--settings` — OAuth and keychain are never read in bare mode.

Other knobs:
- `--setting-sources <user|project|local>` — scope which settings load
- `--plugin-dir <path>` — load only specific plugin dirs
- `--settings <file|json>` — inject settings inline

## Gotchas

1. **SIGINT cleanly cancels the turn but kills the process.** Use `control_request/interrupt` for cancel-and-continue.
2. **FIFO open-for-write blocks forever with no reader.** If the child dies, tear down before attempting another write.
3. **Default permission mode silently auto-denies in `-p`.** No `control_request` is emitted for permission; denials surface only in `result.permission_denials`.
4. **Caller-sent user messages are NOT echoed on stdout** unless `--replay-user-messages`.
5. **`type:"user"` events on stdout are tool_result deliveries**, not caller-sent turns.
6. **`--disable-slash-commands` disables invocation but leaves the skill catalog in the system prompt.** Hide the catalog with `CLAUDE_CONFIG_DIR=<scratch>`.
7. **`CLAUDE_CONFIG_DIR` override loses keychain access.** Pair with `CLAUDE_CODE_OAUTH_TOKEN` (OAuth subscription) or `ANTHROPIC_API_KEY` (API key). The slots are distinct; an OAuth token in `ANTHROPIC_API_KEY` errors "Invalid API key."
8. **Project `CLAUDE.md` auto-discovery from cwd is independent of `CLAUDE_CONFIG_DIR`.** Disable with `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`.
9. **Skills resolve via `/skill-name` under `--bare`.** Full suppression needs `--disable-slash-commands`.
10. **Leading `sleep` is blocked by the Bash tool.** To stall a tool call deterministically, wrap: `bash -c 'sleep N && ...'`.
11. **`--system-prompt` appends to the SDK preamble instead of replacing it.** The result is `You are a Claude agent, built on Anthropic's Claude Agent SDK.<your text>`, concatenated with no separator. `""` leaves just the preamble line.
12. **`--tools ""` leaves the LSP tool.** LSP injects outside the built-in set and ignores `CLAUDE_CODE_DISABLE_LSP`. Remove it with `--disallowedTools "LSP"`.
13. **A context block with the account email and current date lands in the first user message** under every CLI isolation knob. Only the null variant avoids it.

## References

- `claude --help` — flag inventory
- code.claude.com/en/cli-reference, /headless, /permission-modes, /env-vars
- `wire-shapes.md` — full event shape catalogue

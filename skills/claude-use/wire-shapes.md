# Wire shapes: --input-format stream-json / --output-format stream-json

## Stdin (caller → child)

- **User turn** — `{"type":"user","message":{"role":"user","content":<string or array of text/image blocks>}}`
- **Control request** — `{"type":"control_request","request_id":"<string>","request":{"subtype":"<subtype>",...}}`

Known control subtypes (from `claude_agent_sdk.types`). Only those marked ✓ have been verified to work over CLI stdin; the rest are named in the SDK source but not empirically tested here:

- `interrupt` ✓ — cancel current turn (no additional fields needed)
- `stop_task` ✓ — halt a specific task; requires a `task_id` field in the `request` object (CLI rejects with `"No task found with ID: undefined"` if omitted)
- `set_permission_mode` — change mode mid-session
- `mcp_message` — send to MCP server
- `rewind_files` — revert file state
- `mcp_reconnect`, `mcp_toggle` — manage MCP servers
- `permission_request` — request per-tool approval
- `initialize` — init with hooks/agents
- `hook_callback` — fire hook

## Stdout (child → caller)

- `system/init` — session_id, model, permissionMode, tools[], plugins[], skills[], claude_code_version
- `system/task_started`, `task_notification`, `task_updated`
- `rate_limit_event`
- `assistant` — `.message.content[]` items with `type` ∈ {`text`, `tool_use`}
- `user` — tool_result deliveries only by default. With `--replay-user-messages`, caller-sent turns are also emitted as `user` events with `isReplay: true` at the top level (distinguishes them from tool_result deliveries).
- `control_response` — `{subtype:"success", request_id:"..."}` ack for a control_request
- `result/success` — `terminal_reason:"completed"`, `permission_denials[]`, `usage{}`
- `result/error_during_execution` — `terminal_reason: "aborted_tools" | "aborted_streaming"`

## Non-obvious fields

- `result.permission_denials[]` — populated even when no approval prompt was shown (silent denies in default mode)
- `user.tool_use_result.{stdout,stderr,interrupted}` — top-level sibling on tool_result deliveries, alongside `.message.content`
- `user.message.content[].tool_use_id` — links a tool_result back to the prior tool_use
- `result.usage.{cache_read_input_tokens, cache_creation_input_tokens}` and `result.total_cost_usd` — per-turn accounting useful across many experimental runs

## Terminal reasons

- `completed` — normal end of turn
- `aborted_tools` — `control_request/interrupt` hit during tool execution
- `aborted_streaming` — interrupt hit during model streaming (also emitted on SIGINT, but SIGINT kills the process afterward)

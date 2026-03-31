---
name: session-schema
description: >
  Claude Code session JSONL format reference. Trigger when parsing session
  JSONL transcripts, reading subagent logs, or tracing tool calls across
  sessions.
user-invocable: false
---

# Claude Code Session JSONL Reference

> Reverse-engineered from real session files + community tools (v2.1.81–2.1.87, March 2026).
> No official schema exists. Format is undocumented and may change between versions.
>
> **Version drift**: This reference covers v2.1.81–2.1.87. Check the current version
> with `claude --version` or the `version` field on any record. If actual session data
> differs from this doc, **trust the data**. Append unexpected fields, record types, or
> behavioral changes to [drift-log.md](drift-log.md) for review.

## Directory Layout

```
~/.claude/
├── history.jsonl                              # Global prompt history (all projects)
├── sessions/
│   └── <pid>.json                             # Process-level session metadata
├── plans/
│   └── <slug>.md                              # Plan files (referenced by slug field)
└── projects/
    └── <project-hash>/                        # Hash = absolute path with / → -
        ├── <session-uuid>.jsonl               # Main session transcript
        ├── <session-uuid>/
        │   ├── subagents/
        │   │   └── agent-<agent-id>.jsonl     # Subagent transcripts
        │   └── tool-results/
        │       └── <random-id>.txt            # Large tool outputs stored externally
        ├── settings.json
        └── memory/
            └── MEMORY.md + *.md
```

**Project hash**: absolute path with `/` → `-`, leading dash included:
`/Users/alice/code/proj` → `-Users-alice-code-proj`

**Agent IDs**: hex-like strings, e.g. `a08b0807c57650a4e`

---

## JSONL Format

Each file is append-only JSONL. Each line is a self-contained JSON object. Lines are chronological and also linked via `parentUuid` chains forming a tree (not a flat log).

---

## Record Types

### `user` — Human Message or Tool Result

```jsonc
{
  "parentUuid": "<uuid>" | null,               // null = first message or new root after compaction
  "uuid": "<uuid>",
  "sessionId": "<session-uuid>",
  "slug": "radiant-popping-snowglobe",         // Human-readable session name; in plan mode also references ~/.claude/plans/<slug>.md
  "isSidechain": false,                        // true only on subagent records (unreliable for rewind branches)
  "agentId": "a08b0807c57650a4e",              // Only present on subagent records
  "type": "user",
  "message": {
    "role": "user",
    "content": "<string>"                      // Plain text for human messages
    // OR
    "content": [                               // Array for tool results or mixed content
      {
        "type": "tool_result",
        "tool_use_id": "<matching-tool-use-id>",
        "content": "<result-string>",
        "is_error": false
      },
      {
        "type": "text",
        "text": "user follow-up text"          // Can appear alongside tool_result
      }
    ]
  },
  "promptId": "<uuid>",                        // Groups related user messages in same turn
  "permissionMode": "default",                 // Only on human-initiated messages
  "sourceToolAssistantUUID": "<uuid>",         // On tool_result: points to assistant that issued the tool_use
  "toolUseResult": "<summary>" | { ... },      // Summary of tool result (see shapes below)
  "forkedFrom": {                              // Only on messages copied into a forked session
    "sessionId": "<original-uuid>",
    "messageUuid": "<msg-uuid>"
  },
  "timestamp": "2026-03-30T21:18:55.517Z",
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "/Users/delu/code/my-project",
  "version": "2.1.87",
  "gitBranch": "main"
}
```

#### `toolUseResult` shapes

- **String**: `"User rejected tool use"`, `"Error: Exit code 1\n..."`
- **Object with `type: "text"`**: `{"type": "text", "file": {"filePath": "...", "content": "..."}}` — file read/write
- **Object with `type: "create"`**: `{"type": "create", "filePath": "...", "content": "..."}` — file creation
- **Object with status**: `{"status": "completed", "prompt": "..."}` — Agent/skill results
- **Object with todos**: `{"oldTodos": [...], "newTodos": [...]}` — TodoWrite
- **Object with stdout**: `{"stdout": "..."}` — Bash

---

### `assistant` — Claude Response

```jsonc
{
  "parentUuid": "<uuid>",
  "uuid": "<uuid>",
  "sessionId": "<session-uuid>",
  "slug": "...",
  "isSidechain": false,
  "agentId": "...",                            // Only on subagent records
  "type": "assistant",
  "message": {
    "model": "claude-opus-4-6",
    "id": "msg_01TrwA6eGJx8FGbWXsG4V6Rr",
    "type": "message",
    "role": "assistant",
    "content": [ /* content blocks */ ],
    "stop_reason": "tool_use" | "end_turn" | null,
    "stop_sequence": null,
    "usage": {
      "input_tokens": 3,
      "cache_creation_input_tokens": 4876,
      "cache_read_input_tokens": 12328,
      "output_tokens": 346,
      "service_tier": "standard",
      "cache_creation": {
        "ephemeral_5m_input_tokens": 0,
        "ephemeral_1h_input_tokens": 4876
      },
      "server_tool_use": {
        "web_search_requests": 0,
        "web_fetch_requests": 0
      }
    }
  },
  "requestId": "req_011CZZxmK9i52San8AwydDph",
  "timestamp": "...",
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "...",
  "version": "...",
  "gitBranch": "..."
}
```

#### Content Block Types

**`text`** — Plain text:
```jsonc
{ "type": "text", "text": "Here's what I found..." }
```

**`thinking`** — Extended thinking:
```jsonc
{
  "type": "thinking",
  "thinking": "",                              // Often empty/redacted
  "signature": "EvcCClkIDBgC..."               // Cryptographic signature
}
```

**`tool_use`** — Tool invocation:
```jsonc
{
  "type": "tool_use",
  "id": "toolu_01DBvQCL1swBnyCGCj2YVXFp",    // Referenced by tool_result's tool_use_id
  "name": "Bash",                              // Bash, Read, Write, Edit, Glob, Grep, Agent, etc.
  "input": { "command": "ls -la" },            // Tool-specific parameters
  "caller": { "type": "direct" }
}
```

---

### `system` — Metadata Events

Distinguished by `subtype`:

| Subtype | Key Fields | Description |
|---------|-----------|-------------|
| `turn_duration` | `durationMs`, `messageCount` | End-of-turn timing |
| `local_command` | `content`, `level` | Hook/command execution output |
| `api_error` | `error`, `retryInMs`, `retryAttempt` | API failure + retry info |
| `bridge_status` | `content`, `url` | Remote session bridge status |
| `compact_boundary` | `logicalParentUuid`, `compactMetadata` | Context compaction marker (see [branching-and-compaction.md](branching-and-compaction.md)) |

---

### `progress` — Hook Events & Subagent Relay

Two purposes:

**Hook events** — logged alongside tool results:
```jsonc
{
  "type": "progress",
  "data": { "type": "hook_progress", "hookEvent": "PostToolUse", "hookName": "PostToolUse:Read" },
  "parentToolUseID": "toolu_...",
  "toolUseID": "toolu_..."
}
```

**Subagent relay** — inlines subagent tool results into parent transcript via `data.message` (contains a full user/tool_result record).

---

### `queue-operation` — User Input Queue

```jsonc
{
  "type": "queue-operation",
  "operation": "enqueue" | "dequeue",          // dequeue has no content
  "content": "still working?",                 // Only on enqueue
  "sessionId": "...",
  "timestamp": "..."
}
```

---

### `file-history-snapshot` — File State Tracking

```jsonc
{
  "type": "file-history-snapshot",
  "messageId": "<uuid>",                       // Matches associated user message uuid
  "snapshot": {
    "messageId": "<uuid>",
    "trackedFileBackups": {},                   // Map of file paths → backup content
    "timestamp": "..."
  },
  "isSnapshotUpdate": false
}
```

---

## Subagent Sessions

Subagent transcripts live at `<session-uuid>/subagents/agent-<agent-id>.jsonl`.

Distinguishing features:
- `isSidechain: true` (reliably set, unlike rewind branches)
- `agentId` field present
- Same `sessionId` and `slug` as parent
- First record has `parentUuid: null`

The parent session only has the Agent `tool_use` and its final `tool_result`. To see what the subagent did, read its JSONL file.

### Linking parent ↔ subagent

1. Find `tool_use` with `name: "Agent"` in parent — note the `id` field
2. The `tool_result` has `tool_use_id` matching that `id`
3. The subagent file's `agentId` matches the directory name: `agent-<agentId>.jsonl`

---

## How to Read a Session

### Reconstruct the active conversation
Walk backward from the **last record** via `parentUuid`. This is the active path. Everything else is an abandoned branch or metadata.

### Link tool calls to results
Match `tool_use.id` → `tool_result.tool_use_id`.

### Link tool results to issuing assistant
`sourceToolAssistantUUID` on the tool_result record → the assistant record's `uuid`.

### Identify the model
`message.model` on any assistant record.

### Token usage
Sum `message.usage` fields across assistant records.

### Filter noise
Skip these when reconstructing conversation flow:
- `file-history-snapshot` — undo tracking
- `progress` — hook events (creates phantom branches alongside tool_result records)
- `queue-operation` — input queue
- `system` with `subtype: turn_duration` — timing metadata
- `system` with `subtype: api_error` — retry events

---

## Auxiliary Files

**`~/.claude/history.jsonl`** — global prompt history:
```jsonc
{ "display": "fix the auth bug", "pastedContents": {}, "timestamp": 1764547411299, "project": "/Users/delu/code/proj", "sessionId": "<uuid>" }
```

**`~/.claude/sessions/<pid>.json`** — process metadata:
```jsonc
{ "pid": 53458, "sessionId": "<uuid>", "cwd": "...", "startedAt": 1774905564113, "kind": "interactive", "entrypoint": "cli" }
```

**`<session-uuid>/tool-results/<id>.txt`** — large tool outputs stored as plain text.

---

For branching, compaction, session forking, and tree navigation, see [branching-and-compaction.md](branching-and-compaction.md).

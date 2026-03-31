# Branching, Compaction & Tree Navigation

Advanced reference for session tree structure. See [SKILL.md](SKILL.md) for core format.

## Conversation Tree Structure

Sessions are **DAGs (directed acyclic graphs)**, not linear sequences. The `parentUuid` chain forms a tree where multiple records can share the same parent, creating branches.

### How Branches Form

**User edits / rewinds**: When a user rewinds to a previous message and types something different, a new user record is created with the same `parentUuid` as the original. Both paths remain in the JSONL.

```
                  assistant (line 20)
                  ├── user (line 22): "code is data"              ← abandoned (0 children)
                  └── user (line 24): "code is data, and we can   ← active (has children)
                       programmatically modify it"
                       └── assistant (line 25): ...
```

**Multiple edits**: A single parent can have many children (observed: up to 6 at one node):

```
                  user (line 36): [original message]
                  ├── user (line 38): "wait. how would we..."     ← abandoned
                  ├── user (line 43): "continue"                  ← abandoned
                  ├── user (line 51): "i mean. all refs to..."    ← abandoned
                  └── user (line 55): "i mean. all refs to..."    ← active (final edit)
                       └── assistant (line 57): ...
```

### Identifying the Active Path

Walk backward from the **last record in the file** via `parentUuid`. Everything NOT on this path is an abandoned branch.

**`isSidechain` is unreliable for branches** (bug, issue #24471): As of v2.1.87, `isSidechain` is never set to `true` on rewind-created branches in main session files. It IS reliably set on subagent records. Do not use `isSidechain` to detect abandoned branches — use the parentUuid walk.

### Detecting Branches Programmatically

```python
from collections import defaultdict

# Build parent → children map
children_of = defaultdict(list)
uuid_to_record = {}
for i, rec in enumerate(records):
    uuid_to_record[rec.get('uuid')] = rec
    pu = rec.get('parentUuid')
    if pu:
        children_of[pu].append((i, rec))

# Branch points: any node with multiple children
branch_points = {pu: kids for pu, kids in children_of.items() if len(kids) > 1}

# Active path: walk backward from last record
active = set()
uuid = records[-1].get('uuid')
while uuid:
    active.add(uuid)
    rec = uuid_to_record.get(uuid)
    if not rec:
        break
    uuid = rec.get('parentUuid')
```

### Progress Records as "Phantom Branches"

A common fork pattern is `progress` + `tool_result` sharing the same parent (an assistant `tool_use`). This is NOT a user branch — it's the hook system logging alongside the tool result:

```
                  assistant (tool_use)
                  ├── progress (hook_progress, PostToolUse)    ← hook event, skip
                  └── user (tool_result)                       ← actual conversation
```

Filter out `progress` records to avoid false branch detection.

### Real-World Tree Stats (from issue #24471)

```
Session with heavy rewind usage:
├─ Total nodes:           10,671
├─ Active path:           64 messages (post-compaction)
├─ Abandoned branches:    10,607 nodes
├─ Branch points:         275
│  └─ Max children:       6 at a single node
└─ Root nodes:            3 (from compaction creating new roots)
```

---

## Context Compaction

When the context window approaches limits (~167K tokens), Claude Code performs compaction:

1. A **`compact_boundary`** system record is written:
   ```jsonc
   {
     "type": "system",
     "subtype": "compact_boundary",
     "parentUuid": null,                       // Severs the tree
     "logicalParentUuid": "<last-pre-compaction-uuid>",
     "compactMetadata": {
       "trigger": "auto" | "manual",
       "preTokens": 150000
     }
   }
   ```

2. Immediately after: a synthetic **user message**:
   ```jsonc
   {
     "type": "user",
     "isCompactSummary": true,
     "isVisibleInTranscriptOnly": true,
     "message": { "role": "user", "content": "<AI-generated conversation summary>" }
   }
   ```

3. Normal messages resume, parented to the summary.

### Tree Severance

Compaction creates a **new root** (`parentUuid: null`), disconnecting the pre-compaction tree:

```
Pre-compaction:
  Root → msg1 → msg2 → ... → msgN → [compaction point]

Post-compaction:
  Root → msg1 → ... → msgN   ← still in JSONL, unreachable via parentUuid walk

  NewRoot (compact_boundary, parentUuid: null)
    └─ CompactSummary (isCompactSummary: true)
        └─ subsequent messages...
```

All pre-compaction data remains in the file but is not reachable by walking `parentUuid` from the current leaf. To access it, scan for all records with `parentUuid: null` to find roots, then build separate trees from each.

---

## Session Forking (`--fork-session`)

`claude --continue --fork-session` creates a new, self-contained session file:

- The linear chain from root to the branch point is **copied** into the new file
- Messages after the fork point are excluded
- Each copied message has a `forkedFrom` field:
  ```jsonc
  { "forkedFrom": { "sessionId": "<original-uuid>", "messageUuid": "<msg-uuid>" } }
  ```
- New messages after the branch point have no `forkedFrom`
- The original session stays untouched

---

## Session Continuation (`--continue` / `--resume`)

When resuming a session:

1. A new JSONL file is created with a new UUID
2. Initial records copy the parent's final compact_boundary (if any)
3. The `slug` field is shared between parent and continuation
4. The `sessionId` in early records may differ from the filename (parent's ID)
5. Where `sessionId` switches to match the filename = start of the new session

---

## Sources

- [How Claude Code Session Continuation Works](https://blog.fsck.com/releases/2026/02/22/claude-code-session-continuation/) — continuation mechanics
- [Rewind history lost after compaction (issue #24471)](https://github.com/anthropics/claude-code/issues/24471) — tree stats, isSidechain bug
- [Session Management - DeepWiki](https://deepwiki.com/anthropics/claude-code/2.4-session-management) — persistence architecture
- [claude-code-transcripts (simonw)](https://github.com/simonw/claude-code-transcripts) — transcript tools
- [claude-JSONL-browser (withLinda)](https://github.com/withLinda/claude-JSONL-browser) — JSONL viewer
- [claude-code-log (daaain)](https://github.com/daaain/claude-code-log) — JSONL→HTML converter
- [cclv (albertov)](https://github.com/albertov/cclv) — TUI log viewer

# claude-config

Personal source-of-truth for `~/.claude/` configuration. Structure mirrors `~/.claude/`. Not symlinked. Edit here, sync to deploy — `~/.claude/`.

## Sync workflow

`./sync.sh` rsyncs deliverables one-way into `~/.claude/` (`global-claude.md` → `~/.claude/CLAUDE.md`; `docs/`, `scripts/`, `skills/`, `agents/` to matching subdirs). It also applies idempotent `jq` patches to `~/.claude/settings.json` (hooks, statusline, env defaults) — see the script for specifics.

## Key files

- `global-claude.md` — global CLAUDE.md instructions deployed to all projects.
- `scripts/statusline-command.sh` — status bar script. Reads JSON context from stdin, outputs an ANSI line; also writes `~/.claude/usage.json`.
- `scripts/notification-sound.sh` — Stop hook that plays the macOS sound named by the HTML-comment marker at the end of the last message.
- `agents/recuse.md` — `recuse` subagent. Independent reviewer that recuses when the dispatch prompt carries the answer or steers the search.
- `notes/` — write-ups on Claude's behavior, indexed in `notes/README.md`.

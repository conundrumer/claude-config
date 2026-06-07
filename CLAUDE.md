# claude-config

Personal source-of-truth for `~/.claude/` configuration. Structure mirrors `~/.claude/`. Not symlinked. Edit here, sync to deploy — `~/.claude/`.

## Sync workflow

`./sync.sh` rsyncs deliverables one-way into `~/.claude/` and applies idempotent `jq` patches to `~/.claude/settings.json` — see the script for specifics.

## Key files

- `global-claude.md` — global CLAUDE.md instructions deployed to all projects.
- `scripts/statusline-command.sh` — status bar script.
- `scripts/notification-sound.sh` — Stop hook that plays a macOS sound.
- `agents/recuse.md` — `recuse` subagent, an independent reviewer.
- `notes/` — write-ups on Claude's behavior, indexed in `notes/README.md`.

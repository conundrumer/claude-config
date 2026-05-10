# claude-config

Personal source-of-truth for `~/.claude/` configuration. Structure mirrors `~/.claude/`.

## Sync workflow

`./sync.sh` copies deliverables into `~/.claude/` via rsync (one-way, not symlinked):
- `global-claude.md` → `~/.claude/CLAUDE.md`
- `statusline-command.sh` → `~/.claude/statusline-command.sh`
- `hooks/` → `~/.claude/hooks/`
- `skills/` → `~/.claude/skills/`

`sync.sh` also applies idempotent `jq` patches to `~/.claude/settings.json`, so deploying the script wires the behavior, not just the files:
- Registers the notification-sound Stop hook (leaves any other Stop hooks in place).
- Registers a Notification hook that plays `Ping.aiff` on permission prompts and idle-input prompts.
- Defaults `env.CLAUDE_CODE_FORK_SUBAGENT` to `"1"` (preserves any existing value).

Not synced: `projects/`, `sessions/`, `plugins/`, runtime state.

## Key files

- `global-claude.md` — global CLAUDE.md instructions deployed to all projects. Edit here, sync to deploy.
- `statusline-command.sh` — status bar script. Reads Claude Code JSON context from stdin, outputs ANSI-colored line. Also writes rate limit data to `~/.claude/usage.json`.
- `hooks/notification-sound.sh` — Stop hook. An HTML-comment marker (`<!-- glass -->`, `<!-- funk -->`, etc.) at the end of the assistant's last message names a macOS system sound to play. The marker is invisible in rendered Markdown.
- `skills/session-schema/` — reverse-engineered JSONL session format reference. Not user-invocable; loaded automatically when parsing session transcripts.
- `skills/ai-lint/` — linter for AI-generated writing. Removes compulsive AI-writing patterns from existing text.
- `notes/` — write-ups on Claude's behavior. See `notes/README.md` for the index — add a hook there when adding a new file. Not synced; for reference.

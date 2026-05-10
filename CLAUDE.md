# claude-config

Personal source-of-truth for `~/.claude/` configuration. Structure mirrors `~/.claude/`.

## Sync workflow

`./sync.sh` copies deliverables into `~/.claude/` via rsync (one-way, not symlinked):
- `global-claude.md` → `~/.claude/CLAUDE.md`
- `statusline-command.sh` → `~/.claude/statusline-command.sh`
- `hooks/` → `~/.claude/hooks/`
- `skills/` → `~/.claude/skills/`

`settings.json` is managed by hand. `sync.sh` makes a couple of exceptions, both via idempotent `jq` patches: it registers the notification-sound Stop hook (leaving any other Stop hooks in place), and defaults `env.CLAUDE_CODE_FORK_SUBAGENT` to `"1"` (preserves any existing value). Deploying the script also wires both up.

Not synced: `projects/`, `sessions/`, `plugins/`, runtime state.

## Key files

- `global-claude.md` — global CLAUDE.md instructions deployed to all projects. Edit here, sync to deploy.
- `statusline-command.sh` — status bar script. Reads Claude Code JSON context from stdin, outputs ANSI-colored line. Also writes rate limit data to `~/.claude/usage.json`.
- `hooks/notification-sound.sh` — Stop hook. An HTML-comment marker (`<!-- glass -->`, `<!-- funk -->`, etc.) at the end of the assistant's last message names a macOS system sound to play. The marker is invisible in render but lives in the JSONL transcript, which the hook reads via the `transcript_path` it receives on stdin.
- `skills/session-schema/` — reverse-engineered JSONL session format reference. Not user-invocable; loaded automatically when parsing session transcripts.
- `skills/ai-lint/` — linter for AI-generated writing. Removes compulsive AI-writing patterns from existing text.
- `notes/` — write-ups on Claude's behavior. See `notes/README.md` for the index — add a hook there when adding a new file. Not synced; for reference.

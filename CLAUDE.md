# claude-config

Personal source-of-truth for `~/.claude/` configuration. Structure mirrors `~/.claude/`.

## Sync workflow

`./sync.sh` copies deliverables into `~/.claude/` via rsync (one-way, not symlinked):
- `global-claude.md` → `~/.claude/CLAUDE.md`
- `statusline-command.sh` → `~/.claude/statusline-command.sh`
- `skills/` → `~/.claude/skills/`

Not synced: `settings.json`, `projects/`, `sessions/`, `plugins/`, runtime state.

## Key files

- `global-claude.md` — global CLAUDE.md instructions deployed to all projects. Edit here, sync to deploy.
- `statusline-command.sh` — status bar script. Reads Claude Code JSON context from stdin, outputs ANSI-colored line. Also writes rate limit data to `~/.claude/usage.json`.
- `skills/session-schema/` — reverse-engineered JSONL session format reference. Not user-invocable; loaded automatically when parsing session transcripts.
- `skills/ai-lint/` — linter for AI-generated writing. Removes compulsive AI-writing patterns from existing text.

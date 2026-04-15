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

## Scripts (local-only, not synced)

- `scripts/theme-sync/` — Swift LaunchAgent daemon that watches macOS appearance changes and writes `theme` to `~/.claude.json`. Install/uninstall via its shell scripts.
- `scripts/theme-hotreload-patch/` — Binary patcher for Claude Code so running sessions pick up theme changes without restart. Version-specific: each supported version has its own `patterns.py` under a versioned subdirectory.

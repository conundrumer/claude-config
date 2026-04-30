# claude-config

Source of truth for `~/.claude/` configuration. Structure mirrors `~/.claude/`.

## Synced

Copied (not symlinked) into `~/.claude/` via `./sync.sh`:

- `CLAUDE.md`
- `statusline-command.sh`
- `skills/`

## Not synced

- `settings.json` — machine-specific
- `projects/`, `sessions/`, `history.jsonl` — session data
- `plugins/` — managed by plugin system
- Everything else is runtime/ephemeral

## Shell env

Not tracked here, but documented so future-me knows where to look:

- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` lives in `~/.zshenv`. Enables the `SendMessage` deferred tool (resume a spawned agent with full context). Must be a shell-level export — `settings.json` `env:` is parsed after the gate evaluates, so it has no effect. Source: [#35240](https://github.com/anthropics/claude-code/issues/35240#issuecomment-4282667930).

## Scripts

### `scripts/theme-sync/`

Swift daemon that syncs Claude Code theme with macOS system appearance. Based on [alfredomtx/claude-theme-sync](https://github.com/alfredomtx/claude-theme-sync), fixed to use AppKit run loop (required for `DistributedNotificationCenter` to deliver).

```bash
# Install (compiles Swift daemon, registers LaunchAgent)
scripts/theme-sync/install.sh

# Uninstall
scripts/theme-sync/uninstall.sh
```

Writes to `~/.claude.json` `theme` field. Requires Xcode Command Line Tools.

### `scripts/theme-hotreload-patch/`

Patches the Claude Code binary so running sessions pick up theme changes from `~/.claude.json`. Without this, theme only applies at process startup. Pair with theme-sync for automatic light/dark switching.

Version-specific (currently 2.1.87, 2.1.88, 2.1.89, 2.1.90); see its [README](scripts/theme-hotreload-patch/README.md) for how to adapt to new versions.

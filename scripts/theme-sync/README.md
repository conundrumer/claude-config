# Claude Theme Sync

Syncs Claude Code theme with macOS dark/light mode. Based on [alfredomtx/claude-theme-sync](https://github.com/alfredomtx/claude-theme-sync), fixed to use AppKit run loop (required for `DistributedNotificationCenter` to deliver notifications in a LaunchAgent context).

## Installation

```bash
./install.sh
```

Compiles the Swift daemon and registers a LaunchAgent that starts on login.

## Requirements

- macOS
- Xcode Command Line Tools (`xcode-select --install`)

## How it works

A lightweight Swift daemon listens for `AppleInterfaceThemeChangedNotification` and writes the matching theme to `~/.claude.json`.

On its own, this only affects new Claude Code sessions (theme is read at startup). Pair with [`scripts/theme-hotreload-patch/`](../theme-hotreload-patch/) to update running sessions in real time.

## Commands

```bash
# Check if running
launchctl list | grep claude-theme-sync

# View logs
tail -f ~/.claude/theme-sync/claude-theme-sync.log

# Restart
launchctl unload ~/Library/LaunchAgents/com.claude.theme-sync.plist
launchctl load ~/Library/LaunchAgents/com.claude.theme-sync.plist
```

## Uninstall

```bash
./uninstall.sh
```

## Technical details

Claude Code stores its theme preference in `~/.claude.json`:

```json
{
  "theme": "dark",
  ...
}
```

The daemon watches for `AppleInterfaceThemeChangedNotification` and updates that field when macOS appearance changes. Requires `AppKit` (not just `Foundation`) — the `NSApplication` run loop is needed for distributed notifications to be delivered.

## License

MIT

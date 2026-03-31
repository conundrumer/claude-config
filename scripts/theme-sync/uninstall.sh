#!/bin/bash

INSTALL_DIR="$HOME/.claude/theme-sync"
PLIST_NAME="com.claude.theme-sync.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "=== Claude Theme Sync Uninstaller ==="
echo ""

# Unload agent
if launchctl list 2>/dev/null | grep -q "com.claude.theme-sync"; then
    echo "Stopping agent..."
    launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_NAME" 2>/dev/null || true
fi

# Remove plist
if [ -f "$LAUNCH_AGENTS_DIR/$PLIST_NAME" ]; then
    echo "Removing launch agent..."
    rm "$LAUNCH_AGENTS_DIR/$PLIST_NAME"
fi

# Remove install directory
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing installed files..."
    rm -rf "$INSTALL_DIR"
fi

echo ""
echo "=== Uninstall Complete ==="

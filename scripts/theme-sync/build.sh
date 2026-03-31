#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building Claude Theme Sync..."
swiftc -O ClaudeThemeSync.swift -o claude-theme-sync

echo "Build complete: $SCRIPT_DIR/claude-theme-sync"

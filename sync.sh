#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude"

rsync -av "$REPO_DIR/global-claude.md" "$TARGET/CLAUDE.md"
rsync -av "$REPO_DIR/statusline-command.sh" "$TARGET/"

rsync -av "$REPO_DIR/skills/" "$TARGET/skills/"

echo "Synced to $TARGET"

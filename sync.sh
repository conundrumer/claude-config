#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude"

rsync -av --exclude '.git' \
  "$REPO_DIR/CLAUDE.md" \
  "$REPO_DIR/statusline-command.sh" \
  "$TARGET/"

rsync -av "$REPO_DIR/skills/" "$TARGET/skills/"

echo "Synced to $TARGET"

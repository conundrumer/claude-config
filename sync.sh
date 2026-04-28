#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude"

rsync -av "$REPO_DIR/global-claude.md" "$TARGET/CLAUDE.md"
rsync -av "$REPO_DIR/statusline-command.sh" "$TARGET/"

mkdir -p "$TARGET/skills"
for skill in "$REPO_DIR/skills"/*/; do
  name=$(basename "$skill")
  rsync -av --delete "$skill" "$TARGET/skills/$name/"
done

echo "Synced to $TARGET"

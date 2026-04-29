#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude"

rsync -av "$REPO_DIR/global-claude.md" "$TARGET/CLAUDE.md"
rsync -av "$REPO_DIR/statusline-command.sh" "$TARGET/"

mkdir -p "$TARGET/hooks"
rsync -av "$REPO_DIR/hooks/" "$TARGET/hooks/"
chmod +x "$TARGET/hooks"/*.sh

mkdir -p "$TARGET/skills"
for skill in "$REPO_DIR/skills"/*/; do
  name=$(basename "$skill")
  rsync -av --delete "$skill" "$TARGET/skills/$name/"
done

# Idempotent settings.json patch: register the notification-sound Stop hook
# if it isn't already present. Settings is otherwise unsynced; this is the one
# exception so hooks land wired, not just deployed.
SETTINGS="$TARGET/settings.json"
HOOK_CMD="bash ~/.claude/hooks/notification-sound.sh"
if [ -f "$SETTINGS" ]; then
  patched=$(jq --arg cmd "$HOOK_CMD" '
    def has_cmd:
      [.hooks.Stop[]?.hooks[]?.command] | any(. == $cmd);
    if has_cmd then .
    else
      .hooks //= {}
      | .hooks.Stop //= []
      | .hooks.Stop += [{hooks: [{type: "command", command: $cmd}]}]
    end
  ' "$SETTINGS")
  if [ "$patched" != "$(cat "$SETTINGS")" ]; then
    printf '%s\n' "$patched" > "$SETTINGS"
    echo "Wired Stop hook in $SETTINGS"
  fi
fi

echo "Synced to $TARGET"

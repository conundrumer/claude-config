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

# Idempotent settings.json patches. Settings is otherwise unsynced; these are
# the exceptions so behavior lands wired, not just deployed.
# - Register the notification-sound Stop hook if absent.
# - Default CLAUDE_CODE_FORK_SUBAGENT=1 (preserves any existing value).
SETTINGS="$TARGET/settings.json"
HOOK_CMD="bash ~/.claude/hooks/notification-sound.sh"
if [ -f "$SETTINGS" ]; then
  patched=$(jq --arg cmd "$HOOK_CMD" '
    def has_cmd:
      [.hooks.Stop[]?.hooks[]?.command] | any(. == $cmd);
    (if has_cmd then .
     else
       .hooks //= {}
       | .hooks.Stop //= []
       | .hooks.Stop += [{hooks: [{type: "command", command: $cmd}]}]
     end)
    | .env //= {}
    | .env.CLAUDE_CODE_FORK_SUBAGENT //= "1"
  ' "$SETTINGS")
  if [ "$patched" != "$(cat "$SETTINGS")" ]; then
    printf '%s\n' "$patched" > "$SETTINGS"
    echo "Updated $SETTINGS"
  fi
fi

echo "Synced to $TARGET"

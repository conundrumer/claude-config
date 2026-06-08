#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude"

rsync -av "$REPO_DIR/global-claude.md" "$TARGET/CLAUDE.md"

mkdir -p "$TARGET/docs"
rsync -av "$REPO_DIR/docs/" "$TARGET/docs/"

mkdir -p "$TARGET/scripts"
rsync -av "$REPO_DIR/scripts/" "$TARGET/scripts/"
chmod +x "$TARGET/scripts"/*.sh

mkdir -p "$TARGET/skills"
for skill in "$REPO_DIR/skills"/*/; do
  name=$(basename "$skill")
  rsync -av --delete "$skill" "$TARGET/skills/$name/"
done

mkdir -p "$TARGET/agents"
rsync -av --delete "$REPO_DIR/agents/" "$TARGET/agents/"

# Idempotent settings.json patches so behavior lands wired, not just deployed:
# - Register the notification-sound Stop hook if absent.
# - Register the permission/idle Notification hook (Ping sound) if absent.
# - Reconcile the UserPromptSubmit reminder hook to PROMPT_REMINDER.
# - Point statusLine.command at the deployed status bar script.
SETTINGS="$TARGET/settings.json"
STOP_CMD="bash ~/.claude/scripts/notification-sound.sh"
NOTIF_CMD="bash ~/.claude/scripts/notification-sound-permission.sh"
OLD_NOTIF_CMD="afplay /System/Library/Sounds/Ping.aiff"
STATUSLINE_CMD="bash ~/.claude/scripts/statusline-command.sh"
# UserPromptSubmit reminder injected into context on each prompt.
# Set empty to disable; the next sync removes the hook.
PROMPT_REMINDER="Headline-Continuation: Answer, then think."
PROMPT_MARKER="claude-config:prompt-reminder"
PROMPT_CMD="echo '$PROMPT_REMINDER' # $PROMPT_MARKER"
if [ -f "$SETTINGS" ]; then
  patched=$(jq --arg stop_cmd "$STOP_CMD" --arg notif_cmd "$NOTIF_CMD" --arg old_notif_cmd "$OLD_NOTIF_CMD" --arg statusline_cmd "$STATUSLINE_CMD" --arg prompt_cmd "$PROMPT_CMD" --arg prompt_marker "$PROMPT_MARKER" --arg reminder "$PROMPT_REMINDER" '
    def has_stop:
      [.hooks.Stop[]?.hooks[]?.command] | any(. == $stop_cmd);
    def has_notif:
      [.hooks.Notification[]?.hooks[]?.command] | any(. == $notif_cmd);
    # Drop any prior inline Notification hook so we do not double-fire.
    (if .hooks.Notification then
       .hooks.Notification |= map(
         .hooks |= map(select(.command != $old_notif_cmd))
       ) | .hooks.Notification |= map(select((.hooks // []) | length > 0))
     else . end)
    | (if has_stop then .
       else
         .hooks //= {}
         | .hooks.Stop //= []
         | .hooks.Stop += [{hooks: [{type: "command", command: $stop_cmd}]}]
       end)
    | (if has_notif then .
       else
         .hooks //= {}
         | .hooks.Notification //= []
         | .hooks.Notification += [{hooks: [{type: "command", command: $notif_cmd}]}]
       end)
    # Reconcile the marked reminder: strip the prior one, re-add if enabled.
    | .hooks //= {}
    | .hooks.UserPromptSubmit //= []
    | .hooks.UserPromptSubmit |= map(.hooks |= map(select((.command // "") | contains($prompt_marker) | not)))
    | .hooks.UserPromptSubmit |= map(select((.hooks // []) | length > 0))
    | (if ($reminder | length) > 0 then
         .hooks.UserPromptSubmit += [{hooks: [{type: "command", command: $prompt_cmd}]}]
       else . end)
    | (if (.hooks.UserPromptSubmit | length) == 0 then del(.hooks.UserPromptSubmit) else . end)
    | .statusLine = ((.statusLine // {}) + {type: "command", command: $statusline_cmd})
  ' "$SETTINGS")
  if [ "$patched" != "$(cat "$SETTINGS")" ]; then
    printf '%s\n' "$patched" > "$SETTINGS"
    echo "Updated $SETTINGS"
  fi
fi

echo "Synced to $TARGET"

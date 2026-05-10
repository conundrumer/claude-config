#!/bin/bash
# Notification hook. Plays a sound only for permission prompts.
# Claude Code also fires Notification events with notification_type
# "idle_prompt" some seconds after a turn ends — those are skipped so the
# sound stays specific to "permission needed."

SOUND="/System/Library/Sounds/Ping.aiff"

payload=$(cat)
notif_type=$(printf '%s' "$payload" | jq -r '.notification_type // empty')

[ "$notif_type" = "permission_prompt" ] || exit 0

afplay "$SOUND" </dev/null >/dev/null 2>&1 &

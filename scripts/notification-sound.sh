#!/bin/bash
# Stop hook. Plays a macOS system sound when a response ends. The last
# non-empty line of the assistant's last message names the sound, italicized
# or bare: `*glass*` or `glass` → Glass.aiff. Anything else → Morse.

SOUNDS_DIR="/System/Library/Sounds"
ABSENT="Morse"

name=$(jq -r '.last_assistant_message // empty' | awk 'NF{l=$0} END{print l}' \
  | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//; s/^\*([a-z]+)\*$/\1/')

sound="$ABSENT"
if printf '%s' "$name" | grep -qE '^[a-z]+$'; then
  cap=$(printf '%s' "$name" | awk '{print toupper(substr($0,1,1)) substr($0,2)}')
  [ -f "$SOUNDS_DIR/${cap}.aiff" ] && sound="$cap"
fi

# Background afplay so the hook returns immediately and doesn't gate end-of-turn.
afplay "$SOUNDS_DIR/${sound}.aiff" </dev/null >/dev/null 2>&1 &

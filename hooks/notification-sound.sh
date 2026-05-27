#!/bin/bash
# Stop hook. Plays a macOS system sound when a response ends. An HTML-comment
# marker in the assistant's last message names the sound: `<!-- glass -->`
# → Glass.aiff. No marker → Morse. Marker with unknown name → Tink.

SOUNDS_DIR="/System/Library/Sounds"
ABSENT="Morse"
UNKNOWN="Tink"

name=$(jq -r '.last_assistant_message // empty' | grep -oE '<!-- [a-zA-Z]+ -->' | head -1 | sed -E 's/<!-- (.+) -->/\1/')

if [ -z "$name" ]; then
  sound="$ABSENT"
else
  sound=$(printf '%s' "$name" | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}')
  [ -f "$SOUNDS_DIR/${sound}.aiff" ] || sound="$UNKNOWN"
fi

# Background afplay so the hook returns immediately and doesn't gate end-of-turn.
afplay "$SOUNDS_DIR/${sound}.aiff" </dev/null >/dev/null 2>&1 &

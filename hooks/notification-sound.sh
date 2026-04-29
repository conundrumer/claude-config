#!/bin/bash
# Stop hook. Plays a macOS system sound when a response ends. An HTML-comment
# marker in the assistant's last message names the sound: `<!-- glass -->`
# → Glass.aiff. Missing or unknown name → Tink.

SOUNDS_DIR="/System/Library/Sounds"
DEFAULT="Tink"

latest_line()  { tail -n 200 "$1" | awk '/"type":"assistant"/{l=$0} END{print l}'; }
uuid_of()      { printf '%s' "$1" | grep -oE '"uuid":"[^"]+"' | head -1; }
marker_of()    { printf '%s' "$1" | grep -oE '<!-- [a-zA-Z]+ -->' | head -1 | sed 's/<!-- //; s/ -->//'; }
title_case()   { awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}'; }

resolve_sound() {
  local name sound
  name=$(marker_of "$1")
  [ -z "$name" ] && { printf '%s' "$DEFAULT"; return; }
  sound=$(printf '%s' "$name" | title_case)
  [ -f "$SOUNDS_DIR/${sound}.aiff" ] && printf '%s' "$sound" || printf '%s' "$DEFAULT"
}

transcript=$(jq -r '.transcript_path // empty')
sound="$DEFAULT"

if [ -n "$transcript" ] && [ -f "$transcript" ]; then
  # Stop fires before Claude Code flushes the final assistant line, so the
  # file may still hold the prior turn. Wait for the latest assistant `uuid`
  # to change, then read. Cap at ~1.5s.
  initial=$(uuid_of "$(latest_line "$transcript")")
  for _ in 1 2 3 4 5 6 7 8; do
    line=$(latest_line "$transcript")
    current=$(uuid_of "$line")
    [ -n "$current" ] && [ "$current" != "$initial" ] && break
    sleep 0.2
  done
  sound=$(resolve_sound "$line")
fi

afplay "$SOUNDS_DIR/${sound}.aiff" 2>/dev/null &

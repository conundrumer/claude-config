#!/bin/bash
# claude code status bar that shows:
# - current directory and git branch
# - current model
# - context usage %
# - prompt cache deadline
# - 5-hour and 7-day usage % with pacing targets

# Read Claude Code context from stdin
input=$(cat)

# linux and macos supported
[[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]] || (echo "Unsupported OS!" && exit)

# Extract information from Claude Code context
model_name=$(echo "$input" | jq -r '.model.display_name // "Claude"' | sed -E 's/.*(Opus|Sonnet|Haiku)([[:space:]]+[0-9]+(\.[0-9]+)?)?.*/\1\2/')
current_dir=$(echo "$input" | jq -r '.workspace.current_dir // ""')
context_pct=$(echo "$input" | jq -r '.context_window.used_percentage // 10' | cut -d. -f1)
# Get current working directory basename for display
if [ -n "$current_dir" ]; then
    dir_name=$(basename "$current_dir")
else
    dir_name=$(basename "$(pwd)")
fi

# Get git status if we're in a git repo
git_info=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git branch --show-current 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
    if [ -n "$branch" ]; then
        if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
            git_info=" ${branch}*"
        else
            git_info=" ${branch}"
        fi
    fi
fi

color_for_pct() {
    local pct=$1
    if [ "$pct" -ge 70 ]; then
        printf "\033[0;91m"  # bright red
    elif [ "$pct" -ge 45 ]; then
        printf "\033[0;33m"  # yellow
    else
        printf "\033[2;32m"  # dim, green
    fi
}

# Sessions can reset on :00 or :30, so round to the nearest half-hour and
# include minutes only when non-zero. Args: $1 epoch, $2 kind (5h|7d).
format_reset_label() {
    local epoch=$(( ($1 + 900) / 1800 * 1800 ))
    local kind=$2
    if [[ "$OSTYPE" == "darwin"* ]]; then
        local minute=$(date -r "$epoch" '+%M')
        local time_fmt='%-l%p'
        [ "$minute" = "30" ] && time_fmt='%-l:%M%p'
        if [ "$kind" = "7d" ]; then
            date -r "$epoch" "+%a, $time_fmt" | tr '[:upper:]' '[:lower:]' | sed 's/ //2'
        else
            date -r "$epoch" "+$time_fmt" | tr '[:upper:]' '[:lower:]' | tr -d ' '
        fi
    else
        local minute=$(date -d "@$epoch" '+%M')
        local time_fmt='%-Hh'
        [ "$minute" = "30" ] && time_fmt='%-H:%M'
        if [ "$kind" = "7d" ]; then
            date -d "@$epoch" "+%a:$time_fmt"
        else
            date -d "@$epoch" "+$time_fmt"
        fi
    fi
}

CTX_COLOR=$(color_for_pct "$context_pct")

# --- Prompt cache deadline (last API activity + 5min TTL) ---
# The newest assistant entry in the transcript tail marks the last API
# response. File mtime is only a fallback: resumes and hooks bump it without
# any API call. A future time is the cache window; a past time is when the
# cache went cold.
cache_part=""
transcript=$(echo "$input" | jq -r '.transcript_path // empty')
if [ -n "$transcript" ] && [ -f "$transcript" ]; then
    last_api=$(tail -n 50 "$transcript" 2>/dev/null | \
        jq -Rr 'fromjson? | select(.type=="assistant") | (.timestamp | sub("\\.[0-9]+Z$"; "Z") | fromdateiso8601)?' 2>/dev/null | tail -1)
    if [ -z "$last_api" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            last_api=$(stat -f %m "$transcript" 2>/dev/null)
        else
            last_api=$(stat -c %Y "$transcript" 2>/dev/null)
        fi
    fi
    if [ -n "$last_api" ]; then
        cache_deadline=$((last_api + 300))
        if [[ "$OSTYPE" == "darwin"* ]]; then
            cache_part=$(date -r "$cache_deadline" '+%-l:%M%p' | tr '[:upper:]' '[:lower:]')
        else
            cache_part=$(date -d "@$cache_deadline" '+%-l:%M%p' | tr '[:upper:]' '[:lower:]')
        fi
    fi
fi

# --- Usage limits (5-hour and 7-day) from statusline JSON (v2.1.80+) ---
USAGE_CACHE="$HOME/.claude/usage.json"

usage_5h=""
usage_7d=""
target_5h=""
target_7d=""

usage_5h=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty' 2>/dev/null | cut -d. -f1)
usage_7d=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty' 2>/dev/null | cut -d. -f1)
resets_5h=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty' 2>/dev/null)
resets_7d=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty' 2>/dev/null)

NOW_EPOCH=$(date +%s)

# 5-hour pacing target
if [ -n "$resets_5h" ]; then
    reset_epoch=$resets_5h
    window_secs=$((5 * 3600))
    start_epoch=$((reset_epoch - window_secs))
    elapsed=$((NOW_EPOCH - start_epoch))
    [ "$elapsed" -lt 0 ] && elapsed=0
    [ "$elapsed" -gt "$window_secs" ] && elapsed=$window_secs
    target_5h=$(( (elapsed * 100 + window_secs / 2) / window_secs))
    resets_5h_label=$(format_reset_label "$reset_epoch" 5h)
fi

# 7-day pacing target
if [ -n "$resets_7d" ]; then
    reset_epoch=$resets_7d
    window_secs=$((7 * 86400))
    start_epoch=$((reset_epoch - window_secs))
    elapsed=$((NOW_EPOCH - start_epoch))
    [ "$elapsed" -lt 0 ] && elapsed=0
    [ "$elapsed" -gt "$window_secs" ] && elapsed=$window_secs
    target_7d=$(( (elapsed * 100 + window_secs / 2) / window_secs))
    resets_7d_label=$(format_reset_label "$reset_epoch" 7d)
fi

# Compute seconds until reset
resets_in_5h="null"
resets_in_7d="null"
[ -n "$resets_5h" ] && resets_in_5h=$(( resets_5h - NOW_EPOCH ))
[ -n "$resets_7d" ] && resets_in_7d=$(( resets_7d - NOW_EPOCH ))

# Write to cache file for external tools (only if rate limit data is present)
[ -z "$usage_5h" ] && [ -z "$usage_7d" ] || \
jq -n \
  --argjson u5 "${usage_5h:-null}" \
  --argjson e5 "${target_5h:-null}" \
  --argjson r5 "${resets_5h:-null}" \
  --argjson ttl5 "${resets_in_5h}" \
  --argjson u7 "${usage_7d:-null}" \
  --argjson e7 "${target_7d:-null}" \
  --argjson r7 "${resets_7d:-null}" \
  --argjson ttl7 "${resets_in_7d}" \
  '{five_hour: {used_pct: $u5, elapsed_pct: $e5, resets_at_epoch: $r5, ttl_seconds: $ttl5}, seven_day: {used_pct: $u7, elapsed_pct: $e7, resets_at_epoch: $r7, ttl_seconds: $ttl7}}' > "$USAGE_CACHE" 2>/dev/null

# Build usage parts
usage_parts=""
if [ -n "$usage_5h" ]; then
    U5_COLOR=$(color_for_pct "$usage_5h")
    reset_label=""
    [ -n "$resets_5h_label" ] && reset_label="➞${resets_5h_label}"
    target_str=""
    [ -n "$target_5h" ] && target_str="/${target_5h}%"
    usage_parts="${U5_COLOR}5hr${reset_label} ${usage_5h}%${target_str}\033[0m"
fi
if [ -n "$usage_7d" ]; then
    U7_COLOR=$(color_for_pct "$usage_7d")
    reset_7d_label_str=""
    [ -n "$resets_7d_label" ] && reset_7d_label_str="➞${resets_7d_label}"
    target_str=""
    [ -n "$target_7d" ] && target_str="/${target_7d}%"
    [ -n "$usage_parts" ] && usage_parts="${usage_parts}\033[2m │ \033[0m"
    usage_parts="${usage_parts}${U7_COLOR}wk${reset_7d_label_str} ${usage_7d}%${target_str}\033[0m"
fi

# Single line output
line=""
# current path and git status
line+="\033[0;22m\033[32m${dir_name}\033[0;2m${git_info}"
# session cost and current model name
line+=" │ ${model_name}"
# model context status bar
line+=" │ ${CTX_COLOR}ctx ${context_pct}%\033[0m"
# prompt cache deadline
if [ -n "$cache_part" ]; then
    line+="\033[2m │ hot➞${cache_part}\033[0m"
fi
# 5 hour and 7-day usage bars
if [ -n "$usage_parts" ]; then
    line+="\033[2m │ \033[0m${usage_parts}"
fi
echo -e "$line"

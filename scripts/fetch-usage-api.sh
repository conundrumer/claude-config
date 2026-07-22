#!/bin/bash
# Fetches account usage from the Claude OAuth usage API and caches it at
# ~/.claude/usage-api.json as {"fetched_at": epoch, "data": <raw response>}.
# Skips the network call while the cache is younger than TTL_SECONDS.
# Pass --force to fetch regardless of cache age.
#
# The API is undocumented and the response shape can change. Consumers
# should parse defensively.
#
# Token source: macOS keychain item "Claude Code-credentials", with
# ~/.claude/.credentials.json as fallback. The token is read into a
# variable and never written to disk.

set -o pipefail

CACHE="$HOME/.claude/usage-api.json"
TTL_SECONDS=300
ENDPOINT="https://api.anthropic.com/api/oauth/usage"

if [ "$1" != "--force" ] && [ -f "$CACHE" ]; then
    now=$(date +%s)
    fetched_at=$(jq -r '.fetched_at // 0' "$CACHE" 2>/dev/null)
    if [ $((now - fetched_at)) -lt "$TTL_SECONDS" ]; then
        exit 0
    fi
fi

creds=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    creds=$(security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null)
fi
if [ -z "$creds" ] && [ -f "$HOME/.claude/.credentials.json" ]; then
    creds=$(cat "$HOME/.claude/.credentials.json")
fi
token=$(echo "$creds" | jq -r '.claudeAiOauth.accessToken // empty' 2>/dev/null)
if [ -z "$token" ]; then
    echo "fetch-usage-api: no OAuth token available" >&2
    exit 1
fi

tmp=$(mktemp "${TMPDIR:-/tmp}/usage-api.XXXXXX")
trap 'rm -f "$tmp"' EXIT

http_code=$(curl -sS --max-time 10 -o "$tmp" -w '%{http_code}' \
    -H "Authorization: Bearer $token" \
    -H "anthropic-beta: oauth-2025-04-20" \
    "$ENDPOINT" 2>/dev/null)

if [ "$http_code" != "200" ]; then
    echo "fetch-usage-api: HTTP $http_code from usage endpoint" >&2
    exit 1
fi
if ! jq -e . "$tmp" >/dev/null 2>&1; then
    echo "fetch-usage-api: response is not valid JSON" >&2
    exit 1
fi

jq --argjson t "$(date +%s)" '{fetched_at: $t, data: .}' "$tmp" > "$tmp.wrapped" \
    && mv "$tmp.wrapped" "$CACHE"

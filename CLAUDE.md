## Rate Limit Usage
`~/.claude/usage.json` is continuously updated with current rate limit data across the user's entire Claude account:
- `used` — percentage of quota consumed so far
- `elapsed` — percentage of the window's total time that has passed; compare with `used` to assess pacing
- `resets_at` — unix epoch (seconds) when the window resets
- `ttl` — seconds until reset

## Interaction Rules

- When the user says "ack", confirm your understanding so they can verify you understood correctly and clarify if needed. Do not make changes (edits, writes, creates) until the user confirms alignment.

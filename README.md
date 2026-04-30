# claude-config

Personal source-of-truth for `~/.claude/` configuration. Structure mirrors `~/.claude/`; `./sync.sh` deploys.

See [`CLAUDE.md`](CLAUDE.md) for the file map and sync details.

## Shell env

Not tracked here, but documented so future-me knows where to look:

- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` lives in `~/.zshenv`. Enables the `SendMessage` deferred tool (resume a spawned agent with full context). Must be a shell-level export — `settings.json` `env:` is parsed after the gate evaluates, so it has no effect. Source: [#35240](https://github.com/anthropics/claude-code/issues/35240#issuecomment-4282667930).

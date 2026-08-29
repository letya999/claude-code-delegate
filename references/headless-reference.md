# Claude Code headless reference

This skill follows Anthropic's Claude Code CLI (verified against `claude` 2.1.x on 2026-08-11):

- Headless invocation: `claude -p "..."` (also `--print`)
- Working directory: set as the subprocess working directory; grant tool access with `--add-dir <PATH>`
- Machine-readable output: `--output-format json` (one JSON object with a `result` field)
- Streaming alternative: `--output-format stream-json` (NDJSON events; needs `--verbose`)
- Model selection: `--model <MODEL>`
- Resumable sessions: `--session-id <UUID>` to pin a session, `--resume <ID>` or `--continue` to resume
- Permission policy: `--permission-mode <MODE>` for an explicit mode; the wrapper keeps it mutually exclusive with `--always-approve`
- Automated execution: `--dangerously-skip-permissions` (bypass all permission checks) or `--permission-mode acceptEdits`
- Restrict tools: `--allowedTools` / `--disallowedTools`
- Load MCP config: `--mcp-config <FILE>` (add `--strict-mcp-config` to use only those servers)

Authentication is expected to be preconfigured by the user through Claude login (subscription/OAuth) or `ANTHROPIC_API_KEY`. Never inspect or print credentials. If authentication fails, return Claude's error and ask the user to authenticate separately.

Notes:

- The JSON envelope from `--output-format json` includes `result`, session metadata, and cost/usage. The wrapper surfaces `result` as `response` and keeps the full object under `raw`.
- Default permission mode may refuse file edits in `-p` mode. Pass `--always-approve` to the wrapper (maps to `--dangerously-skip-permissions`) only when the user authorizes autonomous edits and the directory is trusted.
- Keep delegation one level deep: a delegated Claude instance should not spawn another `claude -p` in a loop.

Primary sources:

- [Claude Code CLI reference](https://docs.claude.com/en/docs/claude-code/cli-reference)
- [Claude Code headless / SDK usage](https://docs.claude.com/en/docs/claude-code/sdk)
- Local help: `claude --help`

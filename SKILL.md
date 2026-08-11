---
name: claude-code-delegate
description: Run Claude Code CLI as a headless delegate. Use when the user names Claude Code or claude, says "ask Claude", wants a Claude second opinion, or compares coding agents. Do NOT use for interactive sessions, other CLIs, or tasks not meant for delegation.
---

# Claude Code Delegate

Run Claude Code as a bounded headless subprocess (`claude -p`) and hand its final response back to the user. Keep the current project as the working directory unless the user specifies another directory.

## Anti-Rationalization

Trigger this skill when the user explicitly asks for Claude Code, a Claude subprocess, a Claude second opinion, or a comparison that needs Claude Code evidence. Do not skip it just because the current agent can do the task directly; the requested value is the separate Claude Code run.

Pause instead when Claude Code is missing or unauthenticated, the user wants an interactive session, the task requires exposing secrets, or the requested edits/commands exceed the user's authorization.

## Runtime Pre-Flight

Read [runtime-setup.md](references/runtime-setup.md) before invoking the wrapper. Verify Python 3.10+ and `claude` or `CLAUDE_BIN`; stop and report the missing prerequisite instead of inventing an installer or assuming a specific shell.

## Workflow

1. Clarify the delegated objective, scope, and whether Claude may edit files or run commands. Do not delegate secrets or expose protected files in the prompt.
2. Resolve the project directory to an absolute path. Prefer the current working directory. Verify it exists before starting.
3. Run the bundled wrapper with the Python command discovered by [runtime-setup.md](references/runtime-setup.md).
4. Read [headless-reference.md](references/headless-reference.md) when flags, sessions, output parsing, or authentication details are needed.

5. Report the wrapper's result, output-file path, exit status, and any stderr warning. A successful process is not proof that the requested change is correct: inspect the diff and run relevant tests independently when the delegated task changed files.
6. If the task is long-running, use a generous explicit timeout. Never create a hidden daemon, polling loop, or unbounded background process.

## Wrapper behavior

- `delegate_claude.py` invokes `claude` directly, never through a shell, and supports `CLAUDE_BIN` for an explicit executable path.
- It uses Claude Code headless mode with `-p` and `--output-format json`; the project is set as both the subprocess working directory and an allowed `--add-dir`. It adds `--dangerously-skip-permissions` only when `--always-approve` is requested, otherwise it runs with the default permission mode.
- It writes stdout, stderr, and a small result manifest to a temporary output directory, then prints the final captured response as JSON. The parsed `result` text from Claude's JSON envelope is surfaced under `response`.
- It returns nonzero for missing Claude, an invalid project directory, timeout, failed process, or malformed JSON. Do not hide these failures.
- Prefer a one-shot invocation. Use `--session-id` or `--resume` only when the user explicitly asks for a resumable Claude session.

## Safety and verification

- Do not read or print `ANTHROPIC_API_KEY`, OAuth tokens, `~/.claude` credentials, `.credentials.json`, `.env*`, private keys, or browser profiles.
- Do not add MCP servers, disable repository protections, publish code, push commits, or delete data unless the user explicitly asks for that exact action.
- Treat the nested Claude's report as unverified. Inspect changed files, `git diff`, and tests from the controlling agent.
- Avoid unbounded recursion: do not have a delegated Claude instance delegate again to Claude Code in a loop. Keep delegation one level deep unless the user asks otherwise.
- If `claude` is not found, tell the user to verify the official installation and PATH; do not install packages or run an installer automatically.

## Resources

Use `references/runtime-setup.md` for Python and CLI pre-flight, `scripts/delegate_claude.py` for deterministic invocation, and `references/headless-reference.md` for the documented Claude Code interface.

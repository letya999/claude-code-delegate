<p align="center">
  <strong>English</strong> · <a href="README.ru.md">Русский</a>
</p>

<p align="center">
  <h1 align="center">Claude Code Delegate</h1>
</p>

<p align="center">
  <a href="https://github.com/letya999/claude-code-delegate"><img src="https://img.shields.io/badge/status-active-brightgreen" alt="status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License: MIT"></a>
  <a href="https://skills.sh"><img src="https://img.shields.io/badge/skills.sh-discoverable-black" alt="skills.sh"></a>
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/cli-claude-purple" alt="CLI: claude">
</p>

Headless Claude Code CLI delegate skill by [Artem Letyushev](https://github.com/letya999).

The command is `scripts/delegate_claude.py`. The primary consumer is the controlling agent or orchestrator: every execution runs Claude Code once as a bounded, non-interactive subprocess (`claude -p`) and returns one structured JSON envelope.

---

## One objective, bounded subprocess, zero trust

The wrapper acts as a deterministic isolation layer between your controlling agent and the Claude Code CLI:

- **Single non-interactive execution:** Invokes `claude -p` directly via `subprocess.run(..., shell=False)` without interactive prompts.
- **Strict workspace scoping:** Sets subprocess working directory and adds `--add-dir <cwd>` to explicitly bound file access.
- **Envelope extraction:** Extracts the final response text from Claude's structured JSON envelope into a clean `response` field.
- **Zero-trust verification:** Outputs are unverified until independently confirmed by diffs and tests.
- **Credential isolation:** Never inspects or prints `ANTHROPIC_API_KEY`, `~/.claude` tokens, or `.env` files.

## Capability matrix

| Capability / Setting | Specification | Behavior & Guarantees |
|---|---|---|
| **Headless command** | `claude -p "<task>"` | Non-interactive execution in print mode |
| **Output format** | `--output-format json` | Structured envelope parsed into a top-level `response` string |
| **Workspace scoping** | `--add-dir <cwd>` | Grants Claude access to the target workspace directory |
| **Model selection** | `--model <name>` | Forwards specified model alias to Claude CLI |
| **Permission modes** | `--permission-mode <mode>` | Supports granular permission modes (`read-only`, `accept-edits`, etc.) |
| **Autonomous edits** | `--always-approve` | Passes `--dangerously-skip-permissions` (mutually exclusive with `--permission-mode`) |
| **Session resumption** | `--session-id` / `--resume` | Resumes existing conversation context when explicitly requested |
| **Executable override** | `CLAUDE_BIN` env var | Custom executable path before searching PATH |
| **Standard exit codes** | `0, 2, 65, 124, 126, 127` | Standardized error signaling |

## Install

With `npx skills`:

```bash
npx skills add letya999/claude-code-delegate
```

Or clone into an agent skill directory:

```bash
git clone https://github.com/letya999/claude-code-delegate.git .agents/skills/claude-code-delegate
```

## Quick Start

### POSIX (macOS, Linux, WSL)

```bash
python3 scripts/delegate_claude.py \
  --cwd "$PWD" \
  --task "Review this repository and report the highest-risk issue." \
  --timeout 45m
```

### Windows PowerShell

```powershell
py -3 .\scripts\delegate_claude.py `
  --cwd (Get-Location).Path `
  --task "Review this repository and report the highest-risk issue." `
  --timeout 45m
```

---

<details>
<summary>JSON Manifest Schema & Agent Integration</summary>

The wrapper writes `stdout.json`, `stderr.log`, and `result.json` into a temporary directory:

```json
{
  "tool": "claude",
  "cwd": "C:\\work\\repo",
  "exit_code": 0,
  "output_dir": "C:\\Temp\\claude-code-delegate-xyz",
  "stdout": "C:\\Temp\\claude-code-delegate-xyz\\stdout.json",
  "stderr": "C:\\Temp\\claude-code-delegate-xyz\\stderr.log",
  "response": "Extracted response from Claude JSON payload",
  "raw": {
    "result": "..."
  }
}
```

If Claude succeeds with exit code 0 but returns an empty response or malformed payload, the wrapper returns code `65`.

</details>

<details>
<summary>CLI Flags & Configuration Reference</summary>

| Flag | Type | Description |
|---|---|---|
| `--cwd` | Path (required) | Project working directory. Exits with `2` if directory does not exist. |
| `--task` | String (required) | Instruction / prompt to delegate. |
| `--timeout` | Duration (default: `45m`) | Timeout formatted as `90s`, `45m`, `2h`, or integer seconds. |
| `--model` | String | Model override passed to Claude. |
| `--permission-mode` | String | Sets Claude permission mode (e.g. `read-only`). |
| `--always-approve` | Flag | Passes `--dangerously-skip-permissions` for autonomous edits. |
| `--session-id` | String | Resumes conversation by session ID. |
| `--resume` | String | Alternate resume session flag. |
| `--output-dir` | Path | Custom artifact directory. |

</details>

<details>
<summary>Safety Posture & Credential Guardrails</summary>

- **No credential leaks:** Never reads or logs `ANTHROPIC_API_KEY`, OAuth tokens, or `.credentials.json`.
- **Default read permissions:** Bounded execution unless explicit permission flags are provided.
- **Anti-recursion rule:** Delegated Claude instances must not recursively spawn further delegate wrappers.

</details>

<details>
<summary>Independent Verification Protocol</summary>

Outputs are unverified. After delegated file modifications:

1. Inspect diffs: `git diff --stat` and `git diff`.
2. Execute tests outside the delegated agent: `pytest`, `npm test`, `cargo test`.
3. Check code formatting and linting.

</details>

<details>
<summary>Test Suite & Quality Checks</summary>

Run the test suite with standard library `unittest`:

```bash
python -m unittest discover -s tests -v
```

</details>

<details>
<summary>Agent Skill Entry Points</summary>

- [SKILL.md](SKILL.md) — Skill specification file.
- [QUICKSTART.md](QUICKSTART.md) — Quick usage guide.
- [references/runtime-setup.md](references/runtime-setup.md) — Runtime environment checks.
- [references/headless-reference.md](references/headless-reference.md) — Claude CLI headless reference.
- [.well-known/agent-skills/index.json](.well-known/agent-skills/index.json) — Discovery index for skills.sh.
- [dist/claude-code-delegate.zip](dist/claude-code-delegate.zip) — Discoverable archive artifact.

</details>

<details>
<summary>License</summary>

MIT License. See [LICENSE](LICENSE) for full text. Copyright (c) 2026 Artem Letyushev.

</details>

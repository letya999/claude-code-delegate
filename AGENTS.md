# Repository instructions

This repository maintains one portable Agent Skill: `claude-code-delegate`. It runs
`claude` as a bounded headless delegate and returns a JSON manifest.
All maintained repository content is written in English except `README.ru.md`,
the Russian translation.

## Read before editing

Read [SKILL.md](SKILL.md), [README.md](README.md), [QUICKSTART.md](QUICKSTART.md),
`scripts/delegate_claude.py`, and `references/`.

## Wrapper contract

- Invoke via `python scripts/delegate_claude.py --cwd <abs-dir> --task <text> [--timeout ...]`.
- `subprocess.run([...], shell=False)` only — no shell.
- Honor `CLAUDE_BIN` before PATH and well-known install locations.
- Print a JSON manifest; the human-facing result lives under `response`.
- Exit codes: `2` bad cwd, `127` binary missing, `124` timeout, `126` start
  failure, `65` missing/unusable response after claimed success, else the child
  process exit code.
- Temp output dirs use the `claude-code-delegate-` prefix.

## Safety posture

- Default: no auto-approve, no full-access, no permission bypass flags.
- Never read or print credentials: API keys, tokens, `.env*`, `auth.json`,
  private keys, browser profiles, vendor credential stores.
- Delegated output is unverified — check `git diff` and tests before accepting.
- A delegated agent must not re-delegate to the same CLI in a loop.

## Validation and packaging

Run `python -m unittest discover -s tests -v` before publishing changes.
Keep `index.json` and `.well-known/agent-skills/index.json` in sync; rebuild
`dist/` and refresh the sha256 digest whenever the payload changes.

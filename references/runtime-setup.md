# Runtime setup

Use this check before running `scripts/delegate_claude.py`. The wrapper requires Python 3.10+ and an installed/authenticated Claude Code CLI.

## POSIX shell: macOS, Linux, WSL

```sh
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD=python
else
  echo "FAIL: Python 3.10+ not found"
  exit 127
fi

"$PYTHON_CMD" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' || {
  echo "FAIL: Python 3.10+ required"
  exit 127
}

command -v claude >/dev/null 2>&1 || [ -n "${CLAUDE_BIN:-}" ] || {
  echo "FAIL: claude not found; set CLAUDE_BIN or update PATH"
  exit 127
}

"$PYTHON_CMD" "<skill-dir>/scripts/delegate_claude.py" \
  --cwd "<absolute-project-path>" \
  --task "<delegated task>" \
  --timeout 45m
```

## Windows PowerShell

```powershell
$PythonExe = $null
$PythonArgs = @()
if (Get-Command py -ErrorAction SilentlyContinue) {
  $PythonExe = "py"
  $PythonArgs = @("-3")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $PythonExe = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
  $PythonExe = "python3"
} else {
  throw "Python 3.10+ not found"
}

& $PythonExe @PythonArgs -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
if ($LASTEXITCODE -ne 0) { throw "Python 3.10+ required" }

if (-not $env:CLAUDE_BIN -and -not (Get-Command claude -ErrorAction SilentlyContinue)) {
  throw "claude not found; set CLAUDE_BIN or update PATH"
}

& $PythonExe @PythonArgs "<skill-dir>\scripts\delegate_claude.py" `
  --cwd "<absolute-project-path>" `
  --task "<delegated task>" `
  --timeout 45m
```

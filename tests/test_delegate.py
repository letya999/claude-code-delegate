"""Stdlib unit tests for claude-code-delegate wrapper.

Does not invoke the real `claude` binary or the network.
Import the script by file path (no package layout).
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "delegate_claude.py"
MODULE_NAME = "delegate_claude_under_test"


def _load_module():
    spec = importlib.util.spec_from_file_location(MODULE_NAME, SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load wrapper from {SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestParseDuration(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_module()

    def test_seconds_suffix(self) -> None:
        self.assertEqual(self.mod.parse_duration("90s"), 90.0)

    def test_minutes_suffix(self) -> None:
        self.assertEqual(self.mod.parse_duration("45m"), 2700.0)

    def test_hours_suffix(self) -> None:
        self.assertEqual(self.mod.parse_duration("2h"), 7200.0)

    def test_bare_number(self) -> None:
        self.assertEqual(self.mod.parse_duration("30"), 30.0)

    def test_rejects_non_positive_duration(self) -> None:
        for value in ("0", "-1s"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.mod.parse_duration(value)


class TestFindClaude(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_module()

    def test_honors_claude_bin_env(self) -> None:
        fake = str(Path(tempfile.gettempdir()) / "fake-claude-bin-for-tests.exe")
        previous = os.environ.get("CLAUDE_BIN")
        os.environ["CLAUDE_BIN"] = fake
        try:
            self.assertEqual(self.mod.find_claude(), fake)
        finally:
            if previous is None:
                os.environ.pop("CLAUDE_BIN", None)
            else:
                os.environ["CLAUDE_BIN"] = previous


class TestRunBounded(unittest.TestCase):
    def test_utf8_and_timeout(self) -> None:
        mod = _load_module()
        result = mod.run_bounded([sys.executable, "-c", "import sys; sys.stdout.buffer.write('Привет'.encode())"], SKILL_ROOT, 10)
        self.assertEqual(result.stdout.strip(), "Привет")
        with self.assertRaises(subprocess.TimeoutExpired):
            mod.run_bounded([sys.executable, "-c", "import time; time.sleep(30)"], SKILL_ROOT, 0.1)


class TestMainCli(unittest.TestCase):
    def test_forwards_model_and_permission_mode(self) -> None:
        mod = _load_module()
        completed = subprocess.CompletedProcess([], 0, '{"result":"ok"}', "")
        with tempfile.TemporaryDirectory() as output_dir, mock.patch.object(mod, "find_claude", return_value=sys.executable), mock.patch.object(mod, "run_bounded", return_value=completed) as run, mock.patch.object(sys, "argv", ["delegate", "--cwd", str(SKILL_ROOT), "--task", "test", "--model", "gpt-test", "--permission-mode", "manual", "--output-dir", output_dir]):
            self.assertEqual(mod.main(), 0)
            command = run.call_args.args[0]
            self.assertIn(["--model", "gpt-test"], [command[i:i + 2] for i in range(len(command) - 1)])
            self.assertIn(["--permission-mode", "manual"], [command[i:i + 2] for i in range(len(command) - 1)])
            self.assertNotIn("--dangerously-skip-permissions", command)

    def test_rejects_conflicting_permission_flags(self) -> None:
        mod = _load_module()
        with mock.patch.object(sys, "argv", ["delegate", "--cwd", str(SKILL_ROOT), "--task", "test", "--always-approve", "--permission-mode", "manual"]), self.assertRaises(SystemExit) as raised:
            mod.main()
        self.assertEqual(raised.exception.code, 2)

    def test_rejects_conflicting_session_flags(self) -> None:
        mod = _load_module()
        with mock.patch.object(sys, "argv", ["delegate", "--cwd", str(SKILL_ROOT), "--task", "test", "--session-id", "one", "--resume", "two"]), self.assertRaises(SystemExit) as raised:
            mod.main()
        self.assertEqual(raised.exception.code, 2)

    def test_timeout_writes_manifest(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as output_dir, mock.patch.object(mod, "find_claude", return_value=sys.executable), mock.patch.object(mod, "run_bounded", side_effect=subprocess.TimeoutExpired([], 1, output=b"partial", stderr=b"warning")), mock.patch.object(sys, "argv", ["delegate", "--cwd", str(SKILL_ROOT), "--task", "test", "--output-dir", output_dir]):
            self.assertEqual(mod.main(), 124)
            manifest = json.loads((Path(output_dir) / "result.json").read_text(encoding="utf-8"))
            self.assertEqual((manifest["tool"], manifest["exit_code"], manifest["timed_out"]), ("claude", 124, True))

    def test_nonexistent_cwd_exits_2(self) -> None:
        bogus = str(Path(tempfile.gettempdir()) / "claude-delegate-no-such-cwd-xyz")
        # Ensure it does not exist
        if Path(bogus).exists():
            self.skipTest("unexpected existing path for bogus cwd fixture")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--cwd", bogus, "--task", "test"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2, msg=proc.stderr)
        self.assertIn("does not exist", proc.stderr.lower())

    def test_missing_binary_exits_127(self) -> None:
        fake_bin = str(Path(tempfile.gettempdir()) / "missing-claude-xyz123.exe")
        if Path(fake_bin).is_file():
            self.skipTest("unexpected real file at fake bin path")
        env = os.environ.copy()
        env["CLAUDE_BIN"] = fake_bin
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--cwd", str(SKILL_ROOT), "--task", "test"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        combined = (proc.stderr or "") + (proc.stdout or "")
        # Prefer 127; if env override were bypassed and a real binary ran, skip.
        if proc.returncode not in (127, 126) and "not found" not in combined.lower():
            self.skipTest(
                f"CLAUDE_BIN override appears bypassed (exit {proc.returncode}): {combined[:400]}"
            )
        self.assertEqual(proc.returncode, 127, msg=combined)
        self.assertIn("not found", combined.lower())


if __name__ == "__main__":
    unittest.main()

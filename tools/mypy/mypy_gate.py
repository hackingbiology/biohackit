"""Fail on any mypy error in the strict backend apps listed in tools/mypy/strict_apps.txt.

mypy and django-stubs (pinned) run in a throwaway `uv run --isolated` environment built
from backend's locked dependencies, so they are never installed into backend/.venv
(scanned by the licence gate). Config: tools/mypy/mypy.ini (strict, django-stubs plugin).
Exit codes: 0 type-clean, 1 type errors, 2 the check could not run (fail closed).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPS_FILE = ROOT / "tools" / "mypy" / "strict_apps.txt"
CONFIG = "tools/mypy/mypy.ini"
MYPY = "mypy==2.4.1"
DJANGO_STUBS = "django-stubs==6.1.2"
TIMEOUT_SECONDS = 900
ERROR_LINE = re.compile(
    r"^(?P<where>[^\s:][^:]*(?::\d+(?::\d+)?)?): error: (?P<msg>.+)$"
)
SUMMARY_OK = re.compile(r"^Success: no issues found in \d+ source files?$", re.M)
SUMMARY_BAD = re.compile(r"^Found \d+ errors? in \d+ files?", re.M)


class GateError(Exception):
    """The check could not run or its output could not be trusted."""


def read_apps(path: Path = APPS_FILE, root: Path = ROOT) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise GateError(f"cannot read {path}: {exc}") from exc
    apps = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]
    if not apps:
        raise GateError(f"{path} lists no app")
    for app in apps:
        if not (root / app).is_dir():
            raise GateError(f"strict app path does not exist: {app}")
    return apps


def build_command(uv: str, apps: list[str]) -> list[str]:
    command = [uv, "run", "--project", "backend", "--isolated", "--frozen"]
    command += ["--with", MYPY, "--with", DJANGO_STUBS]
    command += [
        "python",
        "-m",
        "mypy",
        "--config-file",
        CONFIG,
        "--show-column-numbers",
    ]
    command += ["--no-color-output", "--hide-error-context"]
    return [*command, *apps]


def run_mypy(uv: str, apps: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            build_command(uv, apps),
            capture_output=True,
            text=True,
            check=False,
            cwd=ROOT,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise GateError(f"mypy timed out after {TIMEOUT_SECONDS}s") from exc
    except OSError as exc:
        raise GateError(f"mypy could not start: {exc}") from exc


def parse(done: subprocess.CompletedProcess[str]) -> list[str]:
    """Return the error lines; raise GateError unless the output is trustworthy."""
    out = done.stdout
    errors = [
        f"{m['where']}: {m['msg']}"
        for m in (ERROR_LINE.match(ln) for ln in out.splitlines())
        if m
    ]
    if done.returncode == 0 and SUMMARY_OK.search(out) and not errors:
        return []
    if done.returncode == 1 and errors and SUMMARY_BAD.search(out):
        return errors
    raise GateError(
        f"mypy exited {done.returncode} with unexpected output: "
        f"{(done.stderr.strip() or out.strip())[-500:]}"
    )


def main() -> int:
    uv = shutil.which("uv")
    try:
        if uv is None:
            raise GateError("uv not found on PATH")
        apps = read_apps()
        errors = parse(run_mypy(uv, apps))
    except GateError as exc:
        print(f"mypy gate cannot run: {exc}")
        return 2
    if errors:
        for line in errors:
            print(f"  {line}")
        print(f"mypy gate: {len(errors)} type error(s) in {', '.join(apps)}")
        return 1
    print(f"mypy gate: strict apps type-clean: {', '.join(apps)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

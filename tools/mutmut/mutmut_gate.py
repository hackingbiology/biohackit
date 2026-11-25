"""Fail on any surviving mutant in the numeric modules listed in tools/mutmut/targets.txt.

mutmut (pinned) runs in a throwaway `uv run --isolated` environment built from backend's
locked dependencies, so it is never installed into backend/.venv (scanned by the licence
gate) or backend/uv.lock. The run happens in a scratch copy of backend/ in a temp
directory, so the worktree is left clean (no mutants/ directory, no cache).

targets.txt: one target per line, `<module path> <test file> [<test file> ...]`, paths
relative to the repo root; `#` starts a comment.
accepted_survivors.txt: `<mutant-id> # <reason>`; a reason is mandatory.
Exit codes: 0 every mutant killed or accepted, 1 unaccepted survivor,
2 the run could not complete (fail closed).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS_FILE = ROOT / "tools" / "mutmut" / "targets.txt"
ACCEPTED_FILE = ROOT / "tools" / "mutmut" / "accepted_survivors.txt"
MUTMUT = "mutmut==3.8.1"
BACKEND = "backend"
TIMEOUT_SECONDS = 1800
CAUGHT = frozenset({"killed", "timeout"})
SURVIVED = frozenset({"survived", "no tests"})
RESULT_LINE = re.compile(r"^\s+(?P<id>[\w.]+): (?P<status>[a-z][a-z ]*)$")
COPY_IGNORE = shutil.ignore_patterns(
    ".venv", "__pycache__", "mutants", ".pytest_cache", ".mypy_cache", ".ruff_cache"
)


class GateError(Exception):
    """The mutation run could not complete or its output could not be trusted."""


@dataclass(frozen=True)
class Target:
    path: str
    tests: tuple[str, ...]

    @property
    def module(self) -> str:
        """Dotted module name as mutmut reports it, e.g. terminology.services."""
        return (
            self.path.removeprefix(f"{BACKEND}/").removesuffix(".py").replace("/", ".")
        )


def _content_lines(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise GateError(f"cannot read {path}: {exc}") from exc
    return [
        ln.strip()
        for ln in text.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]


def read_targets(path: Path = TARGETS_FILE, root: Path = ROOT) -> list[Target]:
    lines = _content_lines(path)
    if not lines:
        raise GateError(f"{path} lists no target")
    targets = []
    for line in lines:
        target, *tests = line.split()
        if not target.startswith(f"{BACKEND}/") or not target.endswith(".py"):
            raise GateError(f"target must be a {BACKEND}/**/*.py file: {target}")
        if not tests:
            raise GateError(f"target has no test file: {target}")
        for item in (target, *tests):
            if not (root / item).is_file():
                raise GateError(f"path does not exist: {item}")
        targets.append(
            Target(target, tuple(t.removeprefix(f"{BACKEND}/") for t in tests))
        )
    return targets


def read_accepted(path: Path = ACCEPTED_FILE) -> dict[str, str]:
    accepted: dict[str, str] = {}
    for line in _content_lines(path):
        mutant, sep, reason = line.partition("#")
        mutant, reason = mutant.strip(), reason.strip()
        if not sep or not reason or not mutant or " " in mutant:
            raise GateError(
                f"accepted survivor needs `<mutant-id> # <reason>`: {line!r}"
            )
        accepted[mutant] = reason
    return accepted


def mutmut_config(targets: list[Target], packages: list[str]) -> str:
    """TOML appended to the scratch pyproject.toml.

    `source_paths` lists every package so the scratch copy shadows the original ones, and
    pytest-django must not add the original project dir to sys.path (it would import
    unmutated code and mutmut would see no trampoline hit).
    """
    tests = sorted({t for target in targets for t in target.tests})
    only = [t.path.removeprefix(f"{BACKEND}/") for t in targets]
    return (
        "\n[tool.mutmut]\n"
        f"source_paths = {json.dumps(packages)}\n"
        f"only_mutate = {json.dumps(only)}\n"
        f"pytest_add_cli_args_test_selection = {json.dumps(tests)}\n"
        'pytest_add_cli_args = ["-o", "django_find_project=false"]\n'
    )


def prepare_scratch(scratch: Path, targets: list[Target], root: Path = ROOT) -> None:
    try:
        shutil.copytree(root / BACKEND, scratch, ignore=COPY_IGNORE)
        packages = sorted(
            p.name for p in scratch.iterdir() if (p / "__init__.py").is_file()
        )
        with (scratch / "pyproject.toml").open("a", encoding="utf-8") as handle:
            handle.write(mutmut_config(targets, packages))
    except OSError as exc:
        raise GateError(f"cannot prepare scratch copy: {exc}") from exc


def run_mutmut(uv: str, scratch: Path, *args: str) -> subprocess.CompletedProcess[str]:
    command = [uv, "run", "--project", str(scratch), "--isolated", "--frozen"]
    command += ["--with", MUTMUT, "mutmut", *args]
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=scratch,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise GateError(f"mutmut {args[0]} timed out after {TIMEOUT_SECONDS}s") from exc
    except OSError as exc:
        raise GateError(f"mutmut could not start: {exc}") from exc


def _require_ok(done: subprocess.CompletedProcess[str], what: str) -> str:
    if done.returncode != 0:
        tail = (done.stdout.strip() or done.stderr.strip())[-500:]
        raise GateError(f"mutmut {what} exited {done.returncode}: {tail}")
    return done.stdout


def parse_results(output: str) -> dict[str, str]:
    """Map mutant id -> status from `mutmut results --all true`."""
    results = {}
    for line in output.splitlines():
        match = RESULT_LINE.match(line)
        if match:
            results[match["id"]] = match["status"].strip()
    if not results:
        raise GateError("mutmut results listed no mutant")
    return results


def tally(
    targets: list[Target], results: dict[str, str]
) -> dict[str, tuple[int, int, list[str]]]:
    """Per target path: (caught, total, surviving ids). Unknown statuses fail closed."""
    tallied = {}
    claimed: set[str] = set()
    for target in targets:
        ids = [m for m in results if m.startswith(f"{target.module}.")]
        if not ids:
            raise GateError(f"mutmut produced no mutant for {target.path}")
        claimed.update(ids)
        survivors = [m for m in ids if results[m] in SURVIVED]
        caught = [m for m in ids if results[m] in CAUGHT]
        if len(survivors) + len(caught) != len(ids):
            odd = sorted({results[m] for m in ids} - CAUGHT - SURVIVED)
            raise GateError(f"{target.path}: mutants not finished or unreliable: {odd}")
        tallied[target.path] = (len(caught), len(ids), survivors)
    if set(results) - claimed:
        raise GateError("mutmut mutated a module that is not a listed target")
    return tallied


def show_diff(uv: str, scratch: Path, mutant: str) -> str:
    try:
        return _require_ok(
            run_mutmut(uv, scratch, "show", mutant), f"show {mutant}"
        ).strip()
    except GateError as exc:
        return f"(diff unavailable: {exc})"


def evaluate(
    uv: str, scratch: Path, targets: list[Target], accepted: dict[str, str]
) -> tuple[list[str], list[str]]:
    """Run mutmut; return (report lines, unaccepted survivor lines)."""
    _require_ok(run_mutmut(uv, scratch, "run"), "run")
    results = parse_results(
        _require_ok(run_mutmut(uv, scratch, "results", "--all", "true"), "results")
    )
    report, failures = [], []
    for path, (caught, total, survivors) in tally(targets, results).items():
        pending = [m for m in survivors if m not in accepted]
        report.append(
            f"  {path}: {caught}/{total} killed, {len(survivors) - len(pending)} accepted"
        )
        for mutant in pending:
            failures.append(
                f"  {path}: surviving mutant {mutant}\n{show_diff(uv, scratch, mutant)}"
            )
    return report, failures


def main() -> int:
    uv = shutil.which("uv")
    try:
        if uv is None:
            raise GateError("uv not found on PATH")
        targets = read_targets(TARGETS_FILE)
        accepted = read_accepted(ACCEPTED_FILE)
        with tempfile.TemporaryDirectory(prefix="mutmut-gate-") as tmp:
            scratch = Path(tmp) / BACKEND
            prepare_scratch(scratch, targets)
            report, failures = evaluate(uv, scratch, targets, accepted)
    except GateError as exc:
        print(f"mutmut gate cannot run: {exc}")
        return 2
    print("\n".join(report))
    if failures:
        print("\n".join(failures))
        print(
            f"mutmut gate: {len(failures)} surviving mutant(s) not in accepted_survivors.txt"
        )
        return 1
    print(f"mutmut gate: all mutants killed or accepted in {len(targets)} target(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

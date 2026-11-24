"""Fail when a production dependency has an AGPL-3.0-incompatible or unknown licence.

Backend: installed pip metadata of backend/.venv. Frontend: `pnpm licenses list --prod --json`.
The allow-list mirrors the licence table in docs/ecosystem/README.md; anything else is unknown.
"""

from __future__ import annotations

import glob
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from importlib.metadata import Distribution
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERRIDES = Path(__file__).with_name("overrides.toml")

# SPDX ids whose AGPL-3.0 verdict is "yes" in docs/ecosystem/README.md.
ALLOWED = frozenset(
    {
        "MIT",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "Apache-2.0",
        "LGPL-3.0-only",
        "LGPL-3.0-or-later",
        "AGPL-3.0-only",
        "AGPL-3.0-or-later",
        "MPL-2.0",
        "CC0-1.0",
        "ISC",
        "0BSD",
        "PSF-2.0",
    }
)
# Allowed only via a documented per-version override: CC-BY-4.0 (data, docs only) and MIT-0 (compatibility unverified, question Q12).
OVERRIDE_ONLY = frozenset(["CC-BY-4.0", "MIT-0"])
# Known-incompatible: proprietary or source-available terms.
INCOMPATIBLE = frozenset({"SSPL-1.0", "BUSL-1.1", "Elastic-2.0", "Proprietary"})

ALIASES = {
    "MIT": "MIT",
    "MIT LICENSE": "MIT",
    "EXPAT": "MIT",
    "BSD-2-CLAUSE": "BSD-2-Clause",
    "BSD-3-CLAUSE": "BSD-3-Clause",
    "APACHE-2.0": "Apache-2.0",
    "APACHE 2.0": "Apache-2.0",
    "LGPL-3.0": "LGPL-3.0-only",
    "LGPL-3.0-ONLY": "LGPL-3.0-only",
    "LGPL-3.0-OR-LATER": "LGPL-3.0-or-later",
    "AGPL-3.0": "AGPL-3.0-only",
    "AGPL-3.0-ONLY": "AGPL-3.0-only",
    "AGPL-3.0-OR-LATER": "AGPL-3.0-or-later",
    "MPL-2.0": "MPL-2.0",
    "CC0-1.0": "CC0-1.0",
    "ISC": "ISC",
    "0BSD": "0BSD",
    "MIT-0": "MIT-0",
    "PSF-2.0": "PSF-2.0",
    "CC-BY-4.0": "CC-BY-4.0",
    "SSPL-1.0": "SSPL-1.0",
    "BUSL-1.1": "BUSL-1.1",
    "ELASTIC-2.0": "Elastic-2.0",
    "PROPRIETARY": "Proprietary",
}
CLASSIFIER_PREFIX = "License :: "
CLASSIFIER_ALIASES = {
    "OSI Approved :: MIT License": "MIT",
    "OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0",
    "OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)": "LGPL-3.0-only",
    "OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)": "LGPL-3.0-or-later",
    "OSI Approved :: GNU Affero General Public License v3": "AGPL-3.0-only",
    "OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)": "AGPL-3.0-or-later",
    "Other/Proprietary License": "Proprietary",
}
MAX_LICENCE_NAME = 200  # longer "License" fields are full licence texts, not names


@dataclass(frozen=True)
class Package:
    ecosystem: str
    name: str
    version: str
    raw: str


def _atoms(expression: str) -> list[list[str]] | None:
    """Split an SPDX expression into an AND of ORs of normalised ids; None if any id is unrecognised."""
    cleaned = expression.replace("(", " ").replace(")", " ").strip()
    result: list[list[str]] = []
    for conjunct in re.split(r"\s+AND\s+", cleaned, flags=re.IGNORECASE):
        options: list[str] = []
        for token in re.split(r"\s+OR\s+|/", conjunct, flags=re.IGNORECASE):
            spdx = ALIASES.get(token.strip().upper())
            if spdx is None:
                return None
            options.append(spdx)
        result.append(options)
    return result


def classify(raw: str, extra_allowed: frozenset[str] = frozenset()) -> str:
    """Return 'allowed', 'incompatible' or 'unknown' for a raw licence string."""
    atoms = _atoms(raw) if raw.strip() else None
    if atoms is None:
        return "unknown"
    verdicts = []
    for options in atoms:
        if any(o in ALLOWED or o in extra_allowed for o in options):
            verdicts.append("allowed")
        elif all(o in INCOMPATIBLE for o in options):
            verdicts.append("incompatible")
        else:
            verdicts.append("unknown")
    for bad in ("incompatible", "unknown"):
        if bad in verdicts:
            return bad
    return "allowed"


def load_overrides(path: Path = OVERRIDES) -> dict[tuple[str, str], str]:
    """Map (package, version) to the SPDX licence of a documented override."""
    if not path.exists():
        return {}
    out: dict[tuple[str, str], str] = {}
    for entry in tomllib.loads(path.read_text()).get("override", []):
        missing = {"package", "version", "licence", "source_url"} - entry.keys()
        if missing:
            raise ValueError(f"override {entry} lacks {sorted(missing)}")
        out[(entry["package"].lower(), entry["version"])] = entry["licence"]
    return out


def verdict(pkg: Package, overrides: dict[tuple[str, str], str]) -> str:
    override = overrides.get((pkg.name.lower(), pkg.version))
    if override is not None:
        return classify(override, OVERRIDE_ONLY)
    return classify(pkg.raw)


def dist_licence(dist: Distribution) -> str:
    """License-Expression, then a short License field, then 'License ::' classifiers."""
    meta = dist.metadata
    expression = meta.get("License-Expression")
    if expression:
        return expression
    text = (meta.get("License") or "").strip()
    if (
        text
        and text.upper() != "UNKNOWN"
        and len(text) <= MAX_LICENCE_NAME
        and "\n" not in text
    ):
        return text
    found = []
    for classifier in meta.get_all("Classifier") or []:
        if (
            classifier.startswith(CLASSIFIER_PREFIX)
            and classifier != CLASSIFIER_PREFIX + "OSI Approved"
        ):
            name = classifier.removeprefix(CLASSIFIER_PREFIX)
            found.append(CLASSIFIER_ALIASES.get(name, name))
    return " AND ".join(found)


def backend_packages(venv: Path = ROOT / "backend" / ".venv") -> list[Package]:
    paths = glob.glob(str(venv / "lib" / "python*" / "site-packages"))
    return [
        Package("backend", dist.metadata["Name"], dist.version, dist_licence(dist))
        for dist in Distribution.discover(path=paths)
    ]


def frontend_packages() -> list[Package]:
    if not (ROOT / "frontend" / "package.json").exists():
        return []
    proc = subprocess.run(
        [
            "pnpm",
            "--dir",
            str(ROOT / "frontend"),
            "licenses",
            "list",
            "--prod",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return [
        Package("frontend", item["name"], version, licence)
        for licence, items in json.loads(proc.stdout).items()
        for item in items
        for version in item["versions"]
    ]


def offenders(
    pkgs: list[Package], overrides: dict[tuple[str, str], str]
) -> list[tuple[Package, str]]:
    return [(p, v) for p in pkgs if (v := verdict(p, overrides)) != "allowed"]


def main() -> int:
    overrides = load_overrides()
    backend, frontend = backend_packages(), frontend_packages()
    if not backend:
        print(
            "licence gate: no backend packages found under backend/.venv; failing closed"
        )
        return 1
    bad = offenders(backend + frontend, overrides)
    print(
        f"licence gate: checked {len(backend)} backend and {len(frontend)} frontend packages"
    )
    for pkg, v in bad:
        print(f"  {v.upper()}: {pkg.ecosystem} {pkg.name} {pkg.version}: {pkg.raw!r}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

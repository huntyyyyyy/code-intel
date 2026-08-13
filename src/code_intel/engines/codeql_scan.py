"""CodeQL named-check stub. engine=codeql. Does not build a database in V1."""

from __future__ import annotations

import shutil
from pathlib import Path

from code_intel.claims import Claim

CODEQL_PREFIX = "codeql:"


def is_codeql_check(check: str) -> bool:
    return check.strip().startswith(CODEQL_PREFIX)


def rule_id(check: str) -> str:
    return check.strip()[len(CODEQL_PREFIX) :].strip()


def verify_codeql(plant: Path, check: str) -> tuple[int, list[Claim], list[str]]:
    rule = rule_id(check)
    if not rule:
        return 2, [], ["codeql check is missing a rule id after 'codeql:'."]
    exe = shutil.which("codeql")
    marker = plant / "qlpack.yml"
    if marker.is_file():
        file_rel = "qlpack.yml"
    elif (plant / "build.gradle").is_file():
        file_rel = "build.gradle"
    else:
        file_rel = "gradlew"
    claim = Claim(
        subject=rule,
        predicate="ENGINE_ABSENT",
        object=None,
        file=file_rel,
        line=1,
        engine="codeql",
        provenance="unproven",
        excerpt="V1 does not run CodeQL. Install codeql and keep this check id.",
    )
    notes = [
        f"codeql on PATH: {'yes' if exe else 'no'}",
        "V1 verify for CodeQL is a stub; compile/test are the executed engines.",
    ]
    return 2, [claim], notes

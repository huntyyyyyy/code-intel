"""Gradle wrapper runner. engine=gradle-test. Never shells a free-form command."""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from code_intel.claims import Claim
from code_intel.settings import Settings, relative_to_plant

COMPILE_CHECK = "compile"
TEST_PREFIX = "test:"
TIMEOUT_COMPILE_SEC = 180
TIMEOUT_TEST_SEC = 300
OUTPUT_TAIL = 40
JAVA_LOC = re.compile(
    r"(?P<path>(?:[A-Za-z]:)?[^\s:]+\.java):(?P<line>\d+)"
)
CHECK_RE = re.compile(r"^(compile|test:[A-Za-z0-9_.*$]+)$")


class VerifyError(ValueError):
    """Malformed verify check."""


@dataclass(frozen=True)
class GradleRun:
    exit_code: int
    output: str
    command: tuple[str, ...]


def parse_check(check: str) -> tuple[str, str | None]:
    text = check.strip()
    if not CHECK_RE.match(text):
        raise VerifyError(
            "check must be 'compile' or 'test:<Gradle --tests filter>'."
        )
    if text == COMPILE_CHECK:
        return COMPILE_CHECK, None
    return "test", text[len(TEST_PREFIX) :]


def find_wrapper(plant: Path) -> Path | None:
    names = ("gradlew.bat", "gradlew") if os.name == "nt" else ("gradlew", "gradlew.bat")
    for name in names:
        candidate = plant / name
        if candidate.is_file():
            return candidate
    return None


def find_build_file(plant: Path) -> Path | None:
    for name in ("build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"):
        candidate = plant / name
        if candidate.is_file():
            return candidate
    return None


def _env_with_java(settings: Settings) -> dict[str, str]:
    env = os.environ.copy()
    if settings.java_home is not None:
        env["JAVA_HOME"] = str(settings.java_home)
        tool_bin = settings.java_home / "bin"
        env["PATH"] = str(tool_bin) + os.pathsep + env.get("PATH", "")
    return env


def run_gradle(settings: Settings, args: list[str], timeout: int) -> GradleRun:
    wrapper = find_wrapper(settings.plant_root)
    if wrapper is None:
        raise VerifyError("no gradlew/gradlew.bat under CODE_INTEL_ROOT")
    command = [str(wrapper), *args]
    completed = subprocess.run(
        command,
        cwd=settings.plant_root,
        env=_env_with_java(settings),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    output = (completed.stdout or "") + "\n" + (completed.stderr or "")
    return GradleRun(
        exit_code=completed.returncode,
        output=output,
        command=tuple(command),
    )


def _snippet(output: str) -> str:
    lines = [line for line in output.splitlines() if line.strip()]
    return "\n".join(lines[-OUTPUT_TAIL:])[:800]


def claims_from_output(
    *,
    settings: Settings,
    subject: str,
    predicate_ok: str,
    predicate_fail: str,
    run: GradleRun,
) -> list[Claim]:
    build = find_build_file(settings.plant_root) or find_wrapper(settings.plant_root)
    if build is None:
        build = settings.plant_root / "gradlew"
    rel = relative_to_plant(build, settings.plant_root)
    if run.exit_code == 0:
        return [
            Claim(
                subject=subject,
                predicate=predicate_ok,
                object=" ".join(run.command),
                file=rel,
                line=1,
                engine="gradle-test",
                provenance="executed",
                excerpt=_snippet(run.output) or "BUILD SUCCESSFUL",
            )
        ]
    parsed: list[Claim] = []
    for match in JAVA_LOC.finditer(run.output):
        raw_path = Path(match.group("path"))
        line_no = max(1, int(match.group("line")))
        file_rel = (
            relative_to_plant(raw_path, settings.plant_root)
            if raw_path.is_absolute()
            else match.group("path").replace("\\", "/")
        )
        parsed.append(
            Claim(
                subject=subject,
                predicate=predicate_fail,
                object=None,
                file=file_rel,
                line=line_no,
                engine="gradle-test",
                provenance="executed",
                excerpt=_snippet(run.output),
            )
        )
        if len(parsed) >= 8:
            break
    if parsed:
        return parsed
    return [
        Claim(
            subject=subject,
            predicate=predicate_fail,
            object=" ".join(run.command),
            file=rel,
            line=1,
            engine="gradle-test",
            provenance="executed",
            excerpt=_snippet(run.output) or f"exit {run.exit_code}",
        )
    ]


def verify_gradle(settings: Settings, check: str) -> tuple[GradleRun, list[Claim]]:
    kind, filter_name = parse_check(check)
    if kind == COMPILE_CHECK:
        run = run_gradle(
            settings,
            ["compileJava", "-Dorg.gradle.console=plain"],
            TIMEOUT_COMPILE_SEC,
        )
        claims = claims_from_output(
            settings=settings,
            subject="compileJava",
            predicate_ok="COMPILE_OK",
            predicate_fail="COMPILE_FAIL",
            run=run,
        )
        return run, claims
    assert filter_name is not None
    run = run_gradle(
        settings,
        ["test", "--tests", filter_name, "-Dorg.gradle.console=plain"],
        TIMEOUT_TEST_SEC,
    )
    claims = claims_from_output(
        settings=settings,
        subject=filter_name,
        predicate_ok="TEST_OK",
        predicate_fail="TEST_FAIL",
        run=run,
    )
    return run, claims


def gradle_python() -> str:
    return sys.executable

"""Plant root and JDK from env. No defaults that point at this laptop."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT_ENV = "CODE_INTEL_ROOT"
JAVA_HOME_ENV = "JAVA_HOME"
SERENA_ENV = "CODE_INTEL_SERENA"


class SettingsError(ValueError):
    """Operator-facing configuration error."""


@dataclass(frozen=True)
class Settings:
    plant_root: Path
    java_home: Path | None
    serena_exe: Path | None


def load_settings(environ: dict[str, str] | None = None) -> Settings:
    env = os.environ if environ is None else environ
    raw_root = (env.get(ROOT_ENV) or "").strip()
    if not raw_root:
        raise SettingsError(
            f"{ROOT_ENV} is unset. Point it at the Java tree "
            "(example: ocs-api-service-develop)."
        )
    root = Path(raw_root).expanduser().resolve()
    if not root.is_dir():
        raise SettingsError(f"{ROOT_ENV} is not a directory: {root}")
    java_raw = (env.get(JAVA_HOME_ENV) or "").strip()
    java_home = Path(java_raw).expanduser().resolve() if java_raw else None
    if java_home is not None and not java_home.is_dir():
        java_home = None
    serena_raw = (env.get(SERENA_ENV) or "").strip()
    serena_exe = Path(serena_raw).expanduser() if serena_raw else None
    if serena_exe is not None and not serena_exe.is_file():
        serena_exe = None
    return Settings(plant_root=root, java_home=java_home, serena_exe=serena_exe)


def relative_to_plant(path: Path, plant_root: Path) -> str:
    try:
        return path.resolve().relative_to(plant_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()

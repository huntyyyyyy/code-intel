"""Labeled source-text scan. Not LSP. Not CodeQL. engine=grep."""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from pathlib import Path

from code_intel.claims import Claim
from code_intel.settings import relative_to_plant

SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        ".gradle",
        ".idea",
        ".serena",
        ".venv",
        "__pycache__",
        "bin",
        "build",
        "node_modules",
        "target",
    }
)
CLAIM_CAP = 40
EXCERPT_CAP = 160
SYMBOL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")


def require_symbol(symbol: str) -> str:
    text = symbol.strip()
    if not text or len(text) > 200 or not SYMBOL_RE.match(text):
        raise ValueError(
            "symbol must be a Java identifier or dotted name "
            "(letters, digits, underscore, dots)."
        )
    return text


def iter_java_files(root: Path) -> Iterator[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIR_NAMES)
        for name in sorted(filenames):
            if name.endswith(".java"):
                yield Path(dirpath) / name


def _excerpt(line: str) -> str:
    return line.strip()[:EXCERPT_CAP]


def _decl_pattern(symbol: str) -> re.Pattern[str]:
    ident = re.escape(symbol.split(".")[-1])
    return re.compile(
        rf"^\s*(?:(?:public|protected|private|abstract|final|sealed|static)\s+)*"
        rf"(?:class|interface|enum|record)\s+{ident}\b"
    )


def _ident_pattern(symbol: str) -> re.Pattern[str]:
    ident = re.escape(symbol.split(".")[-1])
    return re.compile(rf"\b{ident}\b")


def _claim(
    *,
    subject: str,
    predicate: str,
    path: Path,
    plant: Path,
    line_no: int,
    excerpt: str,
    object_: str | None = None,
) -> Claim:
    return Claim(
        subject=subject,
        predicate=predicate,
        object=object_,
        file=relative_to_plant(path, plant),
        line=line_no,
        engine="grep",
        provenance="observed",
        excerpt=_excerpt(excerpt),
    )


def lookup_definitions(plant: Path, symbol: str) -> list[Claim]:
    name = require_symbol(symbol)
    decl = _decl_pattern(name)
    ident = _ident_pattern(name)
    defined: list[Claim] = []
    mentions: list[Claim] = []
    for path in iter_java_files(plant):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for index, line in enumerate(lines, start=1):
            if decl.search(line):
                defined.append(
                    _claim(
                        subject=name,
                        predicate="DEFINES",
                        path=path,
                        plant=plant,
                        line_no=index,
                        excerpt=line,
                    )
                )
            elif ident.search(line) and len(mentions) < CLAIM_CAP:
                mentions.append(
                    _claim(
                        subject=name,
                        predicate="MENTIONS",
                        path=path,
                        plant=plant,
                        line_no=index,
                        excerpt=line,
                    )
                )
    if defined:
        return defined[:CLAIM_CAP]
    return mentions[:CLAIM_CAP]


def impact_mentions(plant: Path, symbol: str) -> list[Claim]:
    name = require_symbol(symbol)
    ident = _ident_pattern(name)
    decl = _decl_pattern(name)
    definition_files: set[Path] = set()
    hits: list[Claim] = []
    for path in iter_java_files(plant):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        if any(decl.search(line) for line in lines):
            definition_files.add(path.resolve())
        for index, line in enumerate(lines, start=1):
            if not ident.search(line):
                continue
            is_test = path.name.endswith("Test.java") or path.name.endswith("Tests.java")
            predicate = "TESTED_IN" if is_test else "MENTIONS"
            hits.append(
                _claim(
                    subject=name,
                    predicate=predicate,
                    path=path,
                    plant=plant,
                    line_no=index,
                    excerpt=line,
                    object_=path.name if is_test else None,
                )
            )
            if len(hits) >= CLAIM_CAP:
                break
        if len(hits) >= CLAIM_CAP:
            break
    out = [
        hit
        for hit in hits
        if Path(plant, hit.file).resolve() not in definition_files
        or hit.predicate == "TESTED_IN"
    ]
    if not out:
        return [hit for hit in hits if hit.predicate != "DEFINES"][:CLAIM_CAP]
    return out[:CLAIM_CAP]

"""Closed task kinds. Server-side context compilation, not a 15-tool catalog."""

from __future__ import annotations

from code_intel.claims import EvidenceBundle
from code_intel.engines.codeql_scan import is_codeql_check, verify_codeql
from code_intel.engines.gradle_test import VerifyError, verify_gradle
from code_intel.engines.grep_scan import impact_mentions, lookup_definitions, require_symbol
from code_intel.settings import Settings, SettingsError, load_settings


def _grep_notes(settings: Settings, tool: str) -> list[str]:
    notes = [
        f"{tool} used engine=grep (source text). Not jdtls/LSP.",
        f"plant={settings.plant_root}",
    ]
    if settings.serena_exe is None:
        notes.append(
            "CODE_INTEL_SERENA unset; keep Serena as a sibling MCP for LSP."
        )
    else:
        notes.append(
            "Serena path is set but V1 does not compose it; lookup/impact stay grep."
        )
    return notes


def lookup(symbol: str, settings: Settings | None = None) -> EvidenceBundle:
    cfg = settings or load_settings()
    name = require_symbol(symbol)
    claims = lookup_definitions(cfg.plant_root, name)
    notes = _grep_notes(cfg, "lookup")
    if not claims:
        notes.append("no Java hits; try a type name (HomeController), not a sentence.")
    return EvidenceBundle(tool="lookup", query=name, claims=claims, notes=notes)


def impact(symbol: str, settings: Settings | None = None) -> EvidenceBundle:
    cfg = settings or load_settings()
    name = require_symbol(symbol)
    claims = impact_mentions(cfg.plant_root, name)
    notes = _grep_notes(cfg, "impact")
    notes.append("grep cannot prove call edges; treat MENTIONS as candidates.")
    if not claims:
        notes.append("no mentions outside a definition, or symbol absent.")
    return EvidenceBundle(tool="impact", query=name, claims=claims, notes=notes)


def verify(check: str, settings: Settings | None = None) -> EvidenceBundle:
    cfg = settings or load_settings()
    text = check.strip()
    if is_codeql_check(text):
        exit_code, claims, notes = verify_codeql(cfg.plant_root, text)
        return EvidenceBundle(
            tool="verify",
            query=text,
            claims=claims,
            notes=notes,
            exit_code=exit_code,
        )
    try:
        run, claims = verify_gradle(cfg, text)
    except VerifyError as exc:
        raise SettingsError(str(exc)) from exc
    notes = [
        f"exit={run.exit_code}",
        "command=" + " ".join(run.command),
        "engine=gradle-test (executed). JDK from JAVA_HOME if set.",
    ]
    if cfg.java_home is None:
        notes.append("JAVA_HOME unset or not a directory; wrapper uses ambient java.")
    return EvidenceBundle(
        tool="verify",
        query=text,
        claims=claims,
        notes=notes,
        exit_code=run.exit_code,
    )

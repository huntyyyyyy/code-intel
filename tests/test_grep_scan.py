from pathlib import Path

import pytest

from code_intel.engines.grep_scan import impact_mentions, lookup_definitions, require_symbol
from code_intel.settings import SettingsError, load_settings


def test_require_symbol_rejects_sentences() -> None:
    with pytest.raises(ValueError, match="identifier"):
        require_symbol("what does auth do?")


def test_lookup_defines_home_controller(plant: Path) -> None:
    claims = lookup_definitions(plant, "HomeController")
    assert claims
    assert claims[0].predicate == "DEFINES"
    assert claims[0].engine == "grep"
    assert claims[0].provenance == "observed"
    assert claims[0].file.endswith("HomeController.java")
    assert "class HomeController" in claims[0].excerpt


def test_lookup_unknown_symbol_empty(plant: Path) -> None:
    assert lookup_definitions(plant, "NotInThisTree") == []


def test_impact_finds_caller_and_test(plant: Path) -> None:
    claims = impact_mentions(plant, "HomeController")
    predicates = {claim.predicate for claim in claims}
    files = {claim.file for claim in claims}
    assert "MENTIONS" in predicates
    assert "TESTED_IN" in predicates
    assert any(path.endswith("TopicController.java") for path in files)
    assert any(path.endswith("HomeControllerTest.java") for path in files)
    assert all(claim.engine == "grep" for claim in claims)


def test_load_settings_requires_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CODE_INTEL_ROOT", raising=False)
    with pytest.raises(SettingsError, match="CODE_INTEL_ROOT"):
        load_settings({})
    monkeypatch.setenv("CODE_INTEL_ROOT", str(tmp_path))
    loaded = load_settings()
    assert loaded.plant_root == tmp_path.resolve()

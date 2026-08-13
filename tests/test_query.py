import pytest

from code_intel.engines.gradle_test import VerifyError, parse_check, verify_gradle
from code_intel.query import lookup, verify
from code_intel.settings import Settings


def test_parse_check_rejects_shell() -> None:
    with pytest.raises(VerifyError):
        parse_check("compile; rm -rf /")
    with pytest.raises(VerifyError):
        parse_check("test:../../etc")
    kind, filt = parse_check("test:com.example.HomeControllerTest")
    assert kind == "test"
    assert filt == "com.example.HomeControllerTest"


def test_verify_compile_ok(settings: Settings) -> None:
    run, claims = verify_gradle(settings, "compile")
    assert run.exit_code == 0
    assert claims[0].predicate == "COMPILE_OK"
    assert claims[0].engine == "gradle-test"
    assert claims[0].provenance == "executed"
    assert "BUILD SUCCESSFUL" in claims[0].excerpt


def test_verify_test_fail_parses_java_line(settings: Settings) -> None:
    run, claims = verify_gradle(settings, "test:failjava")
    assert run.exit_code == 1
    assert claims[0].predicate == "TEST_FAIL"
    assert claims[0].file.endswith("Broken.java")
    assert claims[0].line == 4


def test_query_lookup_sets_notes(settings: Settings) -> None:
    bundle = lookup("HomeController", settings=settings)
    assert bundle.tool == "lookup"
    assert bundle.claims[0].predicate == "DEFINES"
    assert any("engine=grep" in note for note in bundle.notes)


def test_query_verify_codeql_stub(settings: Settings) -> None:
    bundle = verify("codeql:java/sql-injection", settings=settings)
    assert bundle.exit_code == 2
    assert bundle.claims[0].engine == "codeql"
    assert bundle.claims[0].provenance == "unproven"
    assert bundle.claims[0].predicate == "ENGINE_ABSENT"


def test_query_verify_compile_exit(settings: Settings) -> None:
    bundle = verify("compile", settings=settings)
    assert bundle.exit_code == 0
    assert bundle.claims[0].engine == "gradle-test"

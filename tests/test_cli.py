import json

from code_intel.cli import main


def test_cli_lookup_json(plant, monkeypatch, capsys) -> None:
    monkeypatch.setenv("CODE_INTEL_ROOT", str(plant))
    assert main(["lookup", "HomeController"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["tool"] == "lookup"
    assert payload["claims"][0]["predicate"] == "DEFINES"


def test_cli_verify_compile(plant, monkeypatch, capsys) -> None:
    monkeypatch.setenv("CODE_INTEL_ROOT", str(plant))
    assert main(["verify", "compile"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["exit_code"] == 0
    assert payload["claims"][0]["engine"] == "gradle-test"

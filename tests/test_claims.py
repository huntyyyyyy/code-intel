import pytest
from pydantic import ValidationError

from code_intel.claims import Claim


def test_claim_forbids_extra_keys() -> None:
    with pytest.raises(ValidationError):
        Claim(
            subject="HomeController",
            predicate="DEFINES",
            file="HomeController.java",
            line=7,
            engine="grep",
            provenance="observed",
            excerpt="class HomeController",
            scanner="nope",
        )


def test_claim_rejects_unknown_predicate() -> None:
    with pytest.raises(ValueError, match="unknown predicate"):
        Claim(
            subject="HomeController",
            predicate="FEELS_TRUE",
            file="HomeController.java",
            line=7,
            engine="grep",
            provenance="observed",
            excerpt="class HomeController",
        )


def test_claim_line_at_least_one() -> None:
    with pytest.raises(ValidationError):
        Claim(
            subject="HomeController",
            predicate="DEFINES",
            file="HomeController.java",
            line=0,
            engine="grep",
            provenance="observed",
            excerpt="class HomeController",
        )


def test_claim_roundtrip() -> None:
    claim = Claim(
        subject="HomeController",
        predicate="DEFINES",
        object=None,
        file="src/main/java/com/example/HomeController.java",
        line=7,
        engine="grep",
        provenance="observed",
        excerpt="@Controller public class HomeController",
    )
    dumped = claim.model_dump()
    assert dumped["engine"] == "grep"
    assert Claim.model_validate(dumped) == claim

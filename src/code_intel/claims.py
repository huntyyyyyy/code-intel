"""Closed claim object. extra=forbid. Engines stay labeled, never mixed."""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Engine = Literal["lsp", "codeql", "gradle-test", "grep"]
Provenance = Literal["observed", "static", "executed", "unproven"]
ToolName = Literal["lookup", "impact", "verify"]

PREDICATES = frozenset(
    {
        "DEFINES",
        "MENTIONS",
        "TESTED_IN",
        "COMPILE_OK",
        "COMPILE_FAIL",
        "TEST_OK",
        "TEST_FAIL",
        "ENGINE_ABSENT",
    }
)


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str
    predicate: str
    object: Optional[str] = None
    file: str
    line: int = Field(ge=1)
    engine: Engine
    provenance: Provenance
    excerpt: str

    def model_post_init(self, _context: object) -> None:
        if self.predicate not in PREDICATES:
            raise ValueError(f"unknown predicate: {self.predicate}")


class EvidenceBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: ToolName
    query: str
    claims: list[Claim]
    notes: list[str] = Field(default_factory=list)
    exit_code: Optional[int] = None

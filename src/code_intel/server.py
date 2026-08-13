"""stdio MCP: lookup, impact, verify. Run: python -m code_intel.server"""

from __future__ import annotations

from fastmcp import FastMCP

from code_intel.query import impact as run_impact
from code_intel.query import lookup as run_lookup
from code_intel.query import verify as run_verify
from code_intel.settings import SettingsError

mcp = FastMCP("code-intel")


def _dump(bundle) -> dict:
    return bundle.model_dump()


@mcp.tool
def lookup(symbol: str) -> dict:
    """Symbol to definition (and mentions if no class/interface/enum/record hit).

    engine=grep in V1. Cite file:line. Not a Spring-resolved fact.
    """
    try:
        return _dump(run_lookup(symbol))
    except (SettingsError, ValueError) as exc:
        return {"error": str(exc), "tool": "lookup", "query": symbol, "claims": []}


@mcp.tool
def impact(symbol: str) -> dict:
    """Mentions and *Test.java hits for a symbol. Not a call graph.

    engine=grep. MENTIONS are candidates, not proven callers.
    """
    try:
        return _dump(run_impact(symbol))
    except (SettingsError, ValueError) as exc:
        return {"error": str(exc), "tool": "impact", "query": symbol, "claims": []}


@mcp.tool
def verify(check: str) -> dict:
    """Named check: 'compile', 'test:<Gradle filter>', or 'codeql:<rule-id>'.

    compile/test execute the Gradle wrapper. codeql is a stub in V1.
    """
    try:
        return _dump(run_verify(check))
    except (SettingsError, ValueError) as exc:
        return {
            "error": str(exc),
            "tool": "verify",
            "query": check,
            "claims": [],
            "exit_code": 2,
        }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

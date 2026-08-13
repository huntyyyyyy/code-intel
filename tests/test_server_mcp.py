"""In-process MCP smoke: the three tools exist and lookup returns claims."""

from __future__ import annotations

from pathlib import Path

import pytest

from code_intel.server import mcp


@pytest.mark.asyncio
async def test_mcp_tools_and_lookup(plant: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("fastmcp")
    from fastmcp import Client

    monkeypatch.setenv("CODE_INTEL_ROOT", str(plant))
    async with Client(mcp) as client:
        tools = await client.list_tools()
        names = sorted(tool.name for tool in tools)
        assert names == ["impact", "lookup", "verify"]
        result = await client.call_tool("lookup", {"symbol": "HomeController"})
        payload = result.data
        if payload is None:
            payload = result.structured_content
        assert payload is not None
        claims = payload["claims"]
        assert claims[0]["predicate"] == "DEFINES"
        assert claims[0]["engine"] == "grep"
        assert claims[0]["file"].endswith("HomeController.java")

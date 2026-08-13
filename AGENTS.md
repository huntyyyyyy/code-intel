# AGENTS.md

code-intel is a **repository-intelligence MCP**, not a documentation generator.

- Tools: `lookup`, `impact`, `verify` only.
- V1 lookup/impact = labeled **grep**. Serena/jdtls stays a sibling MCP.
- `verify compile` / `verify test:<filter>` execute the Gradle wrapper.
- Claims: closed Pydantic model, `extra=forbid`, engine labeled.
- Plant: `CODE_INTEL_ROOT`. JDK 17 via `JAVA_HOME` (OCS is 17, not 25).
- Eval bank: `eval/tasks.json` — freeze before scored runs.
- Out of scope until eval wins: graph DB, embeddings, GitNexus, 15 tools.

```powershell
uv sync --extra dev
uv run pytest
uv run python -m code_intel lookup HomeController
```

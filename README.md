# code-intel

Evidence MCP for coding agents. Three tools, labeled engines, citations.

This is **not** a documentation generator. Documents are views. The product is:
smallest evidence to understand and change a Spring tree, with `file:line`.

| Tool | V1 engine | Returns |
| --- | --- | --- |
| `lookup` | grep (source text) | `DEFINES` for `class/interface/enum/record`, else `MENTIONS` |
| `impact` | grep | `MENTIONS` + `TESTED_IN` (`*Test.java`) |
| `verify` | gradle-test (executed) | `compile` or `test:<filter>`; `codeql:<id>` is a stub |

Each row is a **claim**: `subject`, `predicate`, `object?`, `file`, `line`,
`engine` (`lsp` \| `codeql` \| `gradle-test` \| `grep`), `provenance`
(`observed` \| `static` \| `executed` \| `unproven`), `excerpt`. Extra keys are
forbidden. Grep is never labeled as LSP.

V1 does **not** compose Serena/jdtls. Keep Serena as a **sibling** MCP for real
LSP. Do not add a graph DB, embeddings, or a 15-tool catalog until frozen eval
tasks beat Grep/Read on this plant.

## Setup (Windows)

Plant (OCS unzip):

`C:\Users\16145\Downloads\ocs-api-service-develop\ocs-api-service-develop`

JDK 17 (do not use JAVA_HOME=25):

`C:\Users\16145\scoop\apps\temurin17-jdk\current`

From this directory:

```powershell
cd C:\Users\16145\projects\code-intel
uv sync --extra dev
$env:CODE_INTEL_ROOT = "C:\Users\16145\Downloads\ocs-api-service-develop\ocs-api-service-develop"
$env:JAVA_HOME = "C:\Users\16145\scoop\apps\temurin17-jdk\current"
uv run pytest
uv run python -m code_intel lookup HomeController
uv run python -m code_intel impact TaxonomyMappingService
uv run python -m code_intel verify compile
```

If `uv` is missing: `irm https://astral.sh/uv/install.ps1 | iex` (or pip:
`py -3.12 -m venv .venv; .\.venv\Scripts\pip install -e ".[dev]"`).

## Claude Desktop

Edit **only** `mcpServers` in `%APPDATA%\Claude\claude_desktop_config.json`.
Keep `coworkUserFilesPath` / `preferences`. Do not replace the whole file.

```json
"code-intel": {
  "command": "C:\\Users\\16145\\projects\\code-intel\\.venv\\Scripts\\python.exe",
  "args": ["-m", "code_intel.server"],
  "env": {
    "CODE_INTEL_ROOT": "C:\\Users\\16145\\Downloads\\ocs-api-service-develop\\ocs-api-service-develop",
    "JAVA_HOME": "C:\\Users\\16145\\scoop\\apps\\temurin17-jdk\\current"
  }
}
```

stdio MCP is `python -m code_intel.server`. The CLI is `python -m code_intel`
(lookup/impact/verify). Do not mix them: Claude must not launch the CLI.

Serena stays a second server (sibling). After `uv sync`, the venv python path
above is the `command`.

## Eval

`eval/tasks.json` is frozen **before** scored Claude runs. Add new ids; do not
edit queries after the first scored pass. Arms: Claude+repo vs Claude+this MCP.
Metrics: false-claim rate and tokens, not “feels smarter.”

## Out of scope until eval wins

Graph DB, embeddings, GitNexus clone, custom CPG, composing Serena in-process,
CodeQL database create, writing files, fifteen MCP tools.

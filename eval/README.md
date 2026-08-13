# Eval protocol

`tasks.json` is the frozen bank. Queries come from types that exist on the
2026-08-13 OCS plant (grep log), not from Spring patterns that plant does not
have (interface `@Transactional`, `SecurityFilterChain`, custom `@interface`).

## Rules

1. Freeze this file before any scored Claude Desktop run.
2. After freeze, do not edit `query` strings. Add `t22+` if you need more.
3. Score **false-claim rate** (claim `file:line` does not contain the excerpt /
   symbol) and **tokens** vs Claude with only Read/Grep.
4. `verify compile` is executed (Gradle). Do not score it as grep.
5. V1 `lookup`/`impact` are grep. A later LSP compose is a new arm, not a silent
   relabel of these rows.

## Success

code-intel wins if, on this bank, the MCP arm has lower false-claim rate at
equal or lower tokens than repo-only, or equal claims at materially fewer
tokens. “Feels easier” is not a metric.

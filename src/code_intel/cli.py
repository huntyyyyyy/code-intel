"""Terminal driver. Does not read stdin as MCP (that is code_intel.server)."""

from __future__ import annotations

import argparse
import json
import sys

from code_intel.query import impact, lookup, verify
from code_intel.settings import SettingsError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code-intel",
        description="lookup / impact / verify against CODE_INTEL_ROOT.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    look = sub.add_parser("lookup", help="Find a type definition (grep in V1).")
    look.add_argument("symbol")
    imp = sub.add_parser("impact", help="Find mentions and tests (grep in V1).")
    imp.add_argument("symbol")
    ver = sub.add_parser("verify", help="compile | test:<filter> | codeql:<id>")
    ver.add_argument("check")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "lookup":
            bundle = lookup(args.symbol)
        elif args.command == "impact":
            bundle = impact(args.symbol)
        else:
            bundle = verify(args.check)
    except (SettingsError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(bundle.model_dump(), indent=2))
    if bundle.tool == "verify" and bundle.exit_code not in (None, 0):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

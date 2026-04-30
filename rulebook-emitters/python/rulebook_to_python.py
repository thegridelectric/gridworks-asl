#!/usr/bin/env python3
"""Emit Python source from the rulebook.

Scaffold: loads the rulebook, prints a summary, writes a placeholder TODO.txt.
The real codegen lands in follow-up commits.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EMITTERS_ROOT = HERE.parent
PROJECT_ROOT = EMITTERS_ROOT.parent
sys.path.insert(0, str(EMITTERS_ROOT))

from shared.loader import load_rulebook, table_summary  # noqa: E402

DEFAULT_INPUT = PROJECT_ROOT / "effortless-rulebook" / "effortless-rulebook.json"
DEFAULT_OUTPUT = HERE / "out"


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit Python source from the rulebook.")
    parser.add_argument("--input", "-i", type=Path, default=DEFAULT_INPUT,
                        help=f"path to effortless-rulebook.json (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT,
                        help=f"output directory (default: {DEFAULT_OUTPUT})")
    args = parser.parse_args()

    rulebook = load_rulebook(args.input)
    args.output.mkdir(parents=True, exist_ok=True)

    print(f"rulebook-to-python: read {args.input}")
    for name, count in table_summary(rulebook):
        print(f"  {name}: {count} rows")

    placeholder = args.output / "TODO.txt"
    placeholder.write_text(
        "rulebook-to-python: scaffold only. Real emission not yet implemented.\n"
        f"Rulebook: {args.input}\n"
    )
    print(f"rulebook-to-python: wrote placeholder {placeholder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

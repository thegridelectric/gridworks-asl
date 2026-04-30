#!/usr/bin/env python3
"""Emit single-page HTML documentation from the rulebook.

Scaffold: loads the rulebook, prints a summary, writes a placeholder sema.html.
The real templating lands in follow-up commits.
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EMITTERS_ROOT = HERE.parent
PROJECT_ROOT = EMITTERS_ROOT.parent
sys.path.insert(0, str(EMITTERS_ROOT))

from shared.loader import load_rulebook, table_summary  # noqa: E402

DEFAULT_INPUT = PROJECT_ROOT / "effortless-rulebook" / "effortless-rulebook.json"
DEFAULT_OUTPUT = HERE / "out"


PLACEHOLDER_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Sema — placeholder</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 720px; margin: 4em auto; padding: 0 1em; color: #222; }}
    code {{ background: #f4f4f4; padding: 0 0.3em; border-radius: 3px; }}
    table {{ border-collapse: collapse; margin-top: 1em; }}
    td, th {{ border: 1px solid #ccc; padding: 0.3em 0.6em; text-align: left; }}
    th {{ background: #f4f4f4; }}
  </style>
</head>
<body>
  <h1>Sema — rulebook-to-html scaffold</h1>
  <p>Real emission not yet implemented. This file is a placeholder so the wiring is testable end-to-end.</p>
  <p>Source rulebook: <code>{input_path}</code></p>
  <h2>Tables found</h2>
  <table>
    <thead><tr><th>Table</th><th>Rows</th></tr></thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit single-page HTML docs from the rulebook.")
    parser.add_argument("--input", "-i", type=Path, default=DEFAULT_INPUT,
                        help=f"path to effortless-rulebook.json (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT,
                        help=f"output directory (default: {DEFAULT_OUTPUT})")
    args = parser.parse_args()

    rulebook = load_rulebook(args.input)
    args.output.mkdir(parents=True, exist_ok=True)

    summary = table_summary(rulebook)
    print(f"rulebook-to-html: read {args.input}")
    for name, count in summary:
        print(f"  {name}: {count} rows")

    rows_html = "\n      ".join(
        f"<tr><td>{html.escape(name)}</td><td>{count}</td></tr>"
        for name, count in summary
    )
    out_path = args.output / "sema.html"
    out_path.write_text(PLACEHOLDER_HTML.format(
        input_path=html.escape(str(args.input)),
        rows=rows_html,
    ))
    print(f"rulebook-to-html: wrote placeholder {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

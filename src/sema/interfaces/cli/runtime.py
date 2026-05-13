from __future__ import annotations

import argparse

from sema.tools.runtime_generation.scaffold_axiom_template import scaffold_axiom_template
from sema.tools.runtime_generation.scaffold_upgrade_template import (
    scaffold_upgrade_template,
)


def _run_scaffold_axiom_template(args: argparse.Namespace) -> None:
    path = scaffold_axiom_template(args.type_name, args.version)
    print(f"Created axiom template: {path}")


def _run_scaffold_upgrade_template(args: argparse.Namespace) -> None:
    path = scaffold_upgrade_template(args.type_name, args.version, args.next_version)
    print(f"Created upgrade template: {path}")


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "runtime",
        help="Runtime generation helper commands.",
        description="Helpers for maintaining generated Sema runtime templates.",
    )
    runtime_subparsers = parser.add_subparsers(dest="runtime_command", required=True)

    scaffold_axiom_parser = runtime_subparsers.add_parser(
        "scaffold-axiom-template",
        help="Create a missing axiom implementation template for a type version.",
        description=(
            "Read definitions/types/<type-name>/<version>.yaml and create a "
            "missing Jinja axiom template. Existing templates are never overwritten."
        ),
    )
    scaffold_axiom_parser.add_argument("type_name")
    scaffold_axiom_parser.add_argument("version")
    scaffold_axiom_parser.set_defaults(handler=_run_scaffold_axiom_template)

    scaffold_upgrade_parser = runtime_subparsers.add_parser(
        "scaffold-upgrade-template",
        help="Create a missing upgrade template for a non-latest type version.",
        description=(
            "Create a missing Jinja upgrade template for "
            "<type-name>:<version> -> <next-version>. The stub raises "
            "NotImplementedError until hand-written. Existing templates are never "
            "overwritten."
        ),
    )
    scaffold_upgrade_parser.add_argument("type_name")
    scaffold_upgrade_parser.add_argument("version")
    scaffold_upgrade_parser.add_argument("next_version")
    scaffold_upgrade_parser.set_defaults(handler=_run_scaffold_upgrade_template)

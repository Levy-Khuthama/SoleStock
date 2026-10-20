"""Command-line entry point: load the inventory, then start the menu."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from .menu import InventoryApp, report_problems
from .stock import Stock
from .storage import (
    InventoryFileError,
    InventoryFileNotFound,
    LoadResult,
    PathLike,
    load_shoes,
)

# inventory.txt sits next to solestock.py, so the program finds it no
# matter which folder it is run from.
DEFAULT_FILE = Path(__file__).resolve().parent.parent / "inventory.txt"


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the command line."""
    parser = argparse.ArgumentParser(
        description="Manage a shoe inventory stored in a CSV file."
    )
    parser.add_argument(
        "--file",
        default=str(DEFAULT_FILE),
        help="path to the inventory file (default: inventory.txt next to "
             "solestock.py)",
    )
    return parser


def load_for_startup(path: PathLike) -> Optional[LoadResult]:
    """Load the file when the program starts.

    A missing file is fine (it is created on the first save) and gives an
    empty result. A file that exists but cannot be read stops the program
    by returning None: carrying on with an empty stock could overwrite
    data that is only unreadable for now.
    """
    try:
        return load_shoes(path)
    except InventoryFileNotFound:
        print(f"No inventory file at {path} yet. "
              "It will be created when you capture a shoe.")
        return LoadResult()
    except InventoryFileError as error:
        print(error)
        return None


def main(argv: Optional[List[str]] = None) -> int:
    """Load the inventory and run the menu. Return the exit code."""
    args = build_parser().parse_args(argv)

    result = load_for_startup(args.file)
    if result is None:
        return 1

    stock = Stock(result.shoes)
    if result.shoes:
        print(f"Loaded {len(stock)} shoes from {Path(args.file).name}.")
    report_problems(result.problems)

    InventoryApp(stock, args.file).run()
    return 0

"""Reading and writing the inventory file.

The file is a CSV with a header row:

    Country,Code,Product,Cost,Quantity

Loading never stops at a bad row: it keeps the good rows and reports each
bad one with its line number. Saving writes to a temporary file first and
swaps it in only when the write has finished, so a failure part-way through
can never leave a half-written inventory.
"""

from __future__ import annotations

import csv
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, List, Sequence, Union

from .models import Shoe

HEADER = ["Country", "Code", "Product", "Cost", "Quantity"]
READ_ENCODING = "utf-8-sig"  # also accepts a file saved with a BOM by Excel
WRITE_ENCODING = "utf-8"

PathLike = Union[str, "os.PathLike[str]"]


class InventoryFileError(Exception):
    """The inventory file could not be read or written."""


class InventoryFileNotFound(InventoryFileError):
    """The inventory file does not exist."""


@dataclass
class LoadResult:
    """What came out of reading the file."""

    shoes: List[Shoe] = field(default_factory=list)
    problems: List[str] = field(default_factory=list)


def parse_row(row: Sequence[str]) -> Shoe:
    """Turn one CSV row into a ``Shoe``. Raise ``ValueError`` if it is bad."""
    if len(row) != len(HEADER):
        raise ValueError(
            f"expected {len(HEADER)} fields but found {len(row)}"
        )

    country, code, product, raw_cost, raw_quantity = (
        cell.strip() for cell in row
    )
    for name, value in (
        ("country", country), ("code", code), ("product", product),
    ):
        if not value:
            raise ValueError(f"the {name} is blank")

    try:
        cost = Decimal(raw_cost)
    except InvalidOperation:
        raise ValueError(f"cost '{raw_cost}' is not a number") from None
    if not cost.is_finite() or cost < 0:
        raise ValueError(f"cost '{raw_cost}' must be zero or more")

    try:
        quantity = int(raw_quantity)
    except ValueError:
        raise ValueError(
            f"quantity '{raw_quantity}' is not a whole number"
        ) from None
    if quantity < 0:
        raise ValueError(f"quantity '{raw_quantity}' cannot be negative")

    return Shoe(country, code, product, cost, quantity)


def load_shoes(path: PathLike) -> LoadResult:
    """Read every valid shoe from ``path``.

    Blank lines are ignored. A row that is malformed, or that repeats a
    code already seen, is skipped and described in ``problems``.
    Raises ``InventoryFileNotFound`` if the file is missing and
    ``InventoryFileError`` if it cannot be read.
    """
    path = Path(path)
    result = LoadResult()
    seen_codes = set()
    checked_first_row = False

    try:
        with path.open(newline="", encoding=READ_ENCODING) as handle:
            reader = csv.reader(handle)
            for row in reader:
                if not any(cell.strip() for cell in row):
                    continue  # blank line

                if not checked_first_row:
                    checked_first_row = True
                    if _is_header(row):
                        continue  # a file without a header is still fine

                try:
                    shoe = parse_row(row)
                except ValueError as error:
                    result.problems.append(
                        f"line {reader.line_num}: {error}"
                    )
                    continue

                key = shoe.code.upper()
                if key in seen_codes:
                    result.problems.append(
                        f"line {reader.line_num}: code {shoe.code} "
                        "is already used by an earlier row"
                    )
                    continue
                seen_codes.add(key)
                result.shoes.append(shoe)
    except FileNotFoundError:
        raise InventoryFileNotFound(f"File not found: {path}") from None
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        raise InventoryFileError(f"Could not read {path}: {error}") from error

    return result


def _is_header(row: Sequence[str]) -> bool:
    """Return True if the row is the file's header row."""
    return [cell.strip().lower() for cell in row] == [
        name.lower() for name in HEADER
    ]


def backup_file(path: PathLike) -> Path:
    """Copy ``path`` to ``<path>.bak`` and return the backup's path."""
    path = Path(path)
    backup = path.with_name(path.name + ".bak")
    try:
        shutil.copy2(path, backup)
    except OSError as error:
        raise InventoryFileError(
            f"Could not back up {path}: {error}"
        ) from error
    return backup


def save_shoes(path: PathLike, shoes: Iterable[Shoe]) -> None:
    """Write ``shoes`` to ``path``, replacing the file only on success.

    Raises ``InventoryFileError`` if the file cannot be written; the
    existing file is then left exactly as it was.
    """
    path = Path(path)
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            "w", dir=path.parent, suffix=".tmp", delete=False,
            newline="", encoding=WRITE_ENCODING,
        ) as handle:
            temp_path = Path(handle.name)
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(HEADER)
            for shoe in shoes:
                writer.writerow([
                    shoe.country, shoe.code, shoe.product,
                    shoe.cost, shoe.quantity,
                ])

        if path.exists():
            shutil.copymode(path, temp_path)  # keep the file's permissions
        os.replace(temp_path, path)
    except OSError as error:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        raise InventoryFileError(f"Could not save {path}: {error}") from error

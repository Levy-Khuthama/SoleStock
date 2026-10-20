"""Turn shoes into text for the console.

These functions only build strings and never print, which keeps the layout
easy to test. The table is plain text, so the program needs no
third-party packages.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from .models import Shoe

COLUMN_GAP = "  "
HEADERS = ("Country", "Code", "Product", "Cost", "Quantity")
RIGHT_ALIGNED = {3, 4}  # the Cost and Quantity columns
EMPTY_MESSAGE = "There are no shoes in the inventory."


def format_money(amount: Decimal) -> str:
    """Format an amount with thousands separators and two decimals."""
    return f"{amount:,.2f}"


def format_shoe(shoe: Shoe) -> str:
    """Describe one shoe on a single line."""
    return (
        f"{shoe.product} ({shoe.code}, {shoe.country}): "
        f"{shoe.quantity} in stock at {format_money(shoe.cost)} each"
    )


def format_table(shoes: Sequence[Shoe]) -> str:
    """Return the shoes as an aligned table with a header row."""
    if not shoes:
        return EMPTY_MESSAGE

    rows = [
        (
            shoe.country,
            shoe.code,
            shoe.product,
            format_money(shoe.cost),
            str(shoe.quantity),
        )
        for shoe in shoes
    ]
    widths = [
        max(len(HEADERS[i]), *(len(row[i]) for row in rows))
        for i in range(len(HEADERS))
    ]

    def format_row(cells: Sequence[str]) -> str:
        parts = [
            cell.rjust(width) if i in RIGHT_ALIGNED else cell.ljust(width)
            for i, (cell, width) in enumerate(zip(cells, widths))
        ]
        return COLUMN_GAP.join(parts).rstrip()

    header_line = format_row(HEADERS)
    lines = [header_line, "-" * len(header_line)]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)


def format_values(shoes: Sequence[Shoe], total: Decimal) -> str:
    """Return each product's stock value, then the grand ``total``."""
    if not shoes:
        return EMPTY_MESSAGE

    names = [shoe.product for shoe in shoes] + ["Total"]
    amounts = [format_money(shoe.value) for shoe in shoes]
    amounts.append(format_money(total))

    name_width = max(len(name) for name in names)
    amount_width = max(len(amount) for amount in amounts)
    lines = [
        f"{name.ljust(name_width)}  {amount.rjust(amount_width)}"
        for name, amount in zip(names, amounts)
    ]
    rule = "-" * len(lines[0])
    return "\n".join(lines[:-1] + [rule, lines[-1]])

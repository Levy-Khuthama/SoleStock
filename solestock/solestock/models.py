"""The data model: one line of shoe stock."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Shoe:
    """A shoe model held in stock.

    ``cost`` is a ``Decimal`` rather than a ``float`` so money is exact and
    reads back from the file exactly as it was written ("2700.0" stays
    "2700.0"). The record is frozen: restocking creates an updated copy
    instead of changing the original.
    """

    country: str
    code: str
    product: str
    cost: Decimal
    quantity: int

    @property
    def value(self) -> Decimal:
        """Total value of the stock held: cost multiplied by quantity."""
        return self.cost * self.quantity

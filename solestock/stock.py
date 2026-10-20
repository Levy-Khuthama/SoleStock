"""The stock list and the questions you can ask of it.

This module knows nothing about files or the console, so it is simple to
test and to reuse.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import Iterable, List, Optional, Tuple

from .models import Shoe


class DuplicateCodeError(ValueError):
    """A shoe with this code is already in stock."""


class UnknownCodeError(LookupError):
    """No shoe in stock has this code."""


def _same_code(first: str, second: str) -> bool:
    """Compare two codes, ignoring case and surrounding spaces."""
    return first.strip().upper() == second.strip().upper()


class Stock:
    """An ordered collection of shoes with unique codes."""

    def __init__(self, shoes: Iterable[Shoe] = ()) -> None:
        self._shoes: List[Shoe] = []
        for shoe in shoes:
            self.add(shoe)

    def __len__(self) -> int:
        return len(self._shoes)

    @property
    def shoes(self) -> Tuple[Shoe, ...]:
        """Every shoe, in the order they were added."""
        return tuple(self._shoes)

    def add(self, shoe: Shoe) -> None:
        """Add a shoe. Raise ``DuplicateCodeError`` if its code is taken."""
        if self.find(shoe.code) is not None:
            raise DuplicateCodeError(
                f"A shoe with code {shoe.code} already exists."
            )
        self._shoes.append(shoe)

    def find(self, code: str) -> Optional[Shoe]:
        """Return the shoe with this code (any case), or None."""
        for shoe in self._shoes:
            if _same_code(shoe.code, code):
                return shoe
        return None

    def lowest_stock(self) -> Optional[Shoe]:
        """Return the shoe with the fewest in stock (first one on a tie)."""
        return min(self._shoes, key=lambda s: s.quantity, default=None)

    def highest_stock(self) -> Optional[Shoe]:
        """Return the shoe with the most in stock (first one on a tie)."""
        return max(self._shoes, key=lambda s: s.quantity, default=None)

    def restock(self, code: str, amount: int) -> Shoe:
        """Add ``amount`` pairs to a shoe and return the updated shoe.

        Raises ``ValueError`` if ``amount`` is not above zero and
        ``UnknownCodeError`` if no shoe has this code.
        """
        if amount <= 0:
            raise ValueError("The restock amount must be above zero.")

        for index, shoe in enumerate(self._shoes):
            if _same_code(shoe.code, code):
                updated = replace(shoe, quantity=shoe.quantity + amount)
                self._shoes[index] = updated
                return updated
        raise UnknownCodeError(f"No shoe has code {code}.")

    def total_value(self) -> Decimal:
        """Return the combined value of everything in stock."""
        return sum((shoe.value for shoe in self._shoes), Decimal(0))

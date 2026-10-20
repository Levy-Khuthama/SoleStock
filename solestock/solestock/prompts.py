"""Validated console input.

Every ``ask_*`` function keeps asking until it gets a usable answer, so the
rest of the program can trust what it receives.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

_YES = {"y", "yes"}
_NO = {"n", "no"}


def ask_text(prompt: str) -> str:
    """Ask until the user enters something other than blank text."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be blank.")


def ask_cost(prompt: str) -> Decimal:
    """Ask until the user enters a cost of zero or more, e.g. 1299.50."""
    while True:
        text = input(prompt).strip()
        try:
            cost = Decimal(text)
        except InvalidOperation:
            print("Invalid input. Please enter a number such as 1299.50.")
            continue

        if cost.is_finite() and cost >= 0:
            return cost
        print("The cost must be zero or more.")


def ask_quantity(prompt: str) -> int:
    """Ask until the user enters a whole number of zero or more."""
    while True:
        quantity = _ask_whole_number(prompt)
        if quantity >= 0:
            return quantity
        print("The quantity cannot be negative.")


def ask_positive_number(prompt: str) -> int:
    """Ask until the user enters a whole number above zero."""
    while True:
        number = _ask_whole_number(prompt)
        if number > 0:
            return number
        print("Please enter a number above zero.")


def ask_yes_no(prompt: str) -> bool:
    """Ask a yes/no question and return True for yes."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in _YES:
            return True
        if answer in _NO:
            return False
        print("Please answer 'yes' or 'no'.")


def _ask_whole_number(prompt: str) -> int:
    """Ask until the user enters a whole number (positive or negative)."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a whole number.")

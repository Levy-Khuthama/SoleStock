"""Shared test helpers."""

import pytest

HEADER_LINE = "Country,Code,Product,Cost,Quantity"

SAMPLE_INVENTORY = f"""{HEADER_LINE}
South Africa,SKU1,Alpha,100,5
China,SKU2,Beta,200.50,2
Brazil,SKU3,Gamma,50,9
"""


@pytest.fixture
def inventory_file(tmp_path):
    """A small inventory file: Beta has the lowest stock, Gamma the highest."""
    path = tmp_path / "inventory.txt"
    path.write_text(SAMPLE_INVENTORY, encoding="utf-8")
    return path


@pytest.fixture
def feed(monkeypatch):
    """Script the answers ``input()`` gives, one per call.

    Once the answers run out, ``input()`` raises EOFError, exactly as it does
    when a person presses Ctrl+D.
    """
    def _feed(*answers):
        remaining = iter(answers)

        def fake_input(prompt=""):
            try:
                return next(remaining)
            except StopIteration:
                raise EOFError from None

        monkeypatch.setattr("builtins.input", fake_input)

    return _feed

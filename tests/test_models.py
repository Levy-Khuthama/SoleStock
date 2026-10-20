import dataclasses
from decimal import Decimal

import pytest

from solestock.models import Shoe


def make_shoe(**changes):
    values = dict(country="Chile", code="SKU9", product="Test",
                  cost=Decimal("19.99"), quantity=3)
    values.update(changes)
    return Shoe(**values)


def test_value_is_cost_times_quantity():
    assert make_shoe().value == Decimal("59.97")


def test_value_is_exact_for_money():
    # With floats, 0.1 * 3 is 0.30000000000000004.
    assert make_shoe(cost=Decimal("0.10"), quantity=3).value == Decimal("0.30")


def test_value_of_zero_stock_is_zero():
    assert make_shoe(quantity=0).value == 0


def test_a_shoe_cannot_be_changed_in_place():
    shoe = make_shoe()
    with pytest.raises(dataclasses.FrozenInstanceError):
        shoe.quantity = 99

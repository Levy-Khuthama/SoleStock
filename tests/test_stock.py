from decimal import Decimal

import pytest

from solestock.models import Shoe
from solestock.stock import DuplicateCodeError, Stock, UnknownCodeError


def make_shoe(code="SKU1", quantity=5, cost="10", product="Alpha"):
    return Shoe("Chile", code, product, Decimal(cost), quantity)


@pytest.fixture
def stock():
    return Stock([
        make_shoe("SKU1", quantity=5, product="Alpha"),
        make_shoe("SKU2", quantity=2, product="Beta"),
        make_shoe("SKU3", quantity=9, product="Gamma"),
    ])


# ---- Adding and finding ----------------------------------------------------

def test_add_grows_the_stock():
    stock = Stock()
    stock.add(make_shoe("SKU1"))
    assert len(stock) == 1


def test_add_rejects_a_code_already_in_stock(stock):
    with pytest.raises(DuplicateCodeError):
        stock.add(make_shoe("SKU1"))


def test_codes_are_compared_ignoring_case_and_spaces(stock):
    with pytest.raises(DuplicateCodeError):
        stock.add(make_shoe(" sku1 "))


def test_building_a_stock_from_duplicates_fails():
    with pytest.raises(DuplicateCodeError):
        Stock([make_shoe("SKU1"), make_shoe("SKU1")])


def test_find_ignores_case_and_spaces(stock):
    assert stock.find("  sku2 ").product == "Beta"


def test_find_returns_none_for_an_unknown_code(stock):
    assert stock.find("SKU404") is None


def test_shoes_cannot_be_changed_through_the_returned_value(stock):
    assert isinstance(stock.shoes, tuple)


# ---- Lowest and highest ----------------------------------------------------

def test_lowest_stock(stock):
    assert stock.lowest_stock().code == "SKU2"


def test_highest_stock(stock):
    assert stock.highest_stock().code == "SKU3"


def test_ties_go_to_the_first_shoe_in_the_list():
    stock = Stock([make_shoe("A", quantity=4), make_shoe("B", quantity=4)])
    assert stock.lowest_stock().code == "A"
    assert stock.highest_stock().code == "A"


def test_lowest_and_highest_of_an_empty_stock_are_none():
    assert Stock().lowest_stock() is None
    assert Stock().highest_stock() is None


# ---- Restocking ------------------------------------------------------------

def test_restock_adds_to_the_quantity_and_returns_the_updated_shoe(stock):
    updated = stock.restock("SKU2", 10)
    assert updated.quantity == 12
    assert stock.find("SKU2").quantity == 12


def test_restock_keeps_the_shoe_in_the_same_position(stock):
    stock.restock("SKU2", 10)
    assert [shoe.code for shoe in stock.shoes] == ["SKU1", "SKU2", "SKU3"]


def test_restock_leaves_other_shoes_alone(stock):
    stock.restock("SKU2", 10)
    assert stock.find("SKU1").quantity == 5
    assert stock.find("SKU3").quantity == 9


def test_restock_finds_the_code_ignoring_case(stock):
    assert stock.restock("sku1", 1).quantity == 6


@pytest.mark.parametrize("amount", [0, -5])
def test_restock_rejects_an_amount_that_is_not_above_zero(stock, amount):
    with pytest.raises(ValueError):
        stock.restock("SKU1", amount)
    assert stock.find("SKU1").quantity == 5


def test_restock_rejects_an_unknown_code(stock):
    with pytest.raises(UnknownCodeError):
        stock.restock("SKU404", 1)


# ---- Value -----------------------------------------------------------------

def test_total_value_adds_up_every_shoe(stock):
    # 5*10 + 2*10 + 9*10
    assert stock.total_value() == Decimal("160")


def test_total_value_of_an_empty_stock_is_zero():
    assert Stock().total_value() == Decimal("0")

from decimal import Decimal

from solestock import display
from solestock.models import Shoe


def make_shoe(code="SKU1", product="Alpha", cost="10", quantity=5,
              country="Chile"):
    return Shoe(country, code, product, Decimal(cost), quantity)


def test_format_money_adds_separators_and_two_decimals():
    assert display.format_money(Decimal("2300")) == "2,300.00"
    assert display.format_money(Decimal("1234567.5")) == "1,234,567.50"
    assert display.format_money(Decimal("0")) == "0.00"


def test_format_shoe_describes_the_shoe_on_one_line():
    text = display.format_shoe(make_shoe(cost="2300", quantity=20))
    assert text == "Alpha (SKU1, Chile): 20 in stock at 2,300.00 each"


def test_table_of_no_shoes_says_so():
    assert display.format_table([]) == display.EMPTY_MESSAGE


def test_table_has_a_header_a_rule_and_one_line_per_shoe():
    lines = display.format_table([
        make_shoe("SKU1", "Alpha"), make_shoe("SKU2", "Beta"),
    ]).splitlines()

    assert len(lines) == 4
    for name in display.HEADERS:
        assert name in lines[0]
    assert set(lines[1]) == {"-"}
    assert "Alpha" in lines[2]
    assert "Beta" in lines[3]


def test_table_columns_line_up_whatever_the_content():
    lines = display.format_table([
        make_shoe("SKU1", "A", cost="5", quantity=1),
        make_shoe("SKU2", "A very long product name indeed",
                  cost="1234567.89", quantity=12345),
    ]).splitlines()

    assert len({len(line) for line in lines}) == 1


def test_numbers_are_right_aligned_in_the_table():
    lines = display.format_table([
        make_shoe("SKU1", quantity=5), make_shoe("SKU2", quantity=120),
    ]).splitlines()

    assert lines[2].endswith("  5")
    assert lines[3].endswith("120")


def test_values_list_each_product_then_the_total():
    shoes = [
        make_shoe("SKU1", "Alpha", cost="100", quantity=5),
        make_shoe("SKU2", "Beta", cost="200.50", quantity=2),
    ]
    lines = display.format_values(shoes, Decimal("901")).splitlines()

    assert lines[0].startswith("Alpha") and lines[0].endswith("500.00")
    assert lines[1].startswith("Beta") and lines[1].endswith("401.00")
    assert set(lines[2]) == {"-"}
    assert lines[3].startswith("Total") and lines[3].endswith("901.00")


def test_values_line_up_even_when_the_total_is_wider():
    shoes = [make_shoe("SKU1", "A", cost="999", quantity=1),
             make_shoe("SKU2", "B", cost="999", quantity=1)]
    lines = display.format_values(shoes, Decimal("1998")).splitlines()

    assert len({len(line) for line in lines}) == 1


def test_values_of_no_shoes_says_so():
    assert display.format_values([], Decimal(0)) == display.EMPTY_MESSAGE

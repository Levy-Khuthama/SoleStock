from decimal import Decimal

import pytest

from solestock import prompts


def test_ask_text_repeats_until_something_is_entered(feed, capsys):
    feed("", "   ", "Chile")
    assert prompts.ask_text("Country: ") == "Chile"
    assert capsys.readouterr().out.count("cannot be blank") == 2


def test_ask_text_strips_spaces(feed):
    feed("  Chile  ")
    assert prompts.ask_text("Country: ") == "Chile"


def test_ask_cost_accepts_a_decimal(feed):
    feed("19.99")
    assert prompts.ask_cost("Cost: ") == Decimal("19.99")


def test_ask_cost_accepts_zero(feed):
    feed("0")
    assert prompts.ask_cost("Cost: ") == Decimal("0")


def test_ask_cost_rejects_text_negatives_and_non_finite_values(feed, capsys):
    feed("abc", "-5", "nan", "inf", "1299.50")
    assert prompts.ask_cost("Cost: ") == Decimal("1299.50")
    output = capsys.readouterr().out
    assert output.count("Invalid input") == 1
    assert output.count("zero or more") == 3


def test_ask_quantity_rejects_text_decimals_and_negatives(feed, capsys):
    feed("x", "2.5", "-1", "7")
    assert prompts.ask_quantity("Quantity: ") == 7
    output = capsys.readouterr().out
    assert output.count("Invalid input") == 2
    assert output.count("cannot be negative") == 1


def test_ask_quantity_accepts_zero(feed):
    feed("0")
    assert prompts.ask_quantity("Quantity: ") == 0


def test_ask_positive_number_rejects_zero_and_negatives(feed, capsys):
    feed("0", "-3", "4")
    assert prompts.ask_positive_number("Add: ") == 4
    assert capsys.readouterr().out.count("above zero") == 2


@pytest.mark.parametrize("answer", ["y", "YES", " Yes "])
def test_ask_yes_no_understands_yes(feed, answer):
    feed(answer)
    assert prompts.ask_yes_no("Sure? ") is True


@pytest.mark.parametrize("answer", ["n", "No", " NO "])
def test_ask_yes_no_understands_no(feed, answer):
    feed(answer)
    assert prompts.ask_yes_no("Sure? ") is False


def test_ask_yes_no_repeats_on_anything_else(feed, capsys):
    feed("maybe", "", "yes")
    assert prompts.ask_yes_no("Sure? ") is True
    assert capsys.readouterr().out.count("'yes' or 'no'") == 2


def test_a_closed_input_stream_is_not_swallowed(feed):
    feed()
    with pytest.raises(EOFError):
        prompts.ask_text("Country: ")

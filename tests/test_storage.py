import os
import stat
import sys
from decimal import Decimal
from pathlib import Path

import pytest

from solestock import storage
from solestock.models import Shoe
from solestock.storage import (
    InventoryFileError,
    InventoryFileNotFound,
    backup_file,
    load_shoes,
    parse_row,
    save_shoes,
)

# A pinned copy of the original data. The live inventory.txt is edited by the
# program itself, so the tests must not depend on its contents.
SAMPLE_INVENTORY = (
    Path(__file__).resolve().parent / "data" / "sample_inventory.txt"
)
HEADER = "Country,Code,Product,Cost,Quantity"


def write(path, text, encoding="utf-8"):
    path.write_bytes(text.encode(encoding))
    return path


# ---- parse_row -------------------------------------------------------------

def test_parse_row_builds_a_shoe():
    shoe = parse_row(["Chile", "SKU1", "Boot", "19.99", "4"])
    assert shoe == Shoe("Chile", "SKU1", "Boot", Decimal("19.99"), 4)


def test_parse_row_trims_spaces():
    shoe = parse_row([" Chile ", " SKU1 ", " Boot ", " 5 ", " 4 "])
    assert (shoe.country, shoe.code, shoe.product) == ("Chile", "SKU1", "Boot")
    assert shoe.cost == Decimal("5")


@pytest.mark.parametrize("row, message", [
    (["Chile", "SKU1", "Boot", "5"], "expected 5 fields but found 4"),
    (["Chile", "SKU1", "Boot", "5", "4", "x"], "found 6"),
    (["", "SKU1", "Boot", "5", "4"], "country is blank"),
    (["Chile", " ", "Boot", "5", "4"], "code is blank"),
    (["Chile", "SKU1", "", "5", "4"], "product is blank"),
    (["Chile", "SKU1", "Boot", "abc", "4"], "'abc' is not a number"),
    (["Chile", "SKU1", "Boot", "-1", "4"], "must be zero or more"),
    (["Chile", "SKU1", "Boot", "nan", "4"], "must be zero or more"),
    (["Chile", "SKU1", "Boot", "5", "x"], "not a whole number"),
    (["Chile", "SKU1", "Boot", "5", "2.5"], "not a whole number"),
    (["Chile", "SKU1", "Boot", "5", "-3"], "cannot be negative"),
])
def test_parse_row_rejects_bad_rows(row, message):
    with pytest.raises(ValueError, match=message):
        parse_row(row)


# ---- load_shoes ------------------------------------------------------------

def test_load_reads_the_shoes(tmp_path):
    path = write(tmp_path / "i.txt",
                 f"{HEADER}\nChile,SKU1,Boot,10,2\nPeru,SKU2,Clog,5.50,1\n")
    result = load_shoes(path)

    assert [shoe.code for shoe in result.shoes] == ["SKU1", "SKU2"]
    assert result.problems == []


def test_load_ignores_blank_lines_without_losing_rows(tmp_path):
    path = write(
        tmp_path / "i.txt",
        f"{HEADER}\nChile,SKU1,Boot,10,2\n\n   \nPeru,SKU2,Clog,5,1\n\n",
    )
    result = load_shoes(path)

    assert len(result.shoes) == 2
    assert result.problems == []


def test_load_reports_bad_rows_with_their_line_numbers(tmp_path):
    path = write(
        tmp_path / "i.txt",
        f"{HEADER}\nChile,SKU1,Boot,10,2\nbroken row\nPeru,SKU2,Clog,x,1\n",
    )
    result = load_shoes(path)

    assert [shoe.code for shoe in result.shoes] == ["SKU1"]
    assert len(result.problems) == 2
    assert result.problems[0].startswith("line 3:")
    assert result.problems[1].startswith("line 4:")


def test_load_skips_a_repeated_code_and_says_so(tmp_path):
    path = write(
        tmp_path / "i.txt",
        f"{HEADER}\nChile,SKU1,Boot,10,2\nPeru,sku1,Clog,5,1\n",
    )
    result = load_shoes(path)

    assert len(result.shoes) == 1
    assert "line 3" in result.problems[0]
    assert "already used" in result.problems[0]


def test_load_accepts_a_file_without_a_header(tmp_path):
    path = write(tmp_path / "i.txt", "Chile,SKU1,Boot,10,2\n")
    result = load_shoes(path)

    assert len(result.shoes) == 1
    assert result.problems == []


def test_load_reports_a_headerless_bad_first_row(tmp_path):
    path = write(tmp_path / "i.txt", "Country,Code\nChile,SKU1,Boot,10,2\n")
    result = load_shoes(path)

    assert len(result.shoes) == 1
    assert result.problems[0].startswith("line 1:")


def test_load_an_empty_file_gives_no_shoes_and_no_problems(tmp_path):
    result = load_shoes(write(tmp_path / "i.txt", ""))
    assert result.shoes == [] and result.problems == []


def test_load_a_header_only_file_gives_no_shoes(tmp_path):
    result = load_shoes(write(tmp_path / "i.txt", HEADER + "\n"))
    assert result.shoes == [] and result.problems == []


def test_load_handles_windows_line_endings(tmp_path):
    path = write(tmp_path / "i.txt",
                 f"{HEADER}\r\nChile,SKU1,Boot,10,2\r\n")
    assert len(load_shoes(path).shoes) == 1


def test_load_handles_a_byte_order_mark(tmp_path):
    path = write(tmp_path / "i.txt",
                 f"{HEADER}\nChile,SKU1,Boot,10,2\n", encoding="utf-8-sig")
    result = load_shoes(path)

    assert len(result.shoes) == 1
    assert result.problems == []


def test_load_keeps_a_comma_inside_quotes(tmp_path):
    path = write(tmp_path / "i.txt",
                 f'{HEADER}\nChile,SKU1,"Boot, tall",10,2\n')
    assert load_shoes(path).shoes[0].product == "Boot, tall"


def test_load_a_missing_file_raises_not_found(tmp_path):
    with pytest.raises(InventoryFileNotFound):
        load_shoes(tmp_path / "nope.txt")


def test_load_a_file_that_is_not_text_raises_a_file_error(tmp_path):
    path = tmp_path / "i.txt"
    path.write_bytes(b"\xff\xfe\x00\x80\x81")
    with pytest.raises(InventoryFileError):
        load_shoes(path)


def test_load_a_folder_raises_a_file_error(tmp_path):
    with pytest.raises(InventoryFileError):
        load_shoes(tmp_path)


def test_the_sample_inventory_file_loads_cleanly():
    result = load_shoes(SAMPLE_INVENTORY)

    assert len(result.shoes) == 24
    assert result.problems == []


# ---- save_shoes ------------------------------------------------------------

def test_save_then_load_gives_the_same_shoes(tmp_path):
    shoes = [
        Shoe("Chile", "SKU1", "Boot, tall", Decimal("10.50"), 2),
        Shoe("Peru", "SKU2", 'The "Clog"', Decimal("5"), 0),
    ]
    path = tmp_path / "i.txt"

    save_shoes(path, shoes)

    assert load_shoes(path).shoes == shoes


def test_save_writes_the_header_and_unix_line_endings(tmp_path):
    path = tmp_path / "i.txt"
    save_shoes(path, [Shoe("Chile", "SKU1", "Boot", Decimal("10"), 2)])

    assert path.read_bytes() == (
        b"Country,Code,Product,Cost,Quantity\nChile,SKU1,Boot,10,2\n"
    )


def test_save_keeps_costs_exactly_as_they_were_written(tmp_path):
    # 2700.0 and 2300 must not turn into each other on a round trip.
    path = write(tmp_path / "i.txt",
                 f"{HEADER}\nA,S1,X,2700.0,1\nB,S2,Y,2300,1\n")

    save_shoes(path, load_shoes(path).shoes)

    assert path.read_text().splitlines()[1:] == [
        "A,S1,X,2700.0,1", "B,S2,Y,2300,1",
    ]


def test_the_sample_inventory_survives_a_save_unchanged(tmp_path):
    copy = tmp_path / "inventory.txt"
    copy.write_bytes(SAMPLE_INVENTORY.read_bytes())

    save_shoes(copy, load_shoes(copy).shoes)

    # Only the missing final newline in the original may differ.
    assert copy.read_text().splitlines() == (
        SAMPLE_INVENTORY.read_text().splitlines()
    )


def test_save_creates_a_missing_file(tmp_path):
    path = tmp_path / "new.txt"
    save_shoes(path, [])
    assert path.read_text() == HEADER + "\n"


def test_a_failed_save_leaves_the_original_and_no_temp_file(
        tmp_path, monkeypatch):
    path = write(tmp_path / "i.txt", f"{HEADER}\nChile,SKU1,Boot,10,2\n")
    original = path.read_bytes()

    def failing_replace(source, destination):
        raise OSError("disk full")

    monkeypatch.setattr(storage.os, "replace", failing_replace)

    with pytest.raises(InventoryFileError, match="disk full"):
        save_shoes(path, [Shoe("Peru", "SKU2", "Clog", Decimal("5"), 1)])

    assert path.read_bytes() == original
    assert list(tmp_path.glob("*.tmp")) == []


def test_saving_into_a_missing_folder_raises_a_file_error(tmp_path):
    with pytest.raises(InventoryFileError):
        save_shoes(tmp_path / "nope" / "i.txt", [])


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permissions")
def test_save_keeps_the_file_permissions(tmp_path):
    path = write(tmp_path / "i.txt", HEADER + "\n")
    os.chmod(path, 0o640)

    save_shoes(path, [])

    assert stat.S_IMODE(os.stat(path).st_mode) == 0o640


# ---- backup_file -----------------------------------------------------------

def test_backup_copies_the_file_next_to_it(tmp_path):
    path = write(tmp_path / "i.txt", "original")

    backup = backup_file(path)

    assert backup == tmp_path / "i.txt.bak"
    assert backup.read_text() == "original"


def test_backup_of_a_missing_file_raises_a_file_error(tmp_path):
    with pytest.raises(InventoryFileError):
        backup_file(tmp_path / "nope.txt")

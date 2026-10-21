"""End-to-end tests: scripted keystrokes driving the real menu and files.

Several of these reproduce bugs found in the original script, so each fix
stays fixed.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from solestock.cli import main
from solestock.storage import load_shoes

HEADER = "Country,Code,Product,Cost,Quantity"
ROOT = Path(__file__).resolve().parent.parent


def run(feed, capsys, path, *answers):
    """Run the program on ``path`` with scripted answers; return its output."""
    feed(*answers)
    code = main(["--file", str(path)])
    assert code == 0
    return capsys.readouterr().out


def rows(path):
    return path.read_text(encoding="utf-8").splitlines()[1:]


# ---- Basic menu behaviour --------------------------------------------------

def test_exit(feed, capsys, inventory_file):
    out = run(feed, capsys, inventory_file, "8")
    assert "Loaded 3 shoes from inventory.txt." in out
    assert "Goodbye" in out


def test_invalid_menu_choices_do_not_crash(feed, capsys, inventory_file):
    out = run(feed, capsys, inventory_file, "x", "", "9", "8")
    assert out.count("Invalid choice") == 3


def test_view_all_lists_every_shoe(feed, capsys, inventory_file):
    out = run(feed, capsys, inventory_file, "3", "8")
    for name in ("Alpha", "Beta", "Gamma"):
        assert name in out


def test_search_ignores_case(feed, capsys, inventory_file):
    out = run(feed, capsys, inventory_file, "5", "sku2", "8")
    assert "Found: Beta (SKU2, China)" in out


def test_search_says_when_nothing_matches(feed, capsys, inventory_file):
    out = run(feed, capsys, inventory_file, "5", "SKU404", "8")
    assert "No shoe found with code SKU404" in out


def test_values_show_each_item_and_the_total(feed, capsys, inventory_file):
    out = run(feed, capsys, inventory_file, "6", "8")
    # 100*5 + 200.50*2 + 50*9
    assert "1,351.00" in out
    assert "Total" in out


def test_highest_stock_goes_on_sale(feed, capsys, inventory_file):
    out = run(feed, capsys, inventory_file, "7", "8")
    assert "The highest stock is: Gamma" in out
    assert "Gamma is now on sale!" in out


def test_reload_does_not_duplicate_shoes(feed, capsys, inventory_file):
    # Original bug: every reload appended the file's shoes a second time.
    out = run(feed, capsys, inventory_file, "1", "1", "3", "8")
    assert out.count("Loaded 3 shoes") == 3  # start-up plus two reloads
    assert out.count("Alpha") == 1


# ---- Capturing -------------------------------------------------------------

def test_capture_is_saved_to_the_file(feed, capsys, inventory_file):
    # Original bug: captured shoes only lived in memory.
    out = run(feed, capsys, inventory_file,
              "2", "Chile", "SKU9", "Delta", "75.25", "6", "8")

    assert "Captured: Delta (SKU9, Chile)" in out
    assert rows(inventory_file)[-1] == "Chile,SKU9,Delta,75.25,6"
    assert len(load_shoes(inventory_file).shoes) == 4


def test_capture_survives_a_restart(feed, capsys, inventory_file):
    run(feed, capsys, inventory_file,
        "2", "Chile", "SKU9", "Delta", "75.25", "6", "8")
    out = run(feed, capsys, inventory_file, "5", "SKU9", "8")

    assert "Found: Delta" in out


def test_capture_refuses_a_code_that_already_exists(
        feed, capsys, inventory_file):
    # Original bug: a shared code silently overwrote the other shoe.
    before = inventory_file.read_text()
    out = run(feed, capsys, inventory_file, "2", "Chile", "sku1", "8")

    assert "already exists" in out
    assert inventory_file.read_text() == before


def test_capture_asks_again_after_bad_input(feed, capsys, inventory_file):
    # Original bug: text where a number was expected crashed the program.
    out = run(feed, capsys, inventory_file,
              "2", "Chile", "SKU9", "Delta",
              "cheap", "-4", "20",
              "lots", "2.5", "-1", "3",
              "8")

    assert "Traceback" not in out
    assert rows(inventory_file)[-1] == "Chile,SKU9,Delta,20,3"


def test_capture_creates_the_file_when_it_is_missing(
        feed, capsys, tmp_path):
    path = tmp_path / "fresh.txt"
    out = run(feed, capsys, path,
              "2", "Chile", "SKU1", "Boot", "10", "2", "8")

    assert "No inventory file" in out
    assert path.read_text() == HEADER + "\nChile,SKU1,Boot,10,2\n"


# ---- Restocking ------------------------------------------------------------

def test_restock_updates_the_lowest_shoe_and_saves(
        feed, capsys, inventory_file):
    out = run(feed, capsys, inventory_file, "4", "yes", "10", "8")

    assert "The lowest stock is: Beta" in out
    assert "Updated: Beta (SKU2, China): 12 in stock" in out
    assert "China,SKU2,Beta,200.50,12" in rows(inventory_file)


def test_restock_can_be_declined(feed, capsys, inventory_file):
    before = inventory_file.read_text()
    out = run(feed, capsys, inventory_file, "4", "no", "8")

    assert "Restock cancelled" in out
    assert inventory_file.read_text() == before


def test_restock_rejects_zero_and_negative_amounts(
        feed, capsys, inventory_file):
    # Original bug: a negative restock removed stock.
    run(feed, capsys, inventory_file, "4", "yes", "-5", "0", "1", "8")

    assert "China,SKU2,Beta,200.50,3" in rows(inventory_file)


def test_restock_of_an_empty_inventory(feed, capsys, tmp_path):
    path = tmp_path / "i.txt"
    path.write_text(HEADER + "\n")
    out = run(feed, capsys, path, "4", "8")

    assert "no shoes" in out


# ---- Protecting the file ---------------------------------------------------

def test_a_blank_line_in_the_file_does_not_lose_rows(
        feed, capsys, tmp_path):
    # Original bug: a blank line stopped loading, and the next save then
    # wiped every row after it.
    path = tmp_path / "i.txt"
    path.write_text(f"{HEADER}\nA,S1,X,10,1\n\nB,S2,Y,20,2\nC,S3,Z,30,3\n")

    run(feed, capsys, path, "2", "Chile", "S9", "New", "5", "5", "8")

    assert len(rows(path)) == 4  # 3 original rows + 1 new row
    assert {row.split(",")[1] for row in rows(path)} == {
        "S1", "S2", "S3", "S9",
    }


def test_a_bad_row_is_reported_and_a_backup_keeps_the_original(
        feed, capsys, tmp_path):
    path = tmp_path / "i.txt"
    original = f"{HEADER}\nA,S1,X,10,1\nnot a shoe\nC,S3,Z,30,3\n"
    path.write_text(original)

    out = run(feed, capsys, path, "2", "Chile", "S9", "New", "5", "5", "8")

    assert "Skipped 1 row" in out
    assert "line 3" in out
    assert (tmp_path / "i.txt.bak").read_text() == original


def test_the_backup_holds_the_file_from_before_the_first_change(
        feed, capsys, inventory_file):
    original = inventory_file.read_text()

    run(feed, capsys, inventory_file,
        "2", "Chile", "SKU8", "One", "1", "1",
        "2", "Chile", "SKU9", "Two", "2", "2",
        "8")

    backup = inventory_file.with_name("inventory.txt.bak")
    assert backup.read_text() == original  # not overwritten by the 2nd save


def test_no_backup_is_made_when_nothing_changes(
        feed, capsys, inventory_file):
    run(feed, capsys, inventory_file, "3", "5", "SKU1", "8")
    assert not inventory_file.with_name("inventory.txt.bak").exists()


def test_a_failed_save_is_reported_not_hidden(
        feed, capsys, inventory_file, monkeypatch):
    def failing_replace(source, destination):
        raise OSError("disk full")

    monkeypatch.setattr("solestock.storage.os.replace", failing_replace)
    before = inventory_file.read_text()

    out = run(feed, capsys, inventory_file,
              "2", "Chile", "SKU9", "Delta", "1", "1", "8")

    assert "NOT saved" in out
    assert inventory_file.read_text() == before


def test_an_unreadable_file_stops_the_program_with_an_error(
        feed, capsys, tmp_path):
    path = tmp_path / "i.txt"
    path.write_bytes(b"\xff\xfe\x00\x80\x81")
    feed("8")

    assert main(["--file", str(path)]) == 1

    assert "Could not read" in capsys.readouterr().out
    assert path.read_bytes() == b"\xff\xfe\x00\x80\x81"


# ---- Leaving the program ---------------------------------------------------

def test_ctrl_d_exits_cleanly(feed, capsys, inventory_file):
    # Original bug: Ctrl+D at the menu printed a traceback.
    out = run(feed, capsys, inventory_file)  # no answers: input() hits EOF
    assert "Goodbye" in out
    assert "Traceback" not in out


def test_ctrl_d_part_way_through_capture_exits_cleanly(
        feed, capsys, inventory_file):
    before = inventory_file.read_text()
    out = run(feed, capsys, inventory_file, "2", "Chile")

    assert "Goodbye" in out
    assert inventory_file.read_text() == before


def test_ctrl_c_exits_cleanly(monkeypatch, capsys, inventory_file):
    def interrupt(prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", interrupt)

    assert main(["--file", str(inventory_file)]) == 0
    assert "Goodbye" in capsys.readouterr().out


# ---- The real script -------------------------------------------------------

@pytest.mark.skipif(sys.platform == "win32", reason="uses a POSIX shell cwd")
def test_the_script_finds_its_file_from_any_folder(tmp_path):
    # Original bug: it only worked when run from its own folder.
    result = subprocess.run(
        [sys.executable, str(ROOT / "solestock.py")],
        input="8\n", capture_output=True, text=True, cwd=tmp_path,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=30,
    )

    assert result.returncode == 0
    # The count depends on the live file, so only check that it was found.
    assert re.search(r"Loaded \d+ shoes from inventory\.txt\.", result.stdout)
    assert result.stderr == ""

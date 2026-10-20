# SoleStock

[![CI](https://github.com/Levy-Khuthama/solestock/actions/workflows/ci.yml/badge.svg)](https://github.com/Levy-Khuthama/solestock/actions/workflows/ci.yml)

**SoleStock** is a command-line program for a shoe warehouse. It keeps stock
in a plain CSV file and lets you search it, restock it, add new shoes and see
what the stock is worth. Python 3.9+, no third-party packages needed to run
it.

Built as a HyperionDev bootcamp task, then reworked to production standard:
validated input, safe file handling, tests and continuous integration.

## Run it

```bash
python solestock.py                      # uses inventory.txt next to the script
python solestock.py --file other.txt     # use a different file
```

It works from any folder, because the default file is found relative to the
script, not to where you happen to be.

## What it does

| # | Option | What happens |
|---|--------|--------------|
| 1 | Reload shoe data | Re-reads the file, replacing what is in memory |
| 2 | Capture a new shoe | Asks for the details, checks them, saves to the file |
| 3 | View all shoes | Prints an aligned table |
| 4 | Restock | Finds the lowest-stock shoe and adds the quantity you choose |
| 5 | Search by code | Finds a shoe, ignoring upper/lower case |
| 6 | Value of each item | Cost x quantity per shoe, plus the total |
| 7 | Highest quantity | Shows the best-stocked shoe and marks it as on sale |
| 8 | Exit | |

## A real session

Recorded by driving the program in a terminal (menu reprinted between steps
is trimmed):

```text
Loaded 24 shoes from inventory.txt.
Enter your choice (1-8): 5
Enter the shoe code to search: sku7
No shoe found with code sku7.

Enter your choice (1-8): 4
The lowest stock is: Air Foamposite (SKU79084, Israel): 4 in stock at 2,430.00 each
Do you want to restock this shoe? (yes/no): yes
Enter the quantity to add: -5
Please enter a number above zero.
Enter the quantity to add: 10
Updated: Air Foamposite (SKU79084, Israel): 14 in stock at 2,430.00 each

Enter your choice (1-8): 2
Enter the country of the shoe: Chile
Enter the code of the shoe: SKU7
Enter the product name: Trail Runner
Enter the cost of the shoe: cheap
Invalid input. Please enter a number such as 1299.50.
Enter the cost of the shoe: 89.99
Enter the quantity of the shoe: 12
Captured: Trail Runner (SKU7, Chile): 12 in stock at 89.99 each

Enter your choice (1-8): 6
...
Trail Runner             1,079.88
---------------------------------
Total                1,383,616.88
```

## The data file

A CSV with a header row:

```text
Country,Code,Product,Cost,Quantity
South Africa,SKU44386,Air Max 90,2300,20
```

- Codes are unique. They are compared ignoring case and surrounding spaces.
- Blank lines are ignored. A bad row is skipped and reported with its line
  number, so one typo never hides the rest of the file.
- Every change is saved straight away. The file is written to a temporary
  copy and swapped in only when complete, so a crash or full disk cannot leave
  a half-written inventory.
- The first time the program saves, it keeps a copy of the file as it was at
  start-up in `inventory.txt.bak`.

## Design

```text
solestock.py            entry point
solestock/
  models.py             Shoe: an immutable record; value = cost x quantity
  stock.py              Stock: the rules (unique codes, restock, lowest/highest)
  storage.py            reading and safely writing the CSV
  prompts.py            asking for validated input
  display.py            turning shoes into text; no printing, no input
  menu.py               the menu and what each option does
  cli.py                command-line options and start-up
tests/                  114 tests, unit and end-to-end
```

The logic (`stock`, `storage`, `display`) never calls `input()` or `print()`,
which is why it can be tested without a terminal. Money is held as `Decimal`,
so 0.10 x 3 is exactly 0.30 rather than 0.30000000000000004.

## Tests and style

```bash
pip install -r requirements-dev.txt
pytest        # 114 tests
flake8        # PEP 8
```

GitHub Actions runs both on every push, on Python 3.9 and 3.12. The
end-to-end tests drive the real menu with scripted keystrokes.

## What changed from the original

The first version worked on the happy path. Reviewing it turned up bugs, each
now fixed and covered by a test:

| Problem in the original | Now |
|---|---|
| Reloading added every shoe a second time | Reload replaces the stock |
| Typing text for a cost or quantity crashed | Asks again, with a clear message |
| New shoes were lost when the program closed | Saved to the file straight away |
| A blank line in the file stopped loading, and the next save wiped the rest | Blank lines ignored; nothing is lost |
| A new shoe with an existing code overwrote the other shoe | Refused |
| Search was case-sensitive | `sku7` finds `SKU7` |
| Only worked when run from its own folder | Finds its file wherever it runs |
| Ctrl+D at the menu printed a traceback | Exits cleanly |
| Saving rewrote costs (2700.0 became 2700) | Costs are kept as written |
| A negative restock removed stock | Must be above zero |
| Needed the `tabulate` package | Aligned table built in, no dependencies |

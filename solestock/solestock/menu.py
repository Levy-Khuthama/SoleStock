"""The menu and the actions behind each option."""

from __future__ import annotations

from pathlib import Path
from typing import List

from . import display, prompts
from .models import Shoe
from .stock import DuplicateCodeError, Stock
from .storage import (
    InventoryFileError,
    PathLike,
    backup_file,
    load_shoes,
    save_shoes,
)

MENU = """
SoleStock: Shoe Inventory Manager
1. Reload shoe data from file
2. Capture a new shoe
3. View all shoes
4. Restock the shoe with the lowest quantity
5. Search for a shoe by code
6. Show the value of each item
7. Show the shoe with the highest quantity (on sale)
8. Exit"""

MAX_PROBLEMS_SHOWN = 5


def report_problems(problems: List[str]) -> None:
    """Print the rows skipped while loading, so they are never silent."""
    if not problems:
        return

    count = len(problems)
    print(f"Skipped {count} row{'s' if count != 1 else ''}:")
    for problem in problems[:MAX_PROBLEMS_SHOWN]:
        print(f"  {problem}")
    if count > MAX_PROBLEMS_SHOWN:
        print(f"  ...and {count - MAX_PROBLEMS_SHOWN} more.")
    print("Skipped rows are left out when the file is next saved. A copy of "
          "the original is kept as a .bak file.")


class InventoryApp:
    """The running program: the stock plus the file it is saved to."""

    def __init__(self, stock: Stock, path: PathLike) -> None:
        self.stock = stock
        self.path = Path(path)
        self._backup_made = False

    # ---- Saving ----------------------------------------------------------

    def _save(self) -> None:
        """Save the stock, keeping a backup of the file on the first save.

        The backup holds the file exactly as it was when the program
        started, whatever happens afterwards.
        """
        try:
            if not self._backup_made and self.path.exists():
                backup_file(self.path)
            self._backup_made = True
            save_shoes(self.path, self.stock.shoes)
        except InventoryFileError as error:
            print(f"{error}\nThe change was NOT saved to the file.")

    # ---- Actions ---------------------------------------------------------

    def reload(self) -> None:
        """Replace the stock with what is currently in the file."""
        try:
            result = load_shoes(self.path)
        except InventoryFileError as error:
            print(error)
            return

        self.stock = Stock(result.shoes)
        print(f"Loaded {len(self.stock)} shoes from {self.path.name}.")
        report_problems(result.problems)

    def capture(self) -> None:
        """Add a new shoe and save it to the file."""
        print("\nCapture a new shoe")
        country = prompts.ask_text("Enter the country of the shoe: ")
        code = prompts.ask_text("Enter the code of the shoe: ")
        if self.stock.find(code) is not None:
            print(f"A shoe with code {code} already exists.")
            return

        product = prompts.ask_text("Enter the product name: ")
        cost = prompts.ask_cost("Enter the cost of the shoe: ")
        quantity = prompts.ask_quantity("Enter the quantity of the shoe: ")
        shoe = Shoe(country, code, product, cost, quantity)

        try:
            self.stock.add(shoe)
        except DuplicateCodeError as error:
            print(error)
            return

        self._save()
        print(f"Captured: {display.format_shoe(shoe)}")

    def view_all(self) -> None:
        """Show every shoe in a table."""
        print()
        print(display.format_table(self.stock.shoes))

    def restock(self) -> None:
        """Offer to add stock to the shoe with the lowest quantity."""
        shoe = self.stock.lowest_stock()
        if shoe is None:
            print("There are no shoes in the inventory to restock.")
            return

        print(f"The lowest stock is: {display.format_shoe(shoe)}")
        if not prompts.ask_yes_no("Do you want to restock this shoe? "
                                  "(yes/no): "):
            print("Restock cancelled.")
            return

        amount = prompts.ask_positive_number("Enter the quantity to add: ")
        updated = self.stock.restock(shoe.code, amount)
        self._save()
        print(f"Updated: {display.format_shoe(updated)}")

    def search(self) -> None:
        """Find a shoe by its code."""
        code = prompts.ask_text("Enter the shoe code to search: ")
        shoe = self.stock.find(code)
        if shoe is None:
            print(f"No shoe found with code {code}.")
        else:
            print(f"Found: {display.format_shoe(shoe)}")

    def show_values(self) -> None:
        """Show the total value of each shoe, and of all the stock."""
        print()
        print(display.format_values(self.stock.shoes,
                                    self.stock.total_value()))

    def show_highest(self) -> None:
        """Show the shoe with the most in stock and mark it as on sale."""
        shoe = self.stock.highest_stock()
        if shoe is None:
            print("There are no shoes in the inventory.")
            return

        print(f"The highest stock is: {display.format_shoe(shoe)}")
        print(f"{shoe.product} is now on sale!")

    # ---- Main loop -------------------------------------------------------

    def run(self) -> None:
        """Show the menu until the user exits.

        Ctrl+C and Ctrl+D leave the program cleanly instead of showing a
        traceback.
        """
        actions = {
            "1": self.reload,
            "2": self.capture,
            "3": self.view_all,
            "4": self.restock,
            "5": self.search,
            "6": self.show_values,
            "7": self.show_highest,
        }

        try:
            while True:
                print(MENU)
                choice = input("Enter your choice (1-8): ").strip()

                if choice == "8":
                    break

                action = actions.get(choice)
                if action is None:
                    print("Invalid choice. Please enter a number "
                          "between 1 and 8.")
                    continue
                action()
        except (EOFError, KeyboardInterrupt):
            print()

        print("Exiting program. Goodbye!")

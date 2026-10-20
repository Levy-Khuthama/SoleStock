"""SoleStock: a shoe inventory manager.

Run with ``python solestock.py``. The program itself lives in the
``solestock`` package; this file is only the entry point.
"""

import sys

from solestock.cli import main

if __name__ == "__main__":
    sys.exit(main())

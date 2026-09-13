"""CLI convenience entry point; inputs and exit statuses match astra-pcb."""

import sys

from astra_pcb.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["check-datasheet-limits"] + sys.argv[1:]))

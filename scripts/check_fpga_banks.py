"""CLI convenience entry point; inputs and exit statuses match astra-pcb."""

import sys

from astra_pcb.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["check", "check_fpga_banks"] + sys.argv[1:]))

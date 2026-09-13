"""Compatibility entry point for environment."""

import sys

from astra_pcb.cli import main

raise SystemExit(main(["environment", *sys.argv[1:]]))

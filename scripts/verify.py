"""Compatibility entry point for verify."""

import sys

from astra_pcb.cli import main

raise SystemExit(main(["verify", *sys.argv[1:]]))

"""Compatibility entry point for release."""

import sys

from astra_pcb.cli import main

raise SystemExit(main(["release", *sys.argv[1:]]))

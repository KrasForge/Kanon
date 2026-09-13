# Developer entry points

Run from the repository root after installing the package. verify.py,
check_environment.py and release.py delegate to the CLI; check_bom.py consumes a JSON
array of canonical BOM rows. Release intentionally reports ERROR until M4 is implemented.

Decoupling, pinmap, FPGA banks, datasheet-limit and power/filter workflow scripts are not
created: their engineering implementations are backlog work. The simulation library has
real batch execution and scalar assertions, but no topology-specific workflow yet.

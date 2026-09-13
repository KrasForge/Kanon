# Read-only PCB verifier MCP

Launch `uv run python -m astra_pcb.verifier` from the repository after installation.
The stdio server implements MCP 2025-06-18 initialize, ping, tools/list and tools/call.
`tools/list` supplies the exact Pydantic input schemas. It advertises only implemented
checks; an unknown tool is an error. Tool results contain a typed VerificationReport in
both text and structuredContent. An ERROR sets isError; engineering FAIL remains a
successful tool invocation carrying a failed engineering result. Neither is approval.

The 17 tools are:

| Tool | Input and checked scope |
|---|---|
| check_power_tree | Declared PowerTree graph, sources, loads and current budgets |
| check_regulator | PowerTree and cited Regulator operating/thermal limits |
| check_bom | Canonical per-reference BOM items |
| check_native_bom | BOM items and native board text for reference/value/footprint parity |
| check_bom_sourcing | SourcingRecord and needed quantity; no live lookup |
| check_alternate | Evidence for seven compatibility criteria; no substitution |
| check_fpga_banks | Pin plan and device/package-specific bank rules |
| check_fpga_pin_plan | Pin plan and DeviceRules for dedicated, clock, differential and VREF pins |
| check_fpga_boot | BootPlan and DeviceRules for flash/interface/straps/pulls/header |
| check_decoupling | Rules, capacitors and known references |
| check_connector_protection | Interface protection rules, devices and known references |
| check_testpoint_coverage | Required signal/rail accessibility and declared test points |
| check_clock_topology | Cited ClockTree frequency, fanout, termination and domain expectations |
| check_audio_signal_chain | AudioChain loaded gain, full-scale limits and headroom |
| check_audio_noise | NoiseBudget with explicit bandwidth and independent-source assumption |
| check_opamp | Cited OpAmpEnvelope operating ranges and known stability constraints |
| check_manufacturability | Profile, measured features, layer count and board thickness |

Run the same bounded checks from a file with
`astra-pcb check check_bom examples/minimal-board/verifier-bom.json`.
This deliberately incomplete example fails for its missing MPN. CLI status is 0 for all
PASS, 2 for WARN/SKIP, and 1 for FAIL/ERROR. Empty reports are not successful.

## Capability boundary

Arguments are data, not file paths, executable names or code. Native board inspection
accepts text supplied by the trusted harness. There are no network, source-file write,
shell, upload, order or mutation operations. An input-schema citation may contain a URL
or path as evidence text; the verifier never opens it. Source content must be collected
and tied to an input digest by the trusted harness before a Reviewer receives it.
Reviewer live KiCad permissions remain empty; optional verifier results can be included
in its frozen review packet. This profile does not grant it the Designer transport.

Each call runs in a separate Python worker with a 15-second parent deadline, a 1 MiB
request limit and an 8 MiB accepted response limit. POSIX workers additionally have a
10-second CPU limit and 512 MiB address-space limit. Output is captured before its size
is checked, so the address-space limit also matters. Non-POSIX hosts need deployment
resource limits. This is a deliberately limited API, not an OS sandbox for arbitrary
agent code. A deployment should also use a read-only filesystem/container policy.

Rules operate on declared inputs. Missing evidence, unknown device rules and unmeasured
geometry do not become PASS. No tools are advertised for automatic electrical-pin-type
extraction, general footprint-to-datasheet matching, high-current path ampacity,
mounting-clearance extraction or electromagnetic return-path analysis. Those require
additional native data adapters and validated algorithms. STEP solid collision checking
is a separate optional local Python API; it does not add filesystem access to this MCP.

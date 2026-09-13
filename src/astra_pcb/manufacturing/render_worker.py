"""Private, bounded subprocess entry for Gerbonara; no GUI or server is started."""

import json
import sys
import warnings
from pathlib import Path


def main():
    from gerbonara import LayerStack
    from gerbonara.rs274x import GerberFile

    config = json.loads(Path(sys.argv[1]).read_text())
    with warnings.catch_warnings(record=True) as diagnostics:
        warnings.simplefilter("always")
        layers = {
            tuple(role.split()): GerberFile.open(path) for role, path in config["layers"].items()
        }
        stack = LayerStack(graphic_layers=layers)
        svg = str(stack.to_svg(margin=1, side_re=config["side_re"]))
        Path(config["output"]).write_text(svg)
    print(json.dumps({"warnings": [str(w.message) for w in diagnostics]}))


if __name__ == "__main__":
    main()

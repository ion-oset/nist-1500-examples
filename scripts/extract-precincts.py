"""Extract single-precinct EDFs from multi-precinct EDFs."""

# --- Display results

def _show_item(item, output = None):
    output = output or sys.stdout
    print(json.dumps(item, indent = 4), file = output)


# --- Main

import argparse
import json
import os
import sys
from pathlib import Path


# Contexts to show debugging output in
_SHOW = ( "document", )


def run(input_file, show, **opts):
    assert input_file.is_file(), f"Not a file: {input_file}"
    document = json.loads(input_file.read_text())
    if "document" in show:
        _show_item(document)


def main():
    parser = argparse.ArgumentParser(
        description = "Extract a valid single precinct EDF from a multi-precinct EDF.",
    )
    add = parser.add_argument
    add("input_file", type = Path,
        help = "EDF file to select precinct from")
    add("--show", choices = _SHOW, action = "append", default = [],
        help = "Contexts to show debugging output. Any of: " + ", ".join(_SHOW))
    opts = parser.parse_args()
    opts = vars(opts)
    run(**opts)


if __name__ == "__main__":
    main()

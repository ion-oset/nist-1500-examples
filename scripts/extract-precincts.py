"""Extract single-precinct EDFs from multi-precinct EDFs."""

from index import Index


# --- Display results

def _show_item(item, output = None):
    output = output or sys.stdout
    print(json.dumps(item, indent = 4), file = output)


def _show_index(document):
    index = Index(document, "ElectionResults")
    print()
    print("Index")
    print("-----\n")
    # Types of elements by their ID
    print("IDs (types):")
    # Strip namespace prefix off of printed type
    n = len(index._namespace) + 1
    for name, value in index._by_id.items():
        print(f"- {name}: {value['@type'][n:]}")
    print()
    # Counts of elements by their type
    print("Types (counts):")
    for name, values in index._by_type.items():
        print(f"- {name}: {len(values)}")


# --- Main

import argparse
import json
import os
import sys
from pathlib import Path


# Contexts to show debugging output in.
# Would be replaced with 'logging' in a non-example application.
_SHOW = ( "document", "index" )


def run(input_file, show, **opts):
    assert input_file.is_file(), f"Not a file: {input_file}"
    document = json.loads(input_file.read_text())
    if "document" in show:
        _show_item(document)
    if "index" in show:
        _show_index(document)


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

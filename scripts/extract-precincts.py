"""Extract single-precinct EDFs from multi-precinct EDFs."""

from electos.datamodels.nist.models.base import NistModel
from electos.datamodels.nist.models.edf import ElectionReport

from index import Index
from selection import PrecinctSelection
from extractor import PrecinctExtractor
from utility import json_save


# --- Display results

def _show_item(item, output = None):
    output = output or sys.stdout
    print(json.dumps(item, indent = 4, default = json_save), file = output)


def _show_index(document):
    index = Index(document, "ElectionResults")
    print()
    print("Index")
    print("-----\n")
    # Types of elements by their ID
    print("IDs (types):")
    # Strip namespace prefix off of printed type
    n = len(index._namespace) + 1
    for name, node in index._by_id.items():
        print(f"- {name}: {node.value.model__type[n:]}")
    print()
    # Counts of elements by their type
    print("Types (counts):")
    for name, nodes in index._by_type.items():
        print(f"- {name}: {len(nodes)}")


def _show_precinct_selection(document, precinct_id, election_id):
    print()
    print("Precinct IDs")
    print("------------\n")
    selection = PrecinctSelection(document, precinct_id, election_id)
    entries = [
        ( "GP Units", selection.gp_units, selection._document.gp_unit ),
        ( "Headers",  selection.headers,  selection._document.header ),
        ( "Contests", selection.contests, selection._election.contest ),
        ( "Candidates", selection.candidates, selection._election.candidate ),
        ( "Offices", selection.offices,   selection._document.office ),
        ( "Parties", selection.parties,   selection._document.party ),
        ( "Persons", selection.persons,   selection._document.person ),
    ]
    for (label1, some, all) in entries:
        print(f"{label1}:")
        sep = "  - "
        nsep = f"\n{sep}"
        other = [_ for _ in all if _ not in some]
        for label2, items in zip(("Precinct IDs", "Other IDs"), (some, other)):
            if len(items) == 0:
                print(f"  {label2}: none")
                continue
            print(f"  {label2}:")
            ids = [_.model__id for _ in items if _]
            print(sep, end = "")
            print(nsep.join(ids))
        print()


def _show_extracted_precinct(document, precinct_id, election_id):
    print()
    print("Extract Precinct")
    print("----------------")
    extractor = PrecinctExtractor()
    precinct_document = extractor.extract_precinct(document, precinct_id, election_id)
    _show_item(precinct_document)


# --- Main

import argparse
import json
import os
import sys
from pathlib import Path


# Contexts to show debugging output in.
# Would be replaced with 'logging' in a non-example application.
_SHOW = ( "document", "index", "selection", "extractor" )


def run(input_file, output_file, precinct_id, election_id, show, **opts):
    assert input_file.is_file(), f"Not a file: {input_file}"
    data = json.loads(input_file.read_text())
    document = ElectionReport(**data)
    if "document" in show:
        _show_item(document)
    if "index" in show:
        _show_index(document)
    if "selection" in show:
        _show_precinct_selection(document, precinct_id, election_id)
    if "extractor" in show:
        _show_extracted_precinct(document, precinct_id, election_id)
    if output_file:
        output_file = Path(output_file)
        assert output_file.parent.is_dir(), f"Not a directory: {output_file.parent}"
        with output_file.open("w") as output:
            runner = PrecinctExtractor()
            precinct_document = runner.extract_precinct(document, precinct_id, election_id)
            print(f"Saving results to {output_file}")
            _show_item(precinct_document, output)


# Notes:
# - Precinct IDs are not names. They are numeric indexes starting at 0.
#   The reason is that BallotStyles have no '@id'. This could be changed to also
#   allow the 'ExternalIdentifier' to be used, but BallotStyles are not required
#   to have one.
# - Election IDs are optional because there is usually only one election.
#   They are kept as numeric indexes for consistency with precinct IDs.

def main():
    parser = argparse.ArgumentParser(
        description = "Extract a valid single precinct EDF from a multi-precinct EDF.",
    )
    add = parser.add_argument
    add("input_file", type = Path,
        help = "EDF file to select precinct from")
    add("precinct_id", type = int,
        help = "ID (numeric index) of the BallotStyle of the precinct to extract")
    add("election_id", type = int, nargs = "?", default = 0,
        help = "ID (numeric index) of the Election to extract. (default: 0)")
    add("-o", "--output-file", type = None,
        help = "EDF file with selected precinct (default: standard output)")
    add("--show", choices = _SHOW, action = "append", default = [],
        help = "Contexts to show debugging output. Any of: " + ", ".join(_SHOW))
    opts = parser.parse_args()
    opts = vars(opts)
    run(**opts)


if __name__ == "__main__":
    main()

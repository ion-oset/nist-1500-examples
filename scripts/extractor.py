"""Precinct extraction."""

import copy

from index import Index
from selection import PrecinctSelection
from utility import ids_of


class PrecinctExtractor:

    """Extract a single precinct EDF from a combined EDF."""


    def extract_precinct(self, document, precinct_id, election_id = 0):
        """Extractor for precinct EDF records.

        Parameters:
            document: EDF document
            precinct_id: ID (numeric index) for root 'BallotStyle'.
            election_id: ID (numeric index) for 'Election'.
                default: 0. There is usually only one 'Election'.
        """
        # Make a copy so the original document isn't clobbered.
        document = copy.deepcopy(document)
        index = Index(document, "ElectionResults")
        selection = PrecinctSelection(document, precinct_id, election_id)
        # Ballot styles have no '@id', so 'ids_of' won't work.
        # Since there's only one ballot style for the precinct this doesn't matter.
        document["Election"][election_id]["BallotStyle"] = [selection.ballot_style]
        for name, ids in (
            ( "Contest", ids_of(selection.contests) ),
            ( "Candidate", ids_of(selection.candidates) ),
            ( "ReportingUnit", ids_of(selection.gp_units) ),
            ( "Header", ids_of(selection.headers) ),
            ( "Office", ids_of(selection.offices) ),
            ( "Party", ids_of(selection.parties) ),
            ( "Person", ids_of(selection.persons) ),
        ):
            self._remove_unreached_elements(index, name, ids)
        return document


    def _remove_unreached_elements(self, index, type_name, reachable_ids):
        """Remove elements that aren't part of the precinct.
        This means elements that aren't reachable from the root BallotStyle."""
        keys = []
        for node in index.by_type(type_name):
            item = node.value
            if item["@id"] not in reachable_ids:
                keys.append(node.key)
        # Delete from end to beginning so that indexes don't change if item
        # is a list. If node is a dict this is unnecessary but harmless.
        keys.reverse()
        for key in keys:
            del node.parent[key]

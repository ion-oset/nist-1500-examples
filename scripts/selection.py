from functools import cached_property, reduce

from electos.datamodels.nist.models.edf import OrderedContest, OrderedHeader


class PrecinctSelection:

    """Selection of all elements in an EDF that belong to a single precinct.

    Notes:

    - All properties are either from 'ElectionReport' or 'Election'.
    - The order of properties is the declaration order from document.
    - Most selections may be empty as nearly all the properties are optional.
      This is a result of the JSON Schema being unconstrained: EDFs can be pass
      schema validation and still not be possible.
    - Modifying the selection should NOT modify the property on the original
      document. (This is not currently being tested.)
    """

    def __init__(self, document, precinct_id, election_id = 0):
        """Construct a precinct selection from an EDF.

        Parameters:
            document: EDF document
            precinct_id: ID (numeric index) for root 'BallotStyle'.
            election_id: ID (numeric index) for 'Election'.
                default: 0. There is usually only one 'Election'.
        """
        self._document = document
        self._precinct_id = precinct_id
        self._election_id = election_id


    @cached_property
    def ballot_style(self):
        """The selected ballot style. Extracted from election report.

        This is the root of the extraction, so there is only one.
        """
        # If the ballot style is missing an error will be raised here.
        # TODO: A selection is not possible without a ballot style so this
        # check should come earlier.
        result = self._election.ballot_style[self._precinct_id]
        return result


    @cached_property
    def candidates(self):
        """Candidates in the precinct. Derived fron the candidate contests."""
        candidates = self._election.candidate
        if not candidates:
            results = []
        else:
            ids = [
                contest_selection.candidate_ids
                # Only look at candidate contests
                for contest in self.contests
                    if contest.model__type == "ElectionResults.CandidateContest"
                # Limit to selections with candidate IDs.
                # Write-ins are candidate contest selections and they *have* a
                # 'CandidateId' property but it is null.
                for contest_selection in contest.contest_selection
                    if getattr(contest_selection, "candidate_ids", None) != None
            ]
            ids = reduce(lambda x, y: x + y, ids, [])
            results = [
                candidate
                for candidate in candidates if candidate.model__id in ids
            ]
        return results


    @cached_property
    def contests(self):
        """Contests in the precinct. Derived from the ballot style."""
        contests = self._election.contest
        if not contests:
            return results
        else:
            ids = [
                contest_id
                for item in self.ballot_style.ordered_content
                for contest_id in self._walk_ordered_content(item)
            ]
            results = [
                contest
                for contest in contests if contest.model__id in ids
            ]
        return results


    @cached_property
    def gp_units(self):
        """Geo-political unit for the precinct. Extracted from election report."""
        gp_units = self._document.gp_unit
        if not gp_units:
            results = []
        else:
            ids = self.ballot_style.gp_unit_ids
            results = [
                gp_unit
                for gp_unit in gp_units if gp_unit.model__id in ids
            ]
            assert len(results) == 1, "More than one GpUnit for precinct"
        return results


    @cached_property
    def headers(self):
        """Ballot headers for the precinct. Extracted from the election report."""
        headers = self._document.header
        if not headers:
            results = []
        else:
            ids = [
                item.header_id
                for item in self.ballot_style.ordered_content
            ]
            results = [
                header
                for header in headers if header.model__id in ids
            ]
        return results


    @cached_property
    def offices(self):
        """Offices for the precinct. Derived from the candidate contests."""
        offices = self._document.office
        if not offices:
            results = []
        else:
            ids = [
                contest.office_ids
                # Only candidate contests have offices
                for contest in self.contests
                    if contest.model__type == "ElectionResults.CandidateContest"
            ]
            ids = reduce(lambda x, y: x + y, ids, [])
            results = [
                office
                for office in offices if office.model__id in ids
            ]
        return results


    @cached_property
    def parties(self):
        """Parties for the precinct. Derived from the candidates."""
        parties = self._document.party
        if not parties:
            results = []
        else:
            ids = [
                candidate.party_id
                # Not all candidates have a party
                for candidate in self.candidates
                    if hasattr(candidate, "party_id")
            ]
            results = [
                party
                for party in parties if party.model__id in ids
            ]
        return results


    @cached_property
    def persons(self):
        """Persons for the precinct. Derived from the candidates."""
        persons = self._document.person
        if not persons:
            results = []
        else:
            ids = [
                candidate.person_id
                for candidate in self.candidates
            ]
            results = [
                person
                # Note: Technically a Candidate can have 0 Persons.
                # It's not clear under what circumstances that can occur.
                for person in persons if person.model__id in ids
            ]
        return results


    # --- Properties: Internal

    @cached_property
    def _election(self):
        elections = self._document.election
        election = elections[self._election_id]
        return election


    # --- Methods: Internal

    def _walk_ordered_content(self, content):
        """Recursively walk 'OrderedContent' and find 'ContestId's.

        There is only one 'OrderedContest' per 'OrderedContent' but
        it may be nested under zero or more 'OrderedHeader's.

        Returns:
            List of 'ContestSelection' IDs.
        """
        if isinstance(content, OrderedContest):
            # return content.ordered_contest_selection_ids
            return [content.contest_id]
        elif isinstance(content, OrderedHeader):
            return self._ordered_content(content.ordered_content)
        else:
            assert False, f"Not an OrderedContent subtype: {type(content).__name__}"

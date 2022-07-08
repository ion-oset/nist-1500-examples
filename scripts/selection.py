from functools import cached_property, reduce


class PrecinctSelection:

    """Selection of all elements in an EDF that belong to a single precinct."""

    # Note: Order of properties is declaration order (i.e. being preserved).

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
                # Write-ins are candidate contest selections but have no IDs.
                for contest_selection in contest.contest_selection
                    if hasattr(contest_selection, "CandidateIds")
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
                item2.contest_id
                for item1 in self.ballot_style.ordered_content
                for item2 in item1.ordered_content
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
                    if hasattr(candidate, "PartyId")
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


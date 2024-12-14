class Ballot:
    total_ballots = 0

    def __init__(self, votes):
        self.id = Ballot.total_ballots
        Ballot.total_ballots += 1
        self.votes = votes

    def __repr__(self) -> str:
        return f"Ballot{self.id}[{self.votes}]"

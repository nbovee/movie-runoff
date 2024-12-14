import re
import argparse
from random import randint
from methods.method_factory import VotingMethodFactory
from domain.ballot import Ballot
from domain.file_utils import acquire_file, parse_file


class Election:
    def __init__(self, filepath, quiet, method="schulze", num_winners=1):
        self.file_contents = parse_file(filepath)
        self.movies, self.ballots = Ballot.load_from_file_contents(self.file_contents)
        self.quiet = quiet
        self.tie = False
        self.method = method
        self.num_winners = num_winners
        self.winners = []
        self.losers = []

    def calculate(self):
        voting_method = VotingMethodFactory.create_method(
            self.method, self.movies.copy(), self.ballots, num_winners=self.num_winners
        )
        self.winners, self.losers = voting_method.process_ballots()
        self.tie = voting_method.tie

        # Print results
        for i, winner in enumerate(self.winners):
            if isinstance(winner, list):
                print(f'Tie for {"Winner" if i == 0 else f"#{i+1}"}: {", ".join(winner)}*')
            else:
                print(f'{"Winner" if i == 0 else f"{f"#{i+1}":>6}"}: {winner}')
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Perform vote calculations for movie night"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="ignore all print statements except for final results",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--reorder_votes",
        help="after a movie is removed, reorder the ballot votes to the lowest possible numbers (i.e. [1,2,4,5,7] -> [1,2,3,4,5])",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--select",
        help="select a file instead of using the most recent expected filename",
        action="store_true",
    )
    parser.add_argument(
        "-m",
        "--method",
        help="voting method to use",
        choices=["instant", "instant-reorder", "schulze"],
        default="schulze",
    )
    parser.add_argument(
        "-n", "--num_winners", help="number of winners to select", type=int, default=1
    )
    args = parser.parse_args()

    filepath = acquire_file(args.select, "Runoff Votes", path="ballots/")

    method = args.method
    print(f"~~~~~ Using {method.title()} Method ~~~~~")
    election = Election(
        filepath, args.quiet, method=method, num_winners=args.num_winners
    )
    election.calculate()


if __name__ == "__main__":
    main()

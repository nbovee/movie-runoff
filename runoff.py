import re
import argparse
from random import randint
from methods.method_factory import VotingMethodFactory
from domain.ballot import Ballot
from domain.file_utils import acquire_file, parse_file


class Election:
    def __init__(self, filepath, quiet, method="schulze", num_winners=1):
        self.movies = []
        self.ballots = []
        self.file_contents = parse_file(filepath)
        self.load_ballots()
        self.quiet = quiet
        self.tie = False
        self.method = method
        self.num_winners = num_winners

    def load_ballots(self):
        self.movies = [
            re.search(r"\[(.+)\]", movie).group(1)
            for movie in self.file_contents[0][1:]
        ]
        for ballot in list(self.file_contents[1:]):
            self.ballots.append(
                Ballot([int(val) if val != "" else -1 for val in ballot[1:]])
            )

    def calculate(self):
        voting_method = VotingMethodFactory.create_method(
            self.method, self.movies.copy(), self.ballots, num_winners=self.num_winners
        )
        results = voting_method.calculate_winner()
        self.tie = voting_method.tie

        # TODO: Check tie handling
        if self.tie:
            print(f'Multiple winners tied: {", ".join(results)}')
            # Randomly select required number of winners
            winners = []
            remaining = results.copy()
            for i in range(min(self.num_winners, len(results))):
                winner = remaining.pop(randint(0, len(remaining) - 1))
                winners.append(winner)
                print(f'{"Winner" if i == 0 else f"#{i+1}"}: {winner}*')
            print()
        else:
            for i, winner in enumerate(results):
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
        help="voting method to use: instant, instant-reorder, or schulze",
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

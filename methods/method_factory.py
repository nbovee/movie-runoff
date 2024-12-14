from abc import ABC, abstractmethod


class VotingMethod(ABC):
    def __init__(self, movies, ballots, num_winners=1):
        self.movies = movies
        self.ballots = ballots
        self.tie = False
        self.num_winners = num_winners

    @abstractmethod
    def process_ballots(self):
        """Calculate and return winners and losers.
        Returns (winners, losers) where:
            - winners is a list of length num_winners, where each element is either:
                - a single winner, or
                - a list of candidates tied for that position
            - losers is a list of remaining candidates in order
        """
        pass


class VotingMethodFactory:
    @staticmethod
    def create_method(method_name, movies, ballots, num_winners=1):
        from methods.schulze import SchulzeMethod
        from methods.runoff import InstantRunoffMethod

        if method_name == "schulze":
            return SchulzeMethod(movies, ballots, num_winners=num_winners)
        elif method_name == "instant":
            return InstantRunoffMethod(
                movies, ballots, reorder=False, num_winners=num_winners
            )
        elif method_name == "instant-reorder":
            return InstantRunoffMethod(
                movies, ballots, reorder=True, num_winners=num_winners
            )
        else:
            raise ValueError(f"Unknown voting method: {method_name}")

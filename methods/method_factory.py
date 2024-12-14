from abc import ABC, abstractmethod


class VotingMethod(ABC):
    def __init__(self, movies, ballots, num_winners=1):
        self.movies = movies
        self.ballots = ballots
        self.tie = False
        self.num_winners = num_winners

    @abstractmethod
    def calculate_winner(self):
        """Calculate and return the winners.
        Returns a list of length num_winners, or more in case of ties."""
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

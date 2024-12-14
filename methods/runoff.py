import sys
from random import randint
from methods.method_factory import VotingMethod
from domain.ballot import Ballot


class InstantRunoffMethod(VotingMethod):
    def __init__(self, movies, ballots, reorder=False, num_winners=1):
        super().__init__(movies, ballots, num_winners)
        self.maxVote = len(movies)
        self.reorder = reorder
        self.movies = movies.copy()  # Create a copy to modify
        self.ballots = [
            Ballot(ballot.votes.copy()) for ballot in ballots
        ]  # Deep copy ballots
        self.eliminated = []  # Keep track of eliminated movies in order

    def count_votes_for_movie(self, vote_num, movie_index):
        return sum(
            1 for ballot in self.ballots if ballot.votes[movie_index] == vote_num
        )

    def get_next_highest_in_array(self, start, arr):
        next_highest = sys.maxsize
        for val in arr:
            if val < next_highest and val > start:
                next_highest = val
        return next_highest

    def shift_first_votes(self, movie_index):
        for ballot in self.ballots:
            if ballot.votes[movie_index] == 1:
                next_highest_vote = self.get_next_highest_in_array(1, ballot.votes)
                ind_to_swap = ballot.votes.index(next_highest_vote)
                ballot.votes[ind_to_swap] = 1
            ballot.votes.pop(movie_index)
        self.movies.pop(movie_index)

    def reorder_ballots(self):
        for ballot in self.ballots:
            ordered_votes = sorted(ballot.votes)
            for i, v in enumerate(ordered_votes):
                idx_to_swap = ballot.votes.index(v)
                ballot.votes[idx_to_swap] = i + 1

    def get_indices_with_lowest_vote_count(self, indices_to_check, vote_num):
        index_counts = {idx: 0 for idx in indices_to_check}
        for ind in indices_to_check:
            for ballot in self.ballots:
                if ballot.votes[ind] == vote_num:
                    index_counts[ind] += 1
        lowest = min(index_counts.values())
        return [key for key, val in index_counts.items() if val == lowest]

    def drop_movies_with_no_first_votes(self):
        s = 0
        e = len(self.movies)
        while s < e:
            if self.count_votes_for_movie(1, s) == 0:
                self.shift_first_votes(s)
                if self.reorder:
                    self.maxVote -= 1
                    self.reorder_ballots()
                e -= 1
            else:
                s += 1

    def process_ballots(self):
        self.drop_movies_with_no_first_votes()
        
        while len(self.movies) > self.num_winners:
            indices_to_check = list(range(len(self.movies)))
            for vote in range(1, self.maxVote + 1):
                indices_to_check = self.get_indices_with_lowest_vote_count(indices_to_check, vote)
                
                if len(indices_to_check) == 1:
                    eliminated = self.movies[indices_to_check[0]]
                    self.eliminated.insert(0, eliminated)  # Add to front of eliminated list
                    self.shift_first_votes(indices_to_check[0])
                    if self.reorder:
                        self.maxVote -= 1
                        self.reorder_ballots()
                    break
                
                if vote == self.maxVote:
                    self.tie = True
                    # All remaining candidates are tied for this position
                    tied_candidates = [self.movies[i] for i in indices_to_check]
                    # Add all but one randomly chosen candidate to eliminated list
                    rand_index = randint(0, len(indices_to_check) - 1)
                    for i, idx in enumerate(indices_to_check):
                        if i != rand_index:
                            self.eliminated.insert(0, self.movies[idx])
                    self.shift_first_votes(indices_to_check[rand_index])
                    if self.reorder:
                        self.maxVote -= 1
                        self.reorder_ballots()
        
        # If there's a tie for the last position, return it as a nested list
        if self.tie:
            winners = self.movies[:-1]  # All clear winners
            winners.append([self.movies[-1]] + self.eliminated[:len(indices_to_check)-1])  # Add tied candidates
            losers = self.eliminated[len(indices_to_check)-1:]  # Rest are losers
        else:
            winners = self.movies
            losers = self.eliminated
        
        return winners, losers

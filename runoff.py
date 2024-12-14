import re
import sys
import argparse
from random import randint
from gform_csvzip import acquire_file, parse_file

class Ballot:
    total_ballots = 0

    def __init__(self, votes):
        self.id = Ballot.total_ballots
        Ballot.total_ballots += 1
        self.votes = votes

    def __repr__(self) -> str:
        return f'Ballot{self.id}[{self.votes}]'
    
class SchulzeMethod:
    def __init__(self, movies, ballots):
        self.movies = movies
        self.ballots = ballots
        self.n = len(movies)
        self.d = [[0 for i in range(self.n)] for j in range(self.n)]
        self.p = [[0 for i in range(self.n)] for j in range(self.n)]
        
    def compute_d(self):
        # For each pair of candidates, count how many voters prefer i over j
        for ballot in self.ballots:
            for i in range(self.n):
                for j in range(self.n):
                    if i != j and ballot.votes[i] != -1 and ballot.votes[j] != -1:
                        if ballot.votes[i] < ballot.votes[j]:
                            self.d[i][j] += 1
    
    def compute_p(self):
        # Find strongest paths between each pair using Floyd-Warshall algorithm
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    if self.d[i][j] > self.d[j][i]:
                        self.p[i][j] = self.d[i][j]
                    else:
                        self.p[i][j] = 0

        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    for k in range(self.n):
                        if i != k and j != k:
                            self.p[j][k] = max(
                                self.p[j][k],
                                min(self.p[j][i], self.p[i][k])
                            )
    
    def get_winner(self):
        self.compute_d()
        self.compute_p()
        
        # Calculate strength of victory for each candidate
        strength_scores = []
        for i in range(self.n):
            wins = 0
            for j in range(self.n):
                if i != j and self.p[i][j] > self.p[j][i]:
                    wins += 1
            strength_scores.append((wins, i))
        
        # Sort by number of wins (highest to lowest)
        strength_scores.sort(reverse=True)
        
        # Get top two candidates
        top_score = strength_scores[0][0]
        second_score = strength_scores[1][0]
        
        # If there's a tie for first, return only those tied for first
        if top_score == second_score:
            tied_winners = [self.movies[i] for wins, i in strength_scores if wins == top_score]
            return tied_winners
        else:
            # Return winner and runner up
            winner = self.movies[strength_scores[0][1]]
            runner_up = self.movies[strength_scores[1][1]]
            return [winner, runner_up]

class Runoff:
    def __init__(self, filepath, quiet, method='schulze'):
        self.lowest = 0
        self.movies = []
        self.ballots = []
        self.file_contents = parse_file(filepath)
        self.load_ballots()
        self.maxVote = len(self.movies)
        self.quiet = quiet
        self.tie = False
        self.method = method
    
    def load_ballots(self):
        self.movies = [re.search(r'\[(.+)\]', movie).group(1) for movie in self.file_contents[0][1:]]
        for ballot in list(self.file_contents[1:]):
            self.ballots.append(Ballot([int(val) if val != '' else -1 for val in ballot[1:]]))
    
    def count_num_votes_for_movie(self,voteNum,movieIndex):
        return sum([1 for ballot in self.ballots if ballot.votes[movieIndex] == voteNum])

    def drop_movies_with_no_first_votes(self,reorder):
        s = 0
        e = len(self.movies)
        while(s < e):
            if self.count_num_votes_for_movie(1,s) == 0:
                if not self.quiet:
                    print(f'{self.movies[s]} dropped.')
                self.shift_first_votes(s)
                if reorder:
                    self.maxVote -= 1
                    self.reorder_ballots()
                e -= 1
            else:
                s += 1
    
    def shift_first_votes(self,movieIndex):
        for ballot in self.ballots:
            if ballot.votes[movieIndex] == 1:
                nextHighestVote = get_next_highest_in_array(1,ballot.votes)
                indToSwap = ballot.votes.index(nextHighestVote)
                ballot.votes[indToSwap] = 1
            ballot.votes.pop(movieIndex)
        self.movies.pop(movieIndex)
    
    def get_movie_indices_with_lowest_count_of_vote(self,indicesToCheck,voteNum):
        indexCounts = {idx:0 for idx in indicesToCheck}
        for ind in indicesToCheck:
            for ballot in self.ballots:
                if ballot.votes[ind] == voteNum:
                    indexCounts[ind] += 1
        lowest = min(indexCounts.values())
        return [key for key,val in indexCounts.items() if val == lowest]
    
    def print_movies(self):
        print([movie for movie in self.movies])
    
    def print_ballots(self):
        for ballot in self.ballots:
            print(ballot.votes)
    
    def reorder_ballots(self):
        for ballot in self.ballots:
            orderedVotes = sorted(ballot.votes)
            for i,v in enumerate(orderedVotes):
                idxToSwap = ballot.votes.index(v)
                ballot.votes[idxToSwap] = i + 1

    
    def runoff(self,reorder):
        if not self.quiet:
            self.print_movies()
            self.print_ballots()
            print('Dropping movies with no 1 votes')
        self.drop_movies_with_no_first_votes(reorder)
        while(len(self.movies) > 1):
            if not self.quiet:
                print()
                self.print_movies()
                self.print_ballots()
            indicesToCheck = list(range(len(self.movies)))
            for vote in range(1,self.maxVote+1):
                indicesToCheck = self.get_movie_indices_with_lowest_count_of_vote(indicesToCheck,vote)
                if len(indicesToCheck) == 1:
                    if not self.quiet:
                        print(f'Dropping {self.movies[indicesToCheck[0]]}; least {vote} votes')
                    self.shift_first_votes(indicesToCheck[0])
                    if reorder:
                        self.maxVote -= 1
                        self.reorder_ballots()
                    break
                else:
                    if not self.quiet:
                        print(f'Tie for least {vote} votes; {", ".join([self.movies[idx] for idx in indicesToCheck])}')
                if vote == self.maxVote:
                    self.tie = True
                    if not self.quiet:
                        print(f'Full ballot tie; {", ".join([self.movies[idx] for idx in indicesToCheck])}')
                    randIndex = randint(0,len(indicesToCheck)-1)
                    if not self.quiet:
                        print(f'{self.movies[indicesToCheck[randIndex]]} has been randomly chosen to drop')
                    self.shift_first_votes(indicesToCheck[randIndex])
                    if reorder:
                        self.maxVote -= 1
                        self.reorder_ballots()
        print(f'Winner is: {self.movies[0]}{"*" if self.tie else ""}\n')

    def calculate(self):
        if self.method == 'instant':
            self.runoff(False)
        elif self.method == 'instant-reorder':
            self.runoff(True)
        elif self.method == 'schulze':
            schulze = SchulzeMethod(self.movies.copy(), self.ballots)
            results = schulze.get_winner()
            
            if len(results) > 2:  # Tie between more than 2 movies
                self.tie = True
                print(f'Multiple winners tied: {", ".join(results)}')
                winner = results[randint(0, len(results)-1)]
                remaining = [r for r in results if r != winner]
                runner_up = remaining[randint(0, len(remaining)-1)]
                print(f'Randomly selected winner: {winner}*')
                print(f'Randomly selected runner up: {runner_up}*\n')
            elif len(results) == 2:  # Clear winner and runner up
                print(f'Winner is: {results[0]}')
                print(f'Runner up: {results[1]}\n')
            else:  # Should never happen, but just in case
                print(f'Winner is: {results[0]}\n')


def main():
    parser = argparse.ArgumentParser(description='Perform vote calculations for movie night')
    parser.add_argument('-q','--quiet',help='ignore all print statements except the one for the winner',action='store_true')
    parser.add_argument('-r','--reorder_votes',help='after a movie is removed, reorder the ballot votes to the lowest possible numbers (i.e. [1,2,4,5,7] -> [1,2,3,4,5])',action='store_true')
    parser.add_argument('-s','--select',help='select a file instead of using the most recent expected filename',action='store_true')
    parser.add_argument('-m','--method',help='voting method to use: instant, instant-reorder, or schulze',
                        choices=['instant', 'instant-reorder', 'schulze'],
                        default='schulze')
    args = parser.parse_args()

    filepath = acquire_file(args.select, 'Runoff Votes', path='ballots/')
    
    # method = 'instant-reorder' if args.reorder_votes else args.method
    method = args.method
    print(f'~~~~~ Using {method} Method ~~~~~')
    runoff = Runoff(filepath, args.quiet, method=method)
    runoff.calculate()

def get_next_highest_in_array(start,arr):
    nextHighest = sys.maxsize
    for val in arr:
        if val < nextHighest and val > start:
            nextHighest = val
    return nextHighest

if __name__ == "__main__":
    main()
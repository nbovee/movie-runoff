from methods.method_factory import VotingMethod

class SchulzeMethod(VotingMethod):
    def __init__(self, movies, ballots, num_winners=1):
        super().__init__(movies, ballots, num_winners)
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
    
    def calculate_winner(self):
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
        
        
        # TODO: Handle ties
        # Return requested number of winners
        return [self.movies[strength_scores[i][1]] for i in range(min(self.num_winners, len(strength_scores)))]

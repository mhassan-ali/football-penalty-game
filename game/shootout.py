from typing import List, Optional

class Shootout:
    def __init__(self, max_rounds: int = 5) -> None:
        self.max_rounds = max_rounds
        self.player_score = 0
        self.opponent_score = 0
        self.player_kicks: List[str] = []      # list of "goal", "save", "miss"
        self.opponent_kicks: List[str] = []    # list of "goal", "save", "miss"
        self.current_round = 0                 # 0-indexed round number (0 to 4)
        self.current_turn = "player"           # "player" (shoots) or "opponent" (AI shoots / player keeps)
        self.is_over = False
        self.winner: Optional[str] = None      # "player" or "opponent"
        self.sudden_death = False

    def record_outcome(self, outcome: str) -> None:
        """Records the outcome of the current turn and updates score, turns, and rounds."""
        is_goal = (outcome == "GOAL")
        
        if self.current_turn == "player":
            self.player_kicks.append(outcome.lower())
            if is_goal:
                self.player_score += 1
            # Next turn is the opponent's attempt
            self.current_turn = "opponent"
        else:
            self.opponent_kicks.append(outcome.lower())
            if is_goal:
                self.opponent_score += 1
            # Round completes after the opponent shoots
            self.current_round += 1
            self.current_turn = "player"

        self.check_match_status()

    def check_match_status(self) -> None:
        """Evaluates whether either team has won, or if sudden death starts."""
        p_kicks = len(self.player_kicks)
        o_kicks = len(self.opponent_kicks)

        if not self.sudden_death:
            # Normal 5-round shootout rules
            p_rem = self.max_rounds - p_kicks
            o_rem = self.max_rounds - o_kicks

            # Can opponent catch up?
            if self.player_score + p_rem < self.opponent_score:
                self.is_over = True
                self.winner = "opponent"
                return
            # Can player catch up?
            if self.opponent_score + o_rem < self.player_score:
                self.is_over = True
                self.winner = "player"
                return

            # Both teams took all 5 kicks
            if p_kicks == self.max_rounds and o_kicks == self.max_rounds:
                if self.player_score == self.opponent_score:
                    self.sudden_death = True
                else:
                    self.is_over = True
                    self.winner = "player" if self.player_score > self.opponent_score else "opponent"
        else:
            # Sudden Death: kicks are evaluated round-by-round (when counts match)
            if p_kicks == o_kicks:
                p_last = self.player_kicks[-1]
                o_last = self.opponent_kicks[-1]
                
                p_scored = (p_last == "goal")
                o_scored = (o_last == "goal")

                if p_scored != o_scored:
                    self.is_over = True
                    self.winner = "player" if p_scored else "opponent"

    def reset(self) -> None:
        self.player_score = 0
        self.opponent_score = 0
        self.player_kicks = []
        self.opponent_kicks = []
        self.current_round = 0
        self.current_turn = "player"
        self.is_over = False
        self.winner = None
        self.sudden_death = False

from typing import List

class Career:
    def __init__(self, team: str = "BRAZIL", max_matches: int = 10) -> None:
        self.team = team
        self.max_matches = max_matches
        self.current_match_idx = 1  # 1-indexed (1 to 10)
        self.wins = 0
        self.losses = 0
        self.points = 0
        self.history: List[str] = []  # List of "win" or "loss"

    def record_match(self, player_won: bool) -> None:
        """Saves player result, adds league points (3 points on win), and advances index."""
        if player_won:
            self.wins += 1
            self.points += 3
            self.history.append("win")
        else:
            self.losses += 1
            self.history.append("loss")
            
        self.current_match_idx += 1

    def is_finished(self) -> bool:
        return self.current_match_idx > self.max_matches

    def reset(self) -> None:
        self.current_match_idx = 1
        self.wins = 0
        self.losses = 0
        self.points = 0
        self.history = []

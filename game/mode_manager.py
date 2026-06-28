from typing import Optional
from game.tournament import Tournament
from game.career import Career

class GameModeManager:
    def __init__(self) -> None:
        self.active_mode = "practice"  # "practice", "tournament", "career"
        self.tournament: Optional[Tournament] = None
        self.career: Optional[Career] = None

    def start_practice(self) -> None:
        self.active_mode = "practice"
        self.tournament = None
        self.career = None

    def start_tournament(self, player_team: str) -> None:
        self.active_mode = "tournament"
        self.tournament = Tournament(player_team)
        self.career = None

    def start_career(self, player_team: str) -> None:
        self.active_mode = "career"
        self.career = Career(player_team)
        self.tournament = None

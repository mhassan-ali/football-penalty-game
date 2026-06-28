import random
from typing import List, Dict, Tuple

class Tournament:
    def __init__(self, player_team: str = "BRAZIL") -> None:
        self.player_team = player_team
        self.teams = ["BRAZIL", "ARGENTINA", "GERMANY", "FRANCE", "ENGLAND", "SPAIN", "ITALY", "PORTUGAL"]
        if player_team not in self.teams:
            # Replace a random team in the roster with the player's choice
            self.teams[random.randint(0, len(self.teams) - 1)] = player_team
            
        self.stages = ["Quarter Final", "Semi Final", "Final"]
        self.current_stage_idx = 0  # 0: QF, 1: SF, 2: Final, 3: Complete (Winner)
        self.eliminated = False
        self.winner = None

        # Bracket definitions
        self.bracket: Dict[str, List[Tuple[str, str]]] = {
            "Quarter Final": [],
            "Semi Final": [],
            "Final": []
        }
        self.results: Dict[str, List[str]] = {
            "Quarter Final": [],
            "Semi Final": [],
            "Final": []
        }
        self._generate_initial_bracket()

    def _generate_initial_bracket(self) -> None:
        """Shuffles roster teams and assigns them to 4 initial match brackets."""
        teams = list(self.teams)
        random.shuffle(teams)
        for i in range(0, 8, 2):
            self.bracket["Quarter Final"].append((teams[i], teams[i+1]))

    def get_player_match(self) -> Tuple[str, str]:
        """Returns the team matchup pair for the player's active stage."""
        stage = self.stages[self.current_stage_idx]
        for t1, t2 in self.bracket[stage]:
            if t1 == self.player_team or t2 == self.player_team:
                return (t1, t2)
        raise ValueError("Player team not found in the current bracket stage!")

    def advance_stage(self, player_won: bool) -> None:
        """Simulates all other bracket matches and builds the next rounds match list."""
        stage = self.stages[self.current_stage_idx]
        
        if not player_won:
            self.eliminated = True
            # Simulate remaining games
            for t1, t2 in self.bracket[stage]:
                if t1 != self.player_team and t2 != self.player_team:
                    self.results[stage].append(random.choice([t1, t2]))
                else:
                    opp = t2 if t1 == self.player_team else t1
                    self.results[stage].append(opp)
            return

        # Player won: simulate other matches
        stage_winners = []
        for t1, t2 in self.bracket[stage]:
            if t1 == self.player_team or t2 == self.player_team:
                stage_winners.append(self.player_team)
            else:
                stage_winners.append(random.choice([t1, t2]))
        
        self.results[stage] = stage_winners

        # Form next matchups
        if stage == "Quarter Final":
            self.bracket["Semi Final"] = [
                (stage_winners[0], stage_winners[1]),
                (stage_winners[2], stage_winners[3])
            ]
            self.current_stage_idx = 1
        elif stage == "Semi Final":
            self.bracket["Final"] = [
                (stage_winners[0], stage_winners[1])
            ]
            self.current_stage_idx = 2
        elif stage == "Final":
            self.winner = self.player_team
            self.current_stage_idx = 3

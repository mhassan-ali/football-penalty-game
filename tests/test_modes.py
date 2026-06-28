import unittest
import pygame
from core.event_manager import EventManager
from core.state_manager import StateManager, State
from core.scene_manager import SceneManager
from managers.asset_manager import AssetManager

from game.mode_manager import GameModeManager
from game.tournament import Tournament
from game.career import Career

from scenes.mode_select import ModeSelectScene
from scenes.team_select import TeamSelectScene
from scenes.difficulty_select import DifficultySelectScene
from scenes.tournament_bracket import TournamentBracketScene
from scenes.career_hub import CareerHubScene
from scenes.championship import ChampionshipScene
from scenes.results import ResultsScene
from scenes.loading import LoadingScene
from scenes.gameplay import GameplayScene

class TestGameModes(unittest.TestCase):
    def test_tournament_bracket_progression(self):
        t = Tournament("BRAZIL")
        self.assertEqual(len(t.teams), 8)
        self.assertIn("BRAZIL", t.teams)
        self.assertEqual(t.current_stage_idx, 0) # QF
        self.assertFalse(t.eliminated)

        # Player wins Quarter Final
        t1, t2 = t.get_player_match()
        self.assertTrue(t1 == "BRAZIL" or t2 == "BRAZIL")
        t.advance_stage(player_won=True)
        self.assertEqual(t.current_stage_idx, 1) # SF
        self.assertFalse(t.eliminated)

        # Player wins Semi Final
        t.advance_stage(player_won=True)
        self.assertEqual(t.current_stage_idx, 2) # Final
        self.assertFalse(t.eliminated)

        # Player wins Final
        t.advance_stage(player_won=True)
        self.assertEqual(t.current_stage_idx, 3) # Complete
        self.assertEqual(t.winner, "BRAZIL")

    def test_tournament_elimination(self):
        t = Tournament("BRAZIL")
        # Player loses Quarter Final
        t.advance_stage(player_won=False)
        self.assertTrue(t.eliminated)
        self.assertEqual(t.current_stage_idx, 0) # Stays QF but marked eliminated

    def test_career_progression(self):
        c = Career("ENGLAND", max_matches=5)
        self.assertEqual(c.team, "ENGLAND")
        self.assertEqual(c.current_match_idx, 1)
        self.assertEqual(c.wins, 0)
        self.assertEqual(c.points, 0)

        # Record Win
        c.record_match(player_won=True)
        self.assertEqual(c.current_match_idx, 2)
        self.assertEqual(c.wins, 1)
        self.assertEqual(c.points, 3)
        self.assertEqual(c.history[-1], "win")

        # Record Loss
        c.record_match(player_won=False)
        self.assertEqual(c.current_match_idx, 3)
        self.assertEqual(c.losses, 1)
        self.assertEqual(c.points, 3)
        self.assertEqual(c.history[-1], "loss")

        # Record remaining matches
        c.record_match(player_won=True)
        c.record_match(player_won=True)
        c.record_match(player_won=False)
        self.assertTrue(c.is_finished())


class TestGameModesSceneIntegration(unittest.TestCase):
    def setUp(self) -> None:
        pygame.init()
        self.event_manager = EventManager()
        self.state_manager = StateManager(self.event_manager, State.LOADING)
        self.scene_manager = SceneManager()
        self.mode_manager = GameModeManager()
        self.scene_manager.mode_manager = self.mode_manager
        self.asset_manager = AssetManager()

        self.scenes = {
            "mode_select": ModeSelectScene("mode_select", self.state_manager, self.scene_manager, self.asset_manager),
            "team_select": TeamSelectScene("team_select", self.state_manager, self.scene_manager, self.asset_manager),
            "difficulty_select": DifficultySelectScene("difficulty_select", self.state_manager, self.scene_manager, self.asset_manager),
            "tournament_bracket": TournamentBracketScene("tournament_bracket", self.state_manager, self.scene_manager, self.asset_manager),
            "career_hub": CareerHubScene("career_hub", self.state_manager, self.scene_manager, self.asset_manager),
            "results": ResultsScene("results", self.state_manager, self.scene_manager, self.asset_manager)
        }
        for name, sc in self.scenes.items():
            self.scene_manager.register_scene(name, sc)

    def test_tournament_selection_routing(self):
        # 1. Mode Select -> Select Tournament
        self.scene_manager.switch_scene("mode_select")
        self.scenes["mode_select"].selected_index = 1  # Tournament Mode
        self.scenes["mode_select"]._select_option()
        self.assertEqual(self.mode_manager.active_mode, "tournament")
        self.assertEqual(self.scene_manager.active_scene.name, "team_select")

        # 2. Team Select -> Confirm Team
        self.scenes["team_select"].selected_index = 2  # GERMANY
        self.scenes["team_select"]._confirm_team()
        self.assertEqual(self.scene_manager.active_scene.name, "difficulty_select")
        self.assertEqual(self.scenes["difficulty_select"].selected_team, "GERMANY")

        # 3. Difficulty Select -> Confirm Difficulty -> Tournament Bracket
        self.scenes["difficulty_select"].selected_index = 1 # Medium
        self.scenes["difficulty_select"]._confirm_difficulty()
        self.assertEqual(self.scene_manager.active_scene.name, "tournament_bracket")
        self.assertIsNotNone(self.mode_manager.tournament)
        self.assertEqual(self.mode_manager.tournament.player_team, "GERMANY")

    def test_results_routing_tournament_win(self):
        self.mode_manager.start_tournament("BRAZIL")
        
        # Win Quarter Final
        self.scene_manager.switch_scene("results", winner="player", selected_team="BRAZIL", difficulty="medium")
        self.assertEqual(self.mode_manager.tournament.current_stage_idx, 1) # Advanced to Semi Final
        
        # Click Continue
        self.scenes["results"].selected_index = 1  # CONTINUE option
        self.scenes["results"]._select_option()
        self.assertEqual(self.scene_manager.active_scene.name, "tournament_bracket")

    def test_results_retry_rollback_career(self):
        self.mode_manager.start_career("BRAZIL")
        self.assertEqual(self.mode_manager.career.current_match_idx, 1)

        # Play match 1 and win
        self.scene_manager.switch_scene("results", winner="player", selected_team="BRAZIL", difficulty="medium")
        self.assertEqual(self.mode_manager.career.current_match_idx, 2)
        self.assertEqual(self.mode_manager.career.wins, 1)

        # Press RETRY (option 0) -> rolls back career result and goes to loading
        self.scenes["results"].selected_index = 0
        # Register loading stub to verify transition
        self.scene_manager.register_scene("loading", LoadingScene("loading", self.state_manager, self.scene_manager, self.asset_manager))
        self.scenes["results"]._select_option()
        
        # Assert rolled back
        self.assertEqual(self.mode_manager.career.current_match_idx, 1)
        self.assertEqual(self.mode_manager.career.wins, 0)
        self.assertEqual(self.scene_manager.active_scene.name, "loading")

import unittest
import pygame
from core.event_manager import EventManager
from core.state_manager import StateManager, State
from core.scene_manager import SceneManager
from managers.asset_manager import AssetManager

from scenes.splash import SplashScene
from scenes.menu import MenuScene
from scenes.mode_select import ModeSelectScene
from scenes.team_select import TeamSelectScene
from scenes.difficulty_select import DifficultySelectScene
from scenes.loading import LoadingScene
from scenes.gameplay import GameplayScene
from scenes.pause import PauseScene
from scenes.results import ResultsScene
from scenes.settings import SettingsScene
from scenes.credits import CreditsScene
from scenes.exit_confirm import ExitConfirmScene
from scenes.tournament_bracket import TournamentBracketScene
from scenes.career_hub import CareerHubScene
from scenes.championship import ChampionshipScene

class TestNavigationFlow(unittest.TestCase):
    def setUp(self) -> None:
        pygame.init()
        self.event_manager = EventManager()
        self.state_manager = StateManager(self.event_manager, State.LOADING)
        self.scene_manager = SceneManager()
        from game.mode_manager import GameModeManager
        self.mode_manager = GameModeManager()
        self.scene_manager.mode_manager = self.mode_manager
        self.asset_manager = AssetManager()

        self.scenes = {
            "splash": SplashScene("splash", self.state_manager, self.scene_manager, self.asset_manager),
            "menu": MenuScene("menu", self.state_manager, self.scene_manager, self.asset_manager),
            "mode_select": ModeSelectScene("mode_select", self.state_manager, self.scene_manager, self.asset_manager),
            "team_select": TeamSelectScene("team_select", self.state_manager, self.scene_manager, self.asset_manager),
            "difficulty_select": DifficultySelectScene("difficulty_select", self.state_manager, self.scene_manager, self.asset_manager),
            "loading": LoadingScene("loading", self.state_manager, self.scene_manager, self.asset_manager),
            "gameplay": GameplayScene("gameplay", self.state_manager, self.scene_manager, self.asset_manager),
            "pause": PauseScene("pause", self.state_manager, self.scene_manager, self.asset_manager),
            "results": ResultsScene("results", self.state_manager, self.scene_manager, self.asset_manager),
            "settings": SettingsScene("settings", self.state_manager, self.scene_manager, self.asset_manager),
            "credits": CreditsScene("credits", self.state_manager, self.scene_manager, self.asset_manager),
            "exit_confirm": ExitConfirmScene("exit_confirm", self.state_manager, self.scene_manager, self.asset_manager),
            "tournament_bracket": TournamentBracketScene("tournament_bracket", self.state_manager, self.scene_manager, self.asset_manager),
            "career_hub": CareerHubScene("career_hub", self.state_manager, self.scene_manager, self.asset_manager),
            "championship": ChampionshipScene("championship", self.state_manager, self.scene_manager, self.asset_manager)
        }
        for name, sc in self.scenes.items():
            self.scene_manager.register_scene(name, sc)

    def test_full_navigation_path(self):
        # 1. Start at Splash
        self.scene_manager.switch_scene("splash")
        self.assertEqual(self.scene_manager.active_scene.name, "splash")

        # 2. Skip to Menu
        self.scenes["splash"]._skip()
        self.assertEqual(self.scene_manager.active_scene.name, "menu")
        self.assertEqual(self.state_manager.current_state, State.MAIN_MENU)

        # 3. Select Play Game -> Mode Select
        self.scenes["menu"]._select_option()
        self.assertEqual(self.scene_manager.active_scene.name, "mode_select")

        # 4. Mode Select -> Team Select
        self.scenes["mode_select"]._select_option()
        self.assertEqual(self.scene_manager.active_scene.name, "team_select")

        # 5. Team Select -> Difficulty Select
        self.scenes["team_select"]._confirm_team()
        self.assertEqual(self.scene_manager.active_scene.name, "difficulty_select")
        self.assertEqual(self.scenes["difficulty_select"].selected_team, "BRAZIL")

        # 6. Difficulty Select -> Loading
        self.scenes["difficulty_select"]._confirm_difficulty()
        self.assertEqual(self.scene_manager.active_scene.name, "loading")
        self.assertEqual(self.state_manager.current_state, State.MAIN_MENU)

        # 7. Loading -> Gameplay
        self.scenes["loading"].update(1.5)
        self.assertEqual(self.scene_manager.active_scene.name, "gameplay")
        self.assertEqual(self.state_manager.current_state, State.GAMEPLAY)

    def test_settings_origin_return(self):
        # From Menu -> Settings -> Back
        self.scene_manager.switch_scene("menu")
        self.scene_manager.switch_scene("settings", origin_scene="menu")
        self.assertEqual(self.scene_manager.active_scene.name, "settings")
        self.scenes["settings"]._go_back()
        self.assertEqual(self.scene_manager.active_scene.name, "menu")

        # From Pause -> Settings -> Back
        self.state_manager.change_state(State.GAMEPLAY)
        self.scene_manager.switch_scene("pause")
        self.scene_manager.switch_scene("settings", origin_scene="pause")
        self.assertEqual(self.scene_manager.active_scene.name, "settings")
        self.scenes["settings"]._go_back()
        self.assertEqual(self.scene_manager.active_scene.name, "pause")

    def test_results_saving_transition(self):
        self.state_manager.change_state(State.GAMEPLAY)
        self.scene_manager.switch_scene("results", winner="player")
        self.assertEqual(self.state_manager.current_state, State.RESULT)

        # Go to menu from results transitions through SAVING -> MAIN_MENU
        self.scenes["results"]._go_to_menu()
        self.assertEqual(self.state_manager.current_state, State.MAIN_MENU)
        self.assertEqual(self.scene_manager.active_scene.name, "menu")

    def test_exit_confirm_cancel_routing(self):
        # 1. From Tournament Bracket -> Exit Confirm -> Cancel (returns to Tournament Bracket)
        self.scene_manager.switch_scene("tournament_bracket")
        self.scenes["tournament_bracket"].selected_index = 1 # Abandon
        self.scenes["tournament_bracket"]._select_option()
        self.assertEqual(self.scene_manager.active_scene.name, "exit_confirm")
        
        # Select NO (cancel)
        self.scenes["exit_confirm"].selected_index = 1
        self.scenes["exit_confirm"]._confirm()
        self.assertEqual(self.scene_manager.active_scene.name, "tournament_bracket")

        # 2. From Pause -> Exit Confirm -> Cancel (returns to Pause)
        self.state_manager.change_state(State.GAMEPLAY)
        self.scene_manager.switch_scene("pause")
        self.scenes["pause"].selected_index = 3 # Return to main menu
        self.scenes["pause"]._select_option()
        self.assertEqual(self.scene_manager.active_scene.name, "exit_confirm")
        
        # Select NO (cancel)
        self.scenes["exit_confirm"].selected_index = 1
        self.scenes["exit_confirm"]._confirm()
        self.assertEqual(self.scene_manager.active_scene.name, "pause")

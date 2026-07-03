import unittest
import os
import json
import shutil
from managers.save_manager import SaveManager
from managers.config_manager import ConfigManager
from game.tournament import Tournament
from game.career import Career

class TestSaveSystem(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = "tests/temp_save_test"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        self.save_path = os.path.join(self.test_dir, "savegame.json")
        self.config_path = os.path.join(self.test_dir, "settings.json")
        
        # Create a basic settings file for config manager
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump({
                "audio": {
                    "master_volume": 0.5,
                    "music_volume": 0.4,
                    "sfx_volume": 0.3
                }
            }, f)
        
        self.config_manager = ConfigManager(self.config_path)

    def tearDown(self) -> None:
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_default_initialization(self):
        # Without config manager
        sm = SaveManager(self.save_path)
        self.assertEqual(sm.data["settings"]["master_volume"], 1.0)
        self.assertEqual(sm.data["statistics"]["matches_played"], 0)
        self.assertFalse(sm.data["achievements"]["first_kick"]["earned"])

        # With config manager
        sm2 = SaveManager(self.save_path, self.config_manager)
        self.assertEqual(sm2.data["settings"]["master_volume"], 0.5)
        self.assertEqual(sm2.data["settings"]["music_volume"], 0.4)
        self.assertEqual(sm2.data["settings"]["sfx_volume"], 0.3)

    def test_save_and_load(self):
        sm = SaveManager(self.save_path, self.config_manager)
        sm.data["statistics"]["matches_played"] = 5
        sm.data["statistics"]["goals_scored"] = 12
        sm.data["achievements"]["first_kick"]["earned"] = True
        sm.data["achievements"]["first_kick"]["earned_date"] = "2026-07-04"
        
        save_ok = sm.save_game()
        self.assertTrue(save_ok)
        self.assertTrue(os.path.exists(self.save_path))

        # Load into another instance
        sm_loaded = SaveManager(self.save_path, self.config_manager)
        self.assertEqual(sm_loaded.data["statistics"]["matches_played"], 5)
        self.assertEqual(sm_loaded.data["statistics"]["goals_scored"], 12)
        self.assertTrue(sm_loaded.data["achievements"]["first_kick"]["earned"])
        self.assertEqual(sm_loaded.data["achievements"]["first_kick"]["earned_date"], "2026-07-04")

    def test_reset_save(self):
        sm = SaveManager(self.save_path, self.config_manager)
        sm.data["statistics"]["matches_played"] = 10
        sm.data["achievements"]["first_kick"]["earned"] = True
        sm.save_game()

        sm.reset_save()
        self.assertEqual(sm.data["statistics"]["matches_played"], 0)
        self.assertFalse(sm.data["achievements"]["first_kick"]["earned"])
        # Settings should be preserved
        self.assertEqual(sm.data["settings"]["master_volume"], 0.5)

    def test_corrupted_save_handling(self):
        # Write random non-JSON bytes to save path
        with open(self.save_path, "w", encoding="utf-8") as f:
            f.write("corrupted data not json {[[[")

        sm = SaveManager(self.save_path, self.config_manager)
        # Should gracefully revert to defaults without crashing
        self.assertEqual(sm.data["statistics"]["matches_played"], 0)
        self.assertEqual(sm.data["settings"]["master_volume"], 0.5)

    def test_tournament_serialization(self):
        sm = SaveManager(self.save_path, self.config_manager)
        t = Tournament("GERMANY")
        t.current_stage_idx = 1
        t.results["Quarter Final"] = ["GERMANY", "BRAZIL"]

        sm.save_tournament(t)

        sm_loaded = SaveManager(self.save_path, self.config_manager)
        t_restored = sm_loaded.load_tournament(Tournament)
        self.assertIsNotNone(t_restored)
        self.assertEqual(t_restored.player_team, "GERMANY")
        self.assertEqual(t_restored.current_stage_idx, 1)
        self.assertEqual(t_restored.results["Quarter Final"], ["GERMANY", "BRAZIL"])

    def test_career_serialization(self):
        sm = SaveManager(self.save_path, self.config_manager)
        c = Career("ITALY")
        c.current_match_idx = 4
        c.wins = 2
        c.losses = 1
        c.points = 6
        c.history = ["win", "loss", "win"]

        sm.save_career(c)

        sm_loaded = SaveManager(self.save_path, self.config_manager)
        c_restored = sm_loaded.load_career(Career)
        self.assertIsNotNone(c_restored)
        self.assertEqual(c_restored.team, "ITALY")
        self.assertEqual(c_restored.current_match_idx, 4)
        self.assertEqual(c_restored.wins, 2)
        self.assertEqual(c_restored.losses, 1)
        self.assertEqual(c_restored.points, 6)
        self.assertEqual(c_restored.history, ["win", "loss", "win"])

    def test_match_achievements(self):
        sm = SaveManager(self.save_path, self.config_manager)
        
        # Test basic achievements
        sm.check_match_achievements(won=True, goals=3, saves=2, opp_score=2)
        self.assertTrue(sm.data["achievements"]["first_kick"]["earned"])
        self.assertTrue(sm.data["achievements"]["first_win"]["earned"])
        self.assertFalse(sm.data["achievements"]["perfect_shootout"]["earned"])
        self.assertFalse(sm.data["achievements"]["sharp_shooter"]["earned"])

        # Test Sharp Shooter and Perfect Shootout
        sm.check_match_achievements(won=True, goals=5, saves=3, opp_score=0)
        self.assertTrue(sm.data["achievements"]["sharp_shooter"]["earned"])
        self.assertTrue(sm.data["achievements"]["perfect_shootout"]["earned"])

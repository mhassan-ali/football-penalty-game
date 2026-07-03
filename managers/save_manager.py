import json
import os
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger("SaveManager")

class SaveManager:
    def __init__(self, save_path: str = "save/savegame.json", config_manager: Any = None) -> None:
        self.save_path = save_path
        self.config_manager = config_manager
        self.data: Dict[str, Any] = {}
        self.load_game()

    def get_default_data(self) -> Dict[str, Any]:
        return {
            "settings": {
                "master_volume": 1.0,
                "music_volume": 0.8,
                "sfx_volume": 0.9
            },
            "statistics": {
                "matches_played": 0,
                "matches_won": 0,
                "goals_scored": 0,
                "saves_made": 0,
                "tournaments_played": 0,
                "tournaments_won": 0,
                "careers_played": 0,
                "careers_completed": 0
            },
            "achievements": {
                "first_kick": {"earned": False, "earned_date": ""},
                "first_win": {"earned": False, "earned_date": ""},
                "goal_machine": {"earned": False, "progress": 0, "target": 50, "earned_date": ""},
                "brick_wall": {"earned": False, "progress": 0, "target": 25, "earned_date": ""},
                "tournament_champion": {"earned": False, "earned_date": ""},
                "career_legend": {"earned": False, "earned_date": ""},
                "perfect_shootout": {"earned": False, "earned_date": ""},
                "sharp_shooter": {"earned": False, "earned_date": ""}
            },
            "tournament_progress": None,
            "career_progress": None
        }

    def load_game(self) -> None:
        """Loads and validates the save file. Resilient to corruption or missing file."""
        self.data = self.get_default_data()

        # Try to sync initial settings from config_manager if available
        if self.config_manager:
            self.data["settings"]["master_volume"] = self.config_manager.get("audio.master_volume", 1.0)
            self.data["settings"]["music_volume"] = self.config_manager.get("audio.music_volume", 0.8)
            self.data["settings"]["sfx_volume"] = self.config_manager.get("audio.sfx_volume", 0.9)

        if not os.path.exists(self.save_path):
            logger.info(f"Save file not found at {self.save_path}. Starting with fresh profile.")
            return

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            self._validate_and_merge(loaded_data)
        except Exception as e:
            logger.error(f"Error loading save game: {e}. Reverting to defaults.")

    def _validate_and_merge(self, loaded: Any) -> None:
        """Merges loaded save data into default schema, performing basic validation."""
        if not isinstance(loaded, dict):
            logger.warning("Loaded save data is not a dictionary.")
            return

        # 1. Merge settings
        if "settings" in loaded and isinstance(loaded["settings"], dict):
            for k in ["master_volume", "music_volume", "sfx_volume"]:
                if k in loaded["settings"] and isinstance(loaded["settings"][k], (int, float)):
                    self.data["settings"][k] = float(loaded["settings"][k])

        # 2. Merge statistics
        if "statistics" in loaded and isinstance(loaded["statistics"], dict):
            for k in self.data["statistics"].keys():
                if k in loaded["statistics"] and isinstance(loaded["statistics"][k], int):
                    self.data["statistics"][k] = loaded["statistics"][k]

        # 3. Merge achievements
        if "achievements" in loaded and isinstance(loaded["achievements"], dict):
            for k in self.data["achievements"].keys():
                if k in loaded["achievements"] and isinstance(loaded["achievements"][k], dict):
                    loaded_ach = loaded["achievements"][k]
                    if "earned" in loaded_ach and isinstance(loaded_ach["earned"], bool):
                        self.data["achievements"][k]["earned"] = loaded_ach["earned"]
                    if "earned_date" in loaded_ach and isinstance(loaded_ach["earned_date"], str):
                        self.data["achievements"][k]["earned_date"] = loaded_ach["earned_date"]
                    if "progress" in self.data["achievements"][k]:
                        if "progress" in loaded_ach and isinstance(loaded_ach["progress"], int):
                            self.data["achievements"][k]["progress"] = loaded_ach["progress"]

        # 4. Merge progress
        if "tournament_progress" in loaded:
            self.data["tournament_progress"] = loaded["tournament_progress"]
        if "career_progress" in loaded:
            self.data["career_progress"] = loaded["career_progress"]

    def save_game(self) -> bool:
        """Saves current data to disk. Employs a temporary file to avoid partial writes."""
        try:
            save_dir = os.path.dirname(self.save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)

            temp_path = self.save_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)

            if os.path.exists(self.save_path):
                os.remove(self.save_path)
            os.rename(temp_path, self.save_path)

            logger.info("Game saved successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            return False

    def reset_save(self) -> bool:
        """Resets all stats, progress, and achievements to defaults while preserving settings."""
        settings = self.data["settings"]
        self.data = self.get_default_data()
        self.data["settings"] = settings
        return self.save_game()

    def update_setting(self, key: str, value: float) -> None:
        if key in self.data["settings"]:
            self.data["settings"][key] = value
            if self.config_manager:
                if "audio" not in self.config_manager.settings:
                    self.config_manager.settings["audio"] = {}
                self.config_manager.settings["audio"][key] = value
                self.config_manager.save_config()
            self.save_game()

    def increment_stat(self, key: str, amount: int = 1) -> None:
        if key in self.data["statistics"]:
            self.data["statistics"][key] += amount
            self.save_game()

    def save_tournament(self, tournament: Optional[Any]) -> None:
        if tournament is None:
            self.data["tournament_progress"] = None
        else:
            self.data["tournament_progress"] = {
                "player_team": tournament.player_team,
                "teams": tournament.teams,
                "current_stage_idx": tournament.current_stage_idx,
                "eliminated": tournament.eliminated,
                "winner": tournament.winner,
                "bracket": tournament.bracket,
                "results": tournament.results
            }
        self.save_game()

    def save_career(self, career: Optional[Any]) -> None:
        if career is None:
            self.data["career_progress"] = None
        else:
            self.data["career_progress"] = {
                "team": career.team,
                "max_matches": career.max_matches,
                "current_match_idx": career.current_match_idx,
                "wins": career.wins,
                "losses": career.losses,
                "points": career.points,
                "history": career.history
            }
        self.save_game()

    def load_tournament(self, tournament_class: Any) -> Optional[Any]:
        prog = self.data.get("tournament_progress")
        if not prog:
            return None
        try:
            t = tournament_class.__new__(tournament_class)
            t.player_team = prog["player_team"]
            t.teams = prog.get("teams", ["BRAZIL", "ARGENTINA", "GERMANY", "FRANCE", "ENGLAND", "SPAIN", "ITALY", "PORTUGAL"])
            t.stages = ["Quarter Final", "Semi Final", "Final"]
            t.current_stage_idx = prog["current_stage_idx"]
            t.eliminated = prog["eliminated"]
            t.winner = prog["winner"]
            t.bracket = prog["bracket"]
            t.results = prog["results"]
            return t
        except Exception as e:
            logger.error(f"Failed to restore tournament from save: {e}")
            return None

    def load_career(self, career_class: Any) -> Optional[Any]:
        prog = self.data.get("career_progress")
        if not prog:
            return None
        try:
            c = career_class.__new__(career_class)
            c.team = prog["team"]
            c.max_matches = prog.get("max_matches", 10)
            c.current_match_idx = prog["current_match_idx"]
            c.wins = prog["wins"]
            c.losses = prog["losses"]
            c.points = prog["points"]
            c.history = prog["history"]
            return c
        except Exception as e:
            logger.error(f"Failed to restore career from save: {e}")
            return None

    def unlock_achievement(self, key: str) -> None:
        if key in self.data["achievements"] and not self.data["achievements"][key]["earned"]:
            self.data["achievements"][key]["earned"] = True
            self.data["achievements"][key]["earned_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"ACHIEVEMENT UNLOCKED: {key}")
            self.save_game()

    def update_achievement_progress(self, key: str, progress: int) -> None:
        if key in self.data["achievements"] and not self.data["achievements"][key]["earned"]:
            ach = self.data["achievements"][key]
            ach["progress"] = progress
            if ach["progress"] >= ach["target"]:
                self.unlock_achievement(key)
            else:
                self.save_game()

    def check_match_achievements(self, won: bool, goals: int, saves: int, opp_score: int) -> None:
        self.unlock_achievement("first_kick")
        if won:
            self.unlock_achievement("first_win")
        
        stats = self.data["statistics"]
        self.update_achievement_progress("goal_machine", stats["goals_scored"])
        self.update_achievement_progress("brick_wall", stats["saves_made"])
        
        if goals >= 5:
            self.unlock_achievement("sharp_shooter")
        if won and goals == 5 and opp_score == 0:
            self.unlock_achievement("perfect_shootout")

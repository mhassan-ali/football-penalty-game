import json
import os
import logging
from typing import Any, Dict

logger = logging.getLogger("ConfigManager")

DEFAULT_CONFIG: Dict[str, Any] = {
    "display": {
        "width": 1280,
        "height": 720,
        "fullscreen": False,
        "title": "Penalty Shootout"
    },
    "gameplay": {
        "target_fps": 60
    },
    "logging": {
        "level": "INFO",
        "file": "logs/game.log"
    },
    "audio": {
        "master_volume": 1.0,
        "music_volume": 0.8,
        "sfx_volume": 0.9
    }
}

class ConfigManager:
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = config_path
        self.settings: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Loads and validates settings from the config file, creating it if it doesn't exist."""
        # Ensure directory exists
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
            except Exception as e:
                logger.warning(f"Could not create configuration directory: {e}")

        # Initialize with deep copy of defaults
        self.settings = json.loads(json.dumps(DEFAULT_CONFIG))

        if not os.path.exists(self.config_path):
            logger.info(f"Config file not found. Creating default configuration at {self.config_path}")
            self.save_config()
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            self._merge_and_validate(loaded)
        except Exception as e:
            logger.error(f"Error loading configuration file '{self.config_path}': {e}. Using defaults.")

    def _merge_and_validate(self, loaded: Any) -> None:
        """Helper to merge loaded configuration with defaults, performing basic type and value checks."""
        if not isinstance(loaded, dict):
            logger.warning("Loaded configuration is not a dictionary. Using defaults.")
            return

        # Display validation
        if "display" in loaded and isinstance(loaded["display"], dict):
            disp = loaded["display"]
            # width
            if "width" in disp and isinstance(disp["width"], int) and 640 <= disp["width"] <= 3840:
                self.settings["display"]["width"] = disp["width"]
            else:
                logger.warning("Invalid or missing 'display.width'. Using default.")
            # height
            if "height" in disp and isinstance(disp["height"], int) and 480 <= disp["height"] <= 2160:
                self.settings["display"]["height"] = disp["height"]
            else:
                logger.warning("Invalid or missing 'display.height'. Using default.")
            # fullscreen
            if "fullscreen" in disp and isinstance(disp["fullscreen"], bool):
                self.settings["display"]["fullscreen"] = disp["fullscreen"]
            else:
                logger.warning("Invalid or missing 'display.fullscreen'. Using default.")
            # title
            if "title" in disp and isinstance(disp["title"], str):
                self.settings["display"]["title"] = disp["title"]

        # Gameplay validation
        if "gameplay" in loaded and isinstance(loaded["gameplay"], dict):
            gp = loaded["gameplay"]
            if "target_fps" in gp and isinstance(gp["target_fps"], int) and 10 <= gp["target_fps"] <= 240:
                self.settings["gameplay"]["target_fps"] = gp["target_fps"]
            else:
                logger.warning("Invalid or missing 'gameplay.target_fps'. Using default.")

        # Logging validation
        if "logging" in loaded and isinstance(loaded["logging"], dict):
            log = loaded["logging"]
            if "level" in log and isinstance(log["level"], str) and log["level"].upper() in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
                self.settings["logging"]["level"] = log["level"].upper()
            else:
                logger.warning("Invalid or missing 'logging.level'. Using default.")
            if "file" in log and isinstance(log["file"], str):
                self.settings["logging"]["file"] = log["file"]

        # Audio validation
        if "audio" in loaded and isinstance(loaded["audio"], dict):
            aud = loaded["audio"]
            for key in ["master_volume", "music_volume", "sfx_volume"]:
                if key in aud and (isinstance(aud[key], (int, float))) and 0.0 <= aud[key] <= 1.0:
                    self.settings["audio"][key] = float(aud[key])
                else:
                    logger.warning(f"Invalid or missing 'audio.{key}'. Using default.")

    def save_config(self) -> None:
        """Saves current settings back to settings.json."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            logger.info(f"Configuration saved successfully to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration to {self.config_path}: {e}")

    def get(self, path: str, default: Any = None) -> Any:
        """
        Retrieves a configuration value by a dot-separated path (e.g. 'display.width').
        
        Args:
            path: Dot-separated string path.
            default: Return value if the path doesn't exist.
        """
        keys = path.split(".")
        current = self.settings
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current

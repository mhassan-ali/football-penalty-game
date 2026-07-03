import sys
import logging
import pygame

from utils.logger import setup_logging
from managers.config_manager import ConfigManager
from managers.asset_manager import AssetManager
from core.event_manager import EventManager
from core.state_manager import StateManager, State
from core.scene_manager import SceneManager
from core.loop import GameLoop

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

from game.mode_manager import GameModeManager
from scenes.tournament_bracket import TournamentBracketScene
from scenes.career_hub import CareerHubScene
from scenes.championship import ChampionshipScene

def main() -> None:
    # 1. Load configuration
    config = ConfigManager("config/settings.json")

    # 2. Setup logging using loaded configuration
    log_level = config.get("logging.level", "INFO")
    log_file = config.get("logging.file", "logs/game.log")
    logger = setup_logging(log_level, log_file)
    logger.info("Application starting up...")

    # 3. Initialize Pygame subsystems
    pygame.init()
    pygame.font.init()
    try:
        pygame.mixer.init()
        logger.info("Pygame mixer initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not initialize Pygame mixer: {e}. Running without audio support.")

    # 4. Set up display
    width = config.get("display.width", 1280)
    height = config.get("display.height", 720)
    fullscreen = config.get("display.fullscreen", False)
    title = config.get("display.title", "Penalty Shootout")

    flags = pygame.FULLSCREEN if fullscreen else 0
    try:
        screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption(title)
        logger.info(f"Display window created: {width}x{height} (Fullscreen: {fullscreen})")
    except Exception as e:
        logger.critical(f"Failed to create display window: {e}")
        pygame.quit()
        sys.exit(1)

    # 5. Initialize Managers and Core Services
    event_manager = EventManager()
    state_manager = StateManager(event_manager, State.LOADING)
    scene_manager = SceneManager()
    mode_manager = GameModeManager()
    scene_manager.mode_manager = mode_manager
    asset_manager = AssetManager()
    from managers.save_manager import SaveManager
    save_manager = SaveManager("save/savegame.json", config)
    scene_manager.save_manager = save_manager

    # Restore in-progress tournament or career if saved
    from game.tournament import Tournament
    from game.career import Career
    restored_t = save_manager.load_tournament(Tournament)
    restored_c = save_manager.load_career(Career)
    if restored_t:
        mode_manager.active_mode = "tournament"
        mode_manager.tournament = restored_t
    elif restored_c:
        mode_manager.active_mode = "career"
        mode_manager.career = restored_c

    # 6. Instantiate and register all Scenes
    scenes_map = {
        "splash": SplashScene("splash", state_manager, scene_manager, asset_manager),
        "menu": MenuScene("menu", state_manager, scene_manager, asset_manager),
        "mode_select": ModeSelectScene("mode_select", state_manager, scene_manager, asset_manager),
        "team_select": TeamSelectScene("team_select", state_manager, scene_manager, asset_manager),
        "difficulty_select": DifficultySelectScene("difficulty_select", state_manager, scene_manager, asset_manager),
        "loading": LoadingScene("loading", state_manager, scene_manager, asset_manager),
        "gameplay": GameplayScene("gameplay", state_manager, scene_manager, asset_manager),
        "pause": PauseScene("pause", state_manager, scene_manager, asset_manager),
        "results": ResultsScene("results", state_manager, scene_manager, asset_manager),
        "settings": SettingsScene("settings", state_manager, scene_manager, asset_manager),
        "credits": CreditsScene("credits", state_manager, scene_manager, asset_manager),
        "exit_confirm": ExitConfirmScene("exit_confirm", state_manager, scene_manager, asset_manager),
        "tournament_bracket": TournamentBracketScene("tournament_bracket", state_manager, scene_manager, asset_manager),
        "career_hub": CareerHubScene("career_hub", state_manager, scene_manager, asset_manager),
        "championship": ChampionshipScene("championship", state_manager, scene_manager, asset_manager)
    }

    for name, scene_obj in scenes_map.items():
        scene_manager.register_scene(name, scene_obj)

    # Boot the splash scene
    scene_manager.switch_scene("splash")

    # 7. Create and configure the Game Loop
    target_fps = config.get("gameplay.target_fps", 60)
    game_loop = GameLoop(target_fps)

    # Subscribe to state transitions to manage shutdown
    def on_state_changed(data):
        if data["new_state"] == State.EXIT:
            logger.info("Exit state detected. Initiating clean shutdown...")
            game_loop.stop()

    event_manager.subscribe("state_changed", on_state_changed)

    # Define loop callbacks
    def handle_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Quit window event detected.")
                # Route through Exit Confirmation dialog from current scene
                scene_manager.switch_scene("exit_confirm", target_action="quit")
            else:
                scene_manager.handle_event(event)

    def update(dt: float):
        scene_manager.update(dt)

    def render():
        scene_manager.render(screen)
        pygame.display.flip()

    # 8. Start loop (blocks execution until stopped)
    try:
        game_loop.start(handle_events, update, render)
    except Exception as e:
        logger.critical(f"Crash detected in main loop: {e}", exc_info=True)
    finally:
        logger.info("Cleaning up resources and quitting Pygame.")
        pygame.quit()
        logger.info("Application terminated cleanly.")

if __name__ == "__main__":
    main()

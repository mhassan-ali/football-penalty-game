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
from scenes.gameplay import GameplayScene

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
    asset_manager = AssetManager()

    # 6. Instantiate and register Scenes
    splash_scene = SplashScene("splash", state_manager, scene_manager, asset_manager)
    menu_scene = MenuScene("menu", state_manager, scene_manager, asset_manager)
    gameplay_scene = GameplayScene("gameplay", state_manager, scene_manager, asset_manager)

    scene_manager.register_scene("splash", splash_scene)
    scene_manager.register_scene("menu", menu_scene)
    scene_manager.register_scene("gameplay", gameplay_scene)

    # Boot the first scene
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
                # Transition state to EXIT which triggers on_state_changed handler to stop loop
                state_manager.change_state(State.EXIT)
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
        # Clean up Pygame resources on shutdown
        logger.info("Cleaning up resources and quitting Pygame.")
        pygame.quit()
        logger.info("Application terminated cleanly.")

if __name__ == "__main__":
    main()

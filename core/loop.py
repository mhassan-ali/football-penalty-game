import logging
import pygame
from typing import Callable

logger = logging.getLogger("GameLoop")

class GameLoop:
    def __init__(self, target_fps: int = 60) -> None:
        self._clock = pygame.time.Clock()
        self.target_fps = target_fps
        self.is_running = False
        self._fps_log_timer = 0.0

    def start(self, 
              handle_events: Callable[[], None], 
              update: Callable[[float], None], 
              render: Callable[[], None]) -> None:
        """
        Starts the game loop. Runs synchronously until stopped.
        
        Args:
            handle_events: Callback for gathering/processing user input events.
            update: Callback for updating game state (dt in seconds passed).
            render: Callback for drawing frame.
        """
        if self.is_running:
            logger.warning("GameLoop is already running.")
            return

        logger.info(f"Starting GameLoop with target FPS: {self.target_fps}")
        self.is_running = True
        
        while self.is_running:
            # Tick the clock to enforce target FPS and compute elapsed milliseconds
            try:
                raw_dt_ms = self._clock.tick(self.target_fps)
            except Exception as e:
                logger.error(f"Error ticking pygame clock: {e}")
                raw_dt_ms = 16.67  # Fallback corresponding to ~60 FPS
            
            dt = raw_dt_ms / 1000.0

            # Clamp dt to avoid massive physics/state jumps (e.g. if the window is moved,
            # or the process gets suspended by OS/debugger)
            dt = min(dt, 0.1)

            # Cycle methods
            try:
                handle_events()
                update(dt)
                render()
            except Exception as e:
                logger.error(f"Uncaught exception inside game loop cycle: {e}", exc_info=True)
                # Keep the application stable if possible, but stop loop if it's critical
                # Here we just stop to exit cleanly
                self.stop()

            # Diagnostic log of average FPS every 5 seconds if log level is debug
            if logger.isEnabledFor(logging.DEBUG):
                self._fps_log_timer += dt
                if self._fps_log_timer >= 5.0:
                    logger.debug(f"Average FPS: {self._clock.get_fps():.2f}")
                    self._fps_log_timer = 0.0

        logger.info("GameLoop stopped.")

    def stop(self) -> None:
        """Stops the game loop at the end of the current frame."""
        logger.info("Stopping GameLoop request received.")
        self.is_running = False

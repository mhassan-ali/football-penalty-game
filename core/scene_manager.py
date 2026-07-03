import logging
from typing import Any, Dict, Optional
import pygame
from scenes.base import Scene

logger = logging.getLogger("SceneManager")

class SceneManager:
    def __init__(self) -> None:
        self._scenes: Dict[str, Scene] = {}
        self._active_scene: Optional[Scene] = None
        self._transition_target: Optional[str] = None
        self._transition_kwargs: Dict[str, Any] = {}
        self._transition_alpha = 0.0
        self._transition_state: Optional[str] = None  # "fade_out", "fade_in", None
        self._transition_speed = 650.0  # Speed of alpha change per second
        self.transitions_enabled = False

    @property
    def active_scene(self) -> Optional[Scene]:
        return self._active_scene

    def register_scene(self, name: str, scene: Scene) -> None:
        """
        Registers a scene in the manager.
        
        Args:
            name: Identifier name for the scene.
            scene: The Scene instance to register.
        """
        self._scenes[name] = scene
        logger.info(f"Scene registered: {name}")

    def switch_scene(self, name: str, **kwargs: Any) -> None:
        """
        Switches the active scene, triggering exit/enter hooks.
        
        Args:
            name: Registered name of the scene to switch to.
            kwargs: Parameters passed forward to the entering scene.
        """
        if name not in self._scenes:
            msg = f"Cannot switch to unregistered scene: {name}"
            logger.error(msg)
            raise KeyError(msg)

        if not self._active_scene or not self.transitions_enabled:
            logger.info(f"Transitioning immediately to scene: {name}")
            if self._active_scene:
                self._active_scene.on_exit()
            self._active_scene = self._scenes[name]
            self._active_scene.on_enter(**kwargs)
            return

        # Start visual transition
        self._transition_target = name
        self._transition_kwargs = kwargs
        self._transition_state = "fade_out"
        self._transition_alpha = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        """Delegate event to active scene if not transitioning."""
        if self._transition_state is not None:
            return  # Block input during transition
        if self._active_scene:
            self._active_scene.handle_event(event)

    def update(self, dt: float) -> None:
        """Update transition state and delegate update to active scene."""
        if self._transition_state == "fade_out":
            self._transition_alpha += self._transition_speed * dt
            if self._transition_alpha >= 255.0:
                self._transition_alpha = 255.0
                
                # Perform physical switch
                if self._active_scene:
                    logger.debug(f"Exiting scene: {self._active_scene.name}")
                    self._active_scene.on_exit()
                
                logger.info(f"Transitioning to scene: {self._transition_target}")
                self._active_scene = self._scenes[self._transition_target]
                self._active_scene.on_enter(**self._transition_kwargs)
                self._transition_state = "fade_in"
                
        elif self._transition_state == "fade_in":
            self._transition_alpha -= self._transition_speed * dt
            if self._transition_alpha <= 0.0:
                self._transition_alpha = 0.0
                self._transition_state = None
                self._transition_target = None
                self._transition_kwargs = {}

        if self._active_scene:
            self._active_scene.update(dt)

    def render(self, screen: pygame.Surface) -> None:
        """Delegate rendering to active scene and overlay transition wash."""
        if self._active_scene:
            self._active_scene.render(screen)

        if self._transition_state is not None:
            # Draw overlay surface with alpha
            wash = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            wash.fill((15, 18, 24, int(self._transition_alpha)))
            screen.blit(wash, (0, 0))

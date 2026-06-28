import logging
from typing import Any, Dict, Optional
import pygame
from scenes.base import Scene

logger = logging.getLogger("SceneManager")

class SceneManager:
    def __init__(self) -> None:
        self._scenes: Dict[str, Scene] = {}
        self._active_scene: Optional[Scene] = None

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

        if self._active_scene:
            logger.debug(f"Exiting scene: {self._active_scene.name}")
            self._active_scene.on_exit()

        logger.info(f"Transitioning to scene: {name}")
        self._active_scene = self._scenes[name]
        self._active_scene.on_enter(**kwargs)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Delegate event to active scene."""
        if self._active_scene:
            self._active_scene.handle_event(event)

    def update(self, dt: float) -> None:
        """Delegate update to active scene."""
        if self._active_scene:
            self._active_scene.update(dt)

    def render(self, screen: pygame.Surface) -> None:
        """Delegate rendering to active scene."""
        if self._active_scene:
            self._active_scene.render(screen)

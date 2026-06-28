import pygame
from typing import Any

class Scene:
    """
    Base class for all scenes in the game.
    Defines the contract for lifecycle hooks and standard loop methods.
    """
    def __init__(self, name: str, state_manager: Any = None, scene_manager: Any = None, asset_manager: Any = None) -> None:
        self.name = name
        self.state_manager = state_manager
        self.scene_manager = scene_manager
        self.asset_manager = asset_manager

    def on_enter(self, **kwargs: Any) -> None:
        """Called when transitioning into this scene."""
        pass

    def on_exit(self) -> None:
        """Called when transitioning out of this scene."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """Processes a single Pygame input event."""
        pass

    def update(self, dt: float) -> None:
        """Advances scene state by dt seconds."""
        pass

    def render(self, screen: pygame.Surface) -> None:
        """Renders scene graphics to the screen surface."""
        pass

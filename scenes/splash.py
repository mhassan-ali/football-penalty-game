import pygame
from typing import Any
from scenes.base import Scene
from core.state_manager import State

class SplashScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.timer = 2.0  # display splash for 2 seconds

    def on_enter(self, **kwargs: Any) -> None:
        self.timer = 2.0

    def update(self, dt: float) -> None:
        self.timer -= dt
        if self.timer <= 0:
            # Transition application state and switch active scene
            self.state_manager.change_state(State.MAIN_MENU)
            self.scene_manager.switch_scene("menu")

    def render(self, screen: pygame.Surface) -> None:
        # Elegant background color
        screen.fill((20, 24, 30))
        
        # Draw game title
        font = self.asset_manager.get_font("default", 48)
        text_surf = font.render("PENALTY SHOOTOUT", True, (240, 240, 240))
        text_rect = text_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 30))
        screen.blit(text_surf, text_rect)

        # Draw sub-text
        font_sub = self.asset_manager.get_font("default", 24)
        sub_text_surf = font_sub.render(f"Loading engine skeleton... {max(0.0, self.timer):.1f}s", True, (150, 160, 175))
        sub_text_rect = sub_text_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 30))
        screen.blit(sub_text_surf, sub_text_rect)

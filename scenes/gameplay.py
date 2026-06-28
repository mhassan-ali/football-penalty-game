import pygame
from typing import Any
from scenes.base import Scene
from core.state_manager import State

class GameplayScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to menu
                self.state_manager.change_state(State.MAIN_MENU)
                self.scene_manager.switch_scene("menu")

    def render(self, screen: pygame.Surface) -> None:
        # Green pitch background
        screen.fill((34, 139, 34))
        
        font = self.asset_manager.get_font("default", 48)
        text_surf = font.render("GAMEPLAY SKELETON (PHASE 2)", True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 30))
        screen.blit(text_surf, text_rect)

        font_sub = self.asset_manager.get_font("default", 24)
        sub_text_surf = font_sub.render("Press ESC to return to Main Menu", True, (220, 220, 220))
        sub_text_rect = sub_text_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 40))
        screen.blit(sub_text_surf, sub_text_rect)

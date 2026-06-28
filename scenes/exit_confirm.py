import pygame
from typing import Any
from scenes.base import Scene
from core.state_manager import State

class ExitConfirmScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.options = ["YES", "NO"]
        self.selected_index = 1  # Default to NO for safety
        self.target_action = "quit"  # "quit" or "menu"

    def on_enter(self, **kwargs: Any) -> None:
        self.selected_index = 1
        self.target_action = kwargs.get("target_action", "quit")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w):
                self.selected_index = 0
            elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s):
                self.selected_index = 1
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._confirm()
            elif event.key == pygame.K_ESCAPE:
                self._cancel()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            screen_w = 1280
            if pygame.Rect(screen_w // 2 - 160, 340, 120, 50).collidepoint(m_pos):
                self.selected_index = 0
                self._confirm()
            elif pygame.Rect(screen_w // 2 + 40, 340, 120, 50).collidepoint(m_pos):
                self.selected_index = 1
                self._confirm()

    def _confirm(self) -> None:
        if self.selected_index == 0:
            # YES clicked
            if self.target_action == "quit":
                self.state_manager.change_state(State.EXIT)
            elif self.target_action == "menu":
                self.state_manager.change_state(State.MAIN_MENU)
                self.scene_manager.switch_scene("menu")
        else:
            # NO clicked
            self._cancel()

    def _cancel(self) -> None:
        if self.target_action == "quit":
            self.scene_manager.switch_scene("menu")
        elif self.target_action == "menu":
            self.scene_manager.switch_scene("pause")

    def render(self, screen: pygame.Surface) -> None:
        # Dark overlay
        wash = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        wash.fill((10, 12, 16, 230))
        screen.blit(wash, (0, 0))

        font_title = self.asset_manager.get_font("default", 48)
        if self.target_action == "quit":
            prompt = "ARE YOU SURE YOU WANT TO QUIT?"
        else:
            prompt = "QUIT MATCH AND RETURN TO MENU?"
            
        title_surf = font_title.render(prompt, True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 220))
        screen.blit(title_surf, title_rect)

        # Buttons
        font_opt = self.asset_manager.get_font("default", 36)
        
        # YES button
        yes_col = (255, 255, 255) if self.selected_index == 0 else (120, 130, 140)
        yes_prefix = "> " if self.selected_index == 0 else "  "
        yes_surf = font_opt.render(yes_prefix + "YES", True, yes_col)
        yes_rect = yes_surf.get_rect(center=(screen.get_width() // 2 - 100, 360))
        screen.blit(yes_surf, yes_rect)

        # NO button
        no_col = (255, 255, 255) if self.selected_index == 1 else (120, 130, 140)
        no_prefix = "> " if self.selected_index == 1 else "  "
        no_surf = font_opt.render(no_prefix + "NO", True, no_col)
        no_rect = no_surf.get_rect(center=(screen.get_width() // 2 + 100, 360))
        screen.blit(no_surf, no_rect)

        font_help = self.asset_manager.get_font("default", 20)
        help_surf = font_help.render("LEFT/RIGHT to select, ENTER to confirm. ESC to cancel.", True, (150, 150, 150))
        help_rect = help_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
        screen.blit(help_surf, help_rect)

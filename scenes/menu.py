import pygame
from typing import Any
from scenes.base import Scene
from core.state_manager import State

class MenuScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.options = ["PLAY GAME (PHASE 2)", "QUIT"]
        self.selected_index = 0

    def on_enter(self, **kwargs: Any) -> None:
        self.selected_index = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._select_option()
            elif event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(State.EXIT)

    def _select_option(self) -> None:
        if self.selected_index == 0:
            self.state_manager.change_state(State.GAMEPLAY)
            self.scene_manager.switch_scene("gameplay")
        elif self.selected_index == 1:
            self.state_manager.change_state(State.EXIT)

    def render(self, screen: pygame.Surface) -> None:
        # Sleek dark background
        screen.fill((30, 34, 42))
        
        # Title
        font_title = self.asset_manager.get_font("default", 64)
        title_surf = font_title.render("MAIN MENU", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 150))
        screen.blit(title_surf, title_rect)

        # Options list
        font_opt = self.asset_manager.get_font("default", 32)
        for idx, option in enumerate(self.options):
            color = (255, 255, 255) if idx == self.selected_index else (120, 130, 140)
            prefix = "> " if idx == self.selected_index else "  "
            opt_surf = font_opt.render(prefix + option, True, color)
            opt_rect = opt_surf.get_rect(center=(screen.get_width() // 2, 300 + idx * 60))
            screen.blit(opt_surf, opt_rect)

        # Helper instructions
        font_help = self.asset_manager.get_font("default", 20)
        help_surf = font_help.render("Use UP/DOWN or W/S to navigate, ENTER to select. ESC to quit.", True, (150, 150, 150))
        help_rect = help_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
        screen.blit(help_surf, help_rect)

import pygame
from typing import Any
from scenes.base import Scene
from core.state_manager import State

class PauseScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.options = ["RESUME", "RESTART MATCH", "SETTINGS", "RETURN TO MAIN MENU"]
        self.selected_index = 0

    def on_enter(self, **kwargs: Any) -> None:
        self.selected_index = 0
        if self.state_manager.current_state != State.PAUSED:
            self.state_manager.change_state(State.PAUSED)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._select_option()
            elif event.key == pygame.K_ESCAPE:
                self._resume()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            screen_w = 1280
            for idx in range(len(self.options)):
                rect = pygame.Rect(screen_w // 2 - 200, 260 + idx * 60, 400, 45)
                if rect.collidepoint(m_pos):
                    self.selected_index = idx
                    self._select_option()

    def _resume(self) -> None:
        self.state_manager.change_state(State.GAMEPLAY)
        self.scene_manager.switch_scene("gameplay", is_resume=True)

    def _select_option(self) -> None:
        if self.selected_index == 0:
            self._resume()
        elif self.selected_index == 1:
            # Restart match
            self.state_manager.change_state(State.GAMEPLAY)
            self.scene_manager.switch_scene("loading")
        elif self.selected_index == 2:
            # Settings from pause
            self.scene_manager.switch_scene("settings", origin_scene="pause")
        elif self.selected_index == 3:
            # Return to main menu (triggers confirm dialog per APP_FLOW)
            self.scene_manager.switch_scene("exit_confirm", target_action="menu", origin_scene=self.name)

    def render(self, screen: pygame.Surface) -> None:
        # Semi-transparent dark overlay over whatever was rendered before or solid dark background
        wash = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        wash.fill((15, 18, 24, 230))
        screen.blit(wash, (0, 0))

        font_title = self.asset_manager.get_font("default", 64)
        title_surf = font_title.render("MATCH PAUSED", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 140))
        screen.blit(title_surf, title_rect)

        font_opt = self.asset_manager.get_font("default", 32)
        for idx, option in enumerate(self.options):
            color = (255, 255, 255) if idx == self.selected_index else (130, 140, 150)
            prefix = "> " if idx == self.selected_index else "  "
            opt_surf = font_opt.render(prefix + option, True, color)
            opt_rect = opt_surf.get_rect(center=(screen.get_width() // 2, 270 + idx * 60))
            screen.blit(opt_surf, opt_rect)

        font_help = self.asset_manager.get_font("default", 20)
        help_surf = font_help.render("UP/DOWN or W/S to navigate, ENTER to select. ESC to resume.", True, (150, 150, 150))
        help_rect = help_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
        screen.blit(help_surf, help_rect)

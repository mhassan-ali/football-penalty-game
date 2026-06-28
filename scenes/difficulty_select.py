import pygame
from typing import Any
from scenes.base import Scene

class DifficultySelectScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.options = ["EASY (Forgiving keeper & slower dives)", "MEDIUM (Balanced competition)", "HARD (Smart corner keeper & fast dives)", "BACK"]
        self.difficulties = ["easy", "medium", "hard"]
        self.selected_index = 1  # Default to Medium
        self.selected_team = "BRAZIL"

    def on_enter(self, **kwargs: Any) -> None:
        if "selected_team" in kwargs:
            self.selected_team = kwargs["selected_team"]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._confirm_difficulty()
            elif event.key == pygame.K_ESCAPE:
                self.scene_manager.switch_scene("team_select")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            screen_w = 1280
            for idx in range(len(self.options)):
                rect = pygame.Rect(screen_w // 2 - 300, 260 + idx * 65, 600, 50)
                if rect.collidepoint(m_pos):
                    self.selected_index = idx
                    self._confirm_difficulty()

    def _confirm_difficulty(self) -> None:
        if self.selected_index == 3:
            self.scene_manager.switch_scene("team_select")
        else:
            diff = self.difficulties[self.selected_index]
            self.scene_manager.switch_scene("loading", selected_team=self.selected_team, difficulty=diff)

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((30, 34, 42))
        
        # Title
        font_title = self.asset_manager.get_font("default", 54)
        title_surf = font_title.render("SELECT DIFFICULTY", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 120))
        screen.blit(title_surf, title_rect)

        # Team subtext
        font_sub = self.asset_manager.get_font("default", 24)
        sub_surf = font_sub.render(f"Representing: {self.selected_team}", True, (200, 200, 200))
        sub_rect = sub_surf.get_rect(center=(screen.get_width() // 2, 180))
        screen.blit(sub_surf, sub_rect)

        # Options
        font_opt = self.asset_manager.get_font("default", 28)
        for idx, option in enumerate(self.options):
            color = (255, 255, 255) if idx == self.selected_index else (130, 140, 150)
            prefix = "> " if idx == self.selected_index else "  "
            opt_surf = font_opt.render(prefix + option, True, color)
            opt_rect = opt_surf.get_rect(center=(screen.get_width() // 2, 270 + idx * 65))
            screen.blit(opt_surf, opt_rect)

        # Hint
        font_help = self.asset_manager.get_font("default", 20)
        help_surf = font_help.render("UP/DOWN or W/S to select, ENTER to launch match. ESC for back.", True, (150, 150, 150))
        help_rect = help_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40))
        screen.blit(help_surf, help_rect)

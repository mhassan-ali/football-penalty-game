import pygame
from typing import Any
from scenes.base import Scene

class TeamSelectScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.teams = ["BRAZIL 🇧🇷", "ARGENTINA 🇦🇷", "GERMANY 🇩🇪", "FRANCE 🇫🇷", "ENGLAND 🏴󠁧󠁢󠁥󠁮󠁧󠁿", "SPAIN 🇪🇸"]
        self.selected_index = 0

    def on_enter(self, **kwargs: Any) -> None:
        self.selected_index = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        audio_mgr = getattr(self.scene_manager, "audio_manager", None)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.teams)
                if audio_mgr:
                    audio_mgr.play_sfx("hover")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.teams)
                if audio_mgr:
                    audio_mgr.play_sfx("hover")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self._confirm_team()
            elif event.key == pygame.K_ESCAPE:
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self.scene_manager.switch_scene("mode_select")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            screen_w = 1280
            for idx in range(len(self.teams)):
                rect = pygame.Rect(screen_w // 2 - 200, 210 + idx * 55, 400, 45)
                if rect.collidepoint(m_pos):
                    self.selected_index = idx
                    if audio_mgr:
                        audio_mgr.play_sfx("click")
                    self._confirm_team()

    def _confirm_team(self) -> None:
        chosen_team = self.teams[self.selected_index].split()[0]  # Get team name without emoji
        self.scene_manager.switch_scene("difficulty_select", selected_team=chosen_team)

    def render(self, screen: pygame.Surface) -> None:
        import math
        screen.fill((30, 34, 42))
        
        # Title
        font_title = self.asset_manager.get_font("default", 54)
        title_surf = font_title.render("SELECT YOUR TEAM", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 120))
        screen.blit(title_surf, title_rect)

        # Teams list
        font_opt = self.asset_manager.get_font("default", 32)
        for idx, team in enumerate(self.teams):
            is_sel = (idx == self.selected_index)
            color = (255, 215, 0) if is_sel else (140, 150, 165)
            
            x_offset = int(6 * math.sin(pygame.time.get_ticks() * 0.008)) if is_sel else 0
            prefix = "▶ " if is_sel else "  "
            
            if is_sel:
                box_rect = pygame.Rect(screen.get_width() // 2 - 220 + x_offset, 205 + idx * 55, 440, 45)
                pygame.draw.rect(screen, (50, 60, 75), box_rect, border_radius=6)
                pygame.draw.rect(screen, (255, 215, 0), box_rect, width=2, border_radius=6)
                
            opt_surf = font_opt.render(prefix + team, True, color)
            opt_rect = opt_surf.get_rect(center=(screen.get_width() // 2 + x_offset, 227 + idx * 55))
            screen.blit(opt_surf, opt_rect)

        # Hint
        font_help = self.asset_manager.get_font("default", 20)
        help_surf = font_help.render("UP/DOWN or W/S to browse, ENTER to confirm. ESC for back.", True, (150, 150, 150))
        help_rect = help_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40))
        screen.blit(help_surf, help_rect)

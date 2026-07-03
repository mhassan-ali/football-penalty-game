import pygame
from typing import Any
from scenes.base import Scene
from core.state_manager import State

class ModeSelectScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.options = ["PRACTICE MODE", "TOURNAMENT MODE", "CAREER MODE", "BACK"]
        self.selected_index = 0

    def on_enter(self, **kwargs: Any) -> None:
        self.selected_index = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        audio_mgr = getattr(self.scene_manager, "audio_manager", None)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
                if audio_mgr:
                    audio_mgr.play_sfx("hover")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
                if audio_mgr:
                    audio_mgr.play_sfx("hover")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self._select_option()
            elif event.key == pygame.K_ESCAPE:
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self.scene_manager.switch_scene("menu")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            screen_w = 1280
            for idx in range(len(self.options)):
                rect = pygame.Rect(screen_w // 2 - 200, 270 + idx * 60, 400, 45)
                if rect.collidepoint(m_pos):
                    self.selected_index = idx
                    if audio_mgr:
                        audio_mgr.play_sfx("click")
                    self._select_option()

    def _select_option(self) -> None:
        mode_mgr = self.scene_manager.mode_manager
        if self.selected_index == 0:
            mode_mgr.active_mode = "practice"
            self.scene_manager.switch_scene("team_select")
        elif self.selected_index == 1:
            mode_mgr.active_mode = "tournament"
            if mode_mgr.tournament and not mode_mgr.tournament.eliminated and mode_mgr.tournament.current_stage_idx < 3:
                self.scene_manager.switch_scene("tournament_bracket")
            else:
                self.scene_manager.switch_scene("team_select")
        elif self.selected_index == 2:
            mode_mgr.active_mode = "career"
            if mode_mgr.career:
                self.scene_manager.switch_scene("career_hub")
            else:
                self.scene_manager.switch_scene("team_select")
        elif self.selected_index == 3:
            self.scene_manager.switch_scene("menu")

    def render(self, screen: pygame.Surface) -> None:
        import math
        screen.fill((30, 34, 42))
        
        # Header
        font_title = self.asset_manager.get_font("default", 54)
        title_surf = font_title.render("SELECT GAME MODE", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 140))
        screen.blit(title_surf, title_rect)

        # Options
        font_opt = self.asset_manager.get_font("default", 32)
        for idx, option in enumerate(self.options):
            is_sel = (idx == self.selected_index)
            color = (255, 215, 0) if is_sel else (140, 150, 165)
            
            x_offset = int(6 * math.sin(pygame.time.get_ticks() * 0.008)) if is_sel else 0
            prefix = "▶ " if is_sel else "  "
            
            if is_sel:
                box_rect = pygame.Rect(screen.get_width() // 2 - 220 + x_offset, 275 + idx * 60, 440, 45)
                pygame.draw.rect(screen, (50, 60, 75), box_rect, border_radius=6)
                pygame.draw.rect(screen, (255, 215, 0), box_rect, width=2, border_radius=6)
                
            opt_surf = font_opt.render(prefix + option, True, color)
            opt_rect = opt_surf.get_rect(center=(screen.get_width() // 2 + x_offset, 297 + idx * 60))
            screen.blit(opt_surf, opt_rect)

        # Navigation hint
        font_help = self.asset_manager.get_font("default", 20)
        help_surf = font_help.render("UP/DOWN or W/S to navigate, ENTER to select. ESC for back.", True, (150, 150, 150))
        help_rect = help_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
        screen.blit(help_surf, help_rect)

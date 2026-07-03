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
                self._confirm_difficulty()
            elif event.key == pygame.K_ESCAPE:
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self.scene_manager.switch_scene("team_select")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            screen_w = 1280
            for idx in range(len(self.options)):
                rect = pygame.Rect(screen_w // 2 - 300, 260 + idx * 65, 600, 50)
                if rect.collidepoint(m_pos):
                    self.selected_index = idx
                    if audio_mgr:
                        audio_mgr.play_sfx("click")
                    self._confirm_difficulty()

    def _confirm_difficulty(self) -> None:
        if self.selected_index == 3:
            self.scene_manager.switch_scene("team_select")
            return
            
        diff = self.difficulties[self.selected_index]
        mode_mgr = self.scene_manager.mode_manager
        save_mgr = self.scene_manager.save_manager
        
        if mode_mgr.active_mode == "practice":
            self.scene_manager.switch_scene("loading", selected_team=self.selected_team, difficulty=diff)
        elif mode_mgr.active_mode == "tournament":
            mode_mgr.start_tournament(self.selected_team)
            if save_mgr:
                save_mgr.increment_stat("tournaments_played")
                save_mgr.save_tournament(mode_mgr.tournament)
            self.scene_manager.switch_scene("tournament_bracket", difficulty=diff)
        elif mode_mgr.active_mode == "career":
            mode_mgr.start_career(self.selected_team)
            if save_mgr:
                save_mgr.increment_stat("careers_played")
                save_mgr.save_career(mode_mgr.career)
            self.scene_manager.switch_scene("career_hub", difficulty=diff)

    def render(self, screen: pygame.Surface) -> None:
        import math
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
        font_opt = self.asset_manager.get_font("default", 26)
        for idx, option in enumerate(self.options):
            is_sel = (idx == self.selected_index)
            color = (255, 215, 0) if is_sel else (140, 150, 165)
            
            x_offset = int(6 * math.sin(pygame.time.get_ticks() * 0.008)) if is_sel else 0
            prefix = "▶ " if is_sel else "  "
            
            if is_sel:
                box_rect = pygame.Rect(screen.get_width() // 2 - 310 + x_offset, 245 + idx * 65, 620, 50)
                pygame.draw.rect(screen, (50, 60, 75), box_rect, border_radius=6)
                pygame.draw.rect(screen, (255, 215, 0), box_rect, width=2, border_radius=6)
                
            opt_surf = font_opt.render(prefix + option, True, color)
            opt_rect = opt_surf.get_rect(center=(screen.get_width() // 2 + x_offset, 270 + idx * 65))
            screen.blit(opt_surf, opt_rect)

        # Hint
        font_help = self.asset_manager.get_font("default", 20)
        help_surf = font_help.render("UP/DOWN or W/S to select, ENTER to launch. ESC for back.", True, (150, 150, 150))
        help_rect = help_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40))
        screen.blit(help_surf, help_rect)

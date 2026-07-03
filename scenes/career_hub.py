import pygame
from typing import Any
from scenes.base import Scene

class CareerHubScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.options = ["PLAY NEXT MATCH", "RETURN TO MAIN MENU"]
        self.selected_index = 0
        self.difficulty = "medium"

    def on_enter(self, **kwargs: Any) -> None:
        self.selected_index = 0
        if "difficulty" in kwargs:
            self.difficulty = kwargs["difficulty"]

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
                rect = pygame.Rect(screen_w // 2 - 200, 480 + idx * 55, 400, 45)
                if rect.collidepoint(m_pos):
                    self.selected_index = idx
                    if audio_mgr:
                        audio_mgr.play_sfx("click")
                    self._select_option()

    def _select_option(self) -> None:
        mode_mgr = self.scene_manager.mode_manager
        if self.selected_index == 0:
            if mode_mgr.career and not mode_mgr.career.is_finished():
                # Switch to loading screen
                self.scene_manager.switch_scene(
                    "loading", 
                    selected_team=mode_mgr.career.team, 
                    difficulty=self.difficulty
                )
        elif self.selected_index == 1:
            self.scene_manager.switch_scene("menu")

    def render(self, screen: pygame.Surface) -> None:
        import math
        screen.fill((20, 24, 30))
        
        # Header
        font_title = self.asset_manager.get_font("default", 54)
        title_surf = font_title.render("CAREER HUB", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 70))
        screen.blit(title_surf, title_rect)

        mode_mgr = self.scene_manager.mode_manager
        c = mode_mgr.career
        if not c:
            return

        # Career stats card panel
        board_w, board_h = 500, 310
        board_x = (screen.get_width() - board_w) // 2
        pygame.draw.rect(screen, (30, 36, 46), (board_x, 120, board_w, board_h), border_radius=8)
        pygame.draw.rect(screen, (50, 60, 75), (board_x, 120, board_w, board_h), width=2, border_radius=8)

        font_lbl = self.asset_manager.get_font("default", 28)
        team_surf = font_lbl.render(f"CLUB: {c.team}", True, (255, 255, 255))
        screen.blit(team_surf, (board_x + 40, 150))

        diff_surf = font_lbl.render(f"DIFFICULTY: {self.difficulty.upper()}", True, (150, 160, 180))
        screen.blit(diff_surf, (board_x + 40, 190))

        match_txt = f"MATCHES: {c.current_match_idx - 1} / {c.max_matches}" if c.current_match_idx <= c.max_matches else f"MATCHES: COMPLETED ({c.max_matches})"
        match_surf = font_lbl.render(match_txt, True, (200, 200, 200))
        screen.blit(match_surf, (board_x + 40, 230))

        w_surf = font_lbl.render(f"WINS: {c.wins}", True, (0, 255, 100))
        l_surf = font_lbl.render(f"LOSSES: {c.losses}", True, (255, 50, 50))
        p_surf = font_lbl.render(f"POINTS: {c.points}", True, (255, 215, 0))
        screen.blit(w_surf, (board_x + 40, 280))
        screen.blit(l_surf, (board_x + 40, 310))
        screen.blit(p_surf, (board_x + board_w - 240, 290))

        # History log indicators (small green/red boxes representing match results)
        font_hist = self.asset_manager.get_font("default", 18)
        hist_lbl = font_hist.render("FORM: ", True, (200, 200, 200))
        screen.blit(hist_lbl, (board_x + 40, 370))
        
        box_sz = 20
        spacing = 6
        for idx, res in enumerate(c.history):
            col = (0, 255, 100) if res == "win" else (255, 50, 50)
            pygame.draw.rect(screen, col, (board_x + 110 + idx * (box_sz + spacing), 370, box_sz, box_sz), border_radius=3)

        # Options
        font_opt = self.asset_manager.get_font("default", 28)
        for idx, option in enumerate(self.options):
            is_sel = (idx == self.selected_index)
            color = (255, 215, 0) if is_sel else (140, 150, 165)
            
            x_offset = int(6 * math.sin(pygame.time.get_ticks() * 0.008)) if is_sel else 0
            prefix = "▶ " if is_sel else "  "
            
            # Lock "PLAY NEXT MATCH" if career finished
            if idx == 0 and c.is_finished():
                option = "CAREER SEASON COMPLETED"
                color = (80, 90, 100)
                
            if is_sel:
                box_rect = pygame.Rect(screen.get_width() // 2 - 220 + x_offset, 455 + idx * 55, 440, 45)
                pygame.draw.rect(screen, (50, 60, 75), box_rect, border_radius=6)
                pygame.draw.rect(screen, (255, 215, 0), box_rect, width=2, border_radius=6)
                
            opt_surf = font_opt.render(prefix + option, True, color)
            opt_rect = opt_surf.get_rect(center=(screen.get_width() // 2 + x_offset, 477 + idx * 55))
            screen.blit(opt_surf, opt_rect)

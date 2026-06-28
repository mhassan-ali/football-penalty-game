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
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._select_option()
            elif event.key == pygame.K_ESCAPE:
                self.scene_manager.switch_scene("menu")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            screen_w = 1280
            for idx in range(len(self.options)):
                rect = pygame.Rect(screen_w // 2 - 200, 480 + idx * 60, 400, 45)
                if rect.collidepoint(m_pos):
                    self.selected_index = idx
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
        screen.fill((30, 34, 42))
        
        # Header
        font_title = self.asset_manager.get_font("default", 54)
        title_surf = font_title.render("CAREER HUB", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title_surf, title_rect)

        mode_mgr = self.scene_manager.mode_manager
        c = mode_mgr.career
        if not c:
            return

        # Render Standings Dashboard Box
        board_w = 600
        board_h = 240
        board_x = (screen.get_width() - board_w) // 2
        pygame.draw.rect(screen, (40, 48, 60), (board_x, 180, board_w, board_h), border_radius=8)
        pygame.draw.rect(screen, (60, 75, 95), (board_x, 180, board_w, board_h), width=2, border_radius=8)

        # Draw details inside Standings
        font_dash = self.asset_manager.get_font("default", 32)
        font_lbl = self.asset_manager.get_font("default", 22)
        
        # Row 1: Team & Season Progression
        team_surf = font_dash.render(f"Club: {c.team}", True, (255, 215, 0))
        prog_surf = font_dash.render(f"Match: {min(c.max_matches, c.current_match_idx)} / {c.max_matches}", True, (255, 255, 255))
        screen.blit(team_surf, (board_x + 40, 210))
        screen.blit(prog_surf, (board_x + board_w - 240, 210))

        # Row 2: Stats (Wins, Losses, Points)
        w_surf = font_lbl.render(f"WINS: {c.wins}", True, (0, 255, 100))
        l_surf = font_lbl.render(f"LOSSES: {c.losses}", True, (255, 50, 50))
        p_surf = font_dash.render(f"POINTS: {c.points}", True, (255, 255, 255))
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
            color = (255, 255, 255) if idx == self.selected_index else (130, 140, 150)
            prefix = "> " if idx == self.selected_index else "  "
            
            # Lock "PLAY NEXT MATCH" if career finished
            if idx == 0 and c.is_finished():
                option = "CAREER SEASON COMPLETED"
                color = (80, 90, 100)
                
            opt_surf = font_opt.render(prefix + option, True, color)
            opt_rect = opt_surf.get_rect(center=(screen.get_width() // 2, 480 + idx * 55))
            screen.blit(opt_surf, opt_rect)

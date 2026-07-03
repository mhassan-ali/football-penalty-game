import pygame
from typing import Any
from scenes.base import Scene

class TournamentBracketScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.options = ["START NEXT MATCH", "ABANDON TOURNAMENT"]
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
                self.scene_manager.switch_scene("exit_confirm", target_action="menu", origin_scene=self.name)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            # Buttons are placed at the bottom
            # Button 1: Start Next Match, Button 2: Abandon
            screen_w = 1280
            for idx in range(len(self.options)):
                rect = pygame.Rect(screen_w // 2 - 200, 560 + idx * 55, 400, 45)
                if rect.collidepoint(m_pos):
                    self.selected_index = idx
                    self._select_option()

    def _select_option(self) -> None:
        mode_mgr = self.scene_manager.mode_manager
        if self.selected_index == 0:
            if mode_mgr.tournament and not mode_mgr.tournament.eliminated:
                t1, t2 = mode_mgr.tournament.get_player_match()
                opponent = t2 if t1 == mode_mgr.tournament.player_team else t1
                
                # Switch to loading scene with difficulty
                self.scene_manager.switch_scene(
                    "loading", 
                    selected_team=mode_mgr.tournament.player_team, 
                    difficulty=self.difficulty,
                    opponent=opponent
                )
        elif self.selected_index == 1:
            # Abandon tournament (requires confirm dialog per App Flow)
            self.scene_manager.switch_scene("exit_confirm", target_action="menu", origin_scene=self.name)

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((30, 34, 42))
        
        # Header
        font_title = self.asset_manager.get_font("default", 54)
        title_surf = font_title.render("TOURNAMENT BRACKET", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 80))
        screen.blit(title_surf, title_rect)

        mode_mgr = self.scene_manager.mode_manager
        t = mode_mgr.tournament
        if not t:
            return

        # Render stage sub-header
        font_stage = self.asset_manager.get_font("default", 28)
        current_stage = t.stages[t.current_stage_idx] if t.current_stage_idx < 3 else "CHAMPIONSHIP COMPLETE"
        stage_surf = font_stage.render(f"Current Round: {current_stage.upper()}", True, (240, 240, 240))
        stage_rect = stage_surf.get_rect(center=(screen.get_width() // 2, 130))
        screen.blit(stage_surf, stage_rect)

        # Draw Bracket columns (Quarter, Semi, Final)
        font_teams = self.asset_manager.get_font("default", 18)
        
        col_w = 280
        col_spacing = 80
        start_x = (screen.get_width() - (3 * col_w + 2 * col_spacing)) // 2
        
        # 1. Render Quarter Finals column
        self._render_bracket_column(screen, start_x, 170, col_w, "QUARTER FINAL", t.bracket["Quarter Final"], t.results["Quarter Final"], t.player_team, font_teams)

        # 2. Render Semi Finals column
        sf_y = 230
        self._render_bracket_column(screen, start_x + col_w + col_spacing, sf_y, col_w, "SEMI FINAL", t.bracket["Semi Final"], t.results["Semi Final"], t.player_team, font_teams)

        # 3. Render Final column
        f_y = 290
        self._render_bracket_column(screen, start_x + 2 * (col_w + col_spacing), f_y, col_w, "FINAL", t.bracket["Final"], t.results["Final"], t.player_team, font_teams)

        # Render options at the bottom
        font_opt = self.asset_manager.get_font("default", 28)
        for idx, option in enumerate(self.options):
            color = (255, 255, 255) if idx == self.selected_index else (130, 140, 150)
            prefix = "> " if idx == self.selected_index else "  "
            opt_surf = font_opt.render(prefix + option, True, color)
            opt_rect = opt_surf.get_rect(center=(screen.get_width() // 2, 560 + idx * 50))
            screen.blit(opt_surf, opt_rect)

    def _render_bracket_column(self, screen: pygame.Surface, x: int, y_start: int, width: int, header: str, matches: list, winners: list, player_team: str, font: pygame.font.Font) -> None:
        # Draw header
        font_hdr = self.asset_manager.get_font("default", 20)
        hdr_surf = font_hdr.render(header, True, (255, 215, 0))
        screen.blit(hdr_surf, (x + 10, y_start - 25))
        
        box_h = 45
        spacing = 15
        
        for idx, match in enumerate(matches):
            t1, t2 = match
            y = y_start + idx * (box_h + spacing)
            
            # Determine match colors
            bg_color = (40, 48, 60)
            border_color = (60, 75, 95)
            
            # Highlight player active match
            if t1 == player_team or t2 == player_team:
                bg_color = (45, 68, 102)
                border_color = (0, 153, 255)
            
            # Draw box frame
            pygame.draw.rect(screen, bg_color, (x, y, width, box_h), border_radius=4)
            pygame.draw.rect(screen, border_color, (x, y, width, box_h), width=1, border_radius=4)
            
            # Render match text
            t1_win = (len(winners) > idx and winners[idx] == t1)
            t2_win = (len(winners) > idx and winners[idx] == t2)
            
            t1_col = (255, 255, 255) if t1_win or len(winners) <= idx else (100, 110, 120)
            t2_col = (255, 255, 255) if t2_win or len(winners) <= idx else (100, 110, 120)
            
            t1_surf = font.render(f"{t1}" + (" (W)" if t1_win else ""), True, t1_col)
            t2_surf = font.render(f"{t2}" + (" (W)" if t2_win else ""), True, t2_col)
            
            screen.blit(t1_surf, (x + 10, y + 5))
            screen.blit(t2_surf, (x + 10, y + 23))
            
            # Draw VS divider
            vs_surf = font.render("VS", True, (255, 215, 0))
            screen.blit(vs_surf, (x + width - 35, y + 14))

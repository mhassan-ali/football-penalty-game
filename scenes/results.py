import pygame
from typing import Any
from scenes.base import Scene
from core.state_manager import State

class ResultsScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.options = ["RETRY MATCH", "CONTINUE", "RETURN TO MAIN MENU"]
        self.selected_index = 0
        self.winner = "player"
        self.player_score = 0
        self.opponent_score = 0
        self.selected_team = "BRAZIL"
        self.difficulty = "medium"
        self.player_saves = 0

    def on_enter(self, **kwargs: Any) -> None:
        self.selected_index = 0
        self.winner = kwargs.get("winner", "player")
        self.player_score = kwargs.get("player_score", 0)
        self.opponent_score = kwargs.get("opponent_score", 0)
        self.selected_team = kwargs.get("selected_team", "BRAZIL")
        self.difficulty = kwargs.get("difficulty", "medium")
        self.player_saves = kwargs.get("player_saves", 0)
        
        # Ensure state is RESULT
        if self.state_manager.current_state != State.RESULT:
            self.state_manager.change_state(State.RESULT)

        # Update mode progression
        mode_mgr = self.scene_manager.mode_manager
        player_won = (self.winner == "player")
        
        if mode_mgr.active_mode == "tournament" and mode_mgr.tournament:
            mode_mgr.tournament.advance_stage(player_won)
        elif mode_mgr.active_mode == "career" and mode_mgr.career:
            mode_mgr.career.record_match(player_won)

        # Update stats & achievements & save game
        save_mgr = self.scene_manager.save_manager
        if save_mgr:
            save_mgr.increment_stat("matches_played")
            if player_won:
                save_mgr.increment_stat("matches_won")
            save_mgr.increment_stat("goals_scored", self.player_score)
            save_mgr.increment_stat("saves_made", self.player_saves)

            if mode_mgr.active_mode == "tournament" and mode_mgr.tournament:
                t = mode_mgr.tournament
                if t.winner == t.player_team:
                    save_mgr.increment_stat("tournaments_won")
                    save_mgr.check_tournament_champion()
                    save_mgr.save_tournament(None)
                elif t.eliminated:
                    save_mgr.save_tournament(None)
                else:
                    save_mgr.save_tournament(t)
            elif mode_mgr.active_mode == "career" and mode_mgr.career:
                c = mode_mgr.career
                if c.is_finished():
                    save_mgr.increment_stat("careers_completed")
                    save_mgr.check_career_legend()
                    save_mgr.save_career(None)
                else:
                    save_mgr.save_career(c)

            save_mgr.check_match_achievements(player_won, self.player_score, self.player_saves, self.opponent_score)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._select_option()
            elif event.key == pygame.K_ESCAPE:
                self._go_to_menu()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            screen_w = 1280
            for idx in range(len(self.options)):
                rect = pygame.Rect(screen_w // 2 - 200, 340 + idx * 60, 400, 45)
                if rect.collidepoint(m_pos):
                    self.selected_index = idx
                    self._select_option()

    def _select_option(self) -> None:
        mode_mgr = self.scene_manager.mode_manager
        
        if self.selected_index == 0:
            # Retry Match: go back to Gameplay
            self.state_manager.change_state(State.SAVING)
            self.state_manager.change_state(State.GAMEPLAY)
            # Re-initialize the active mode round back to same state
            # If in tournament or career, we need to roll back the result we just recorded!
            # Since we just advanced stage or recorded match in on_enter:
            save_mgr = self.scene_manager.save_manager
            player_won = (self.winner == "player")
            if save_mgr:
                save_mgr.increment_stat("matches_played", -1)
                if player_won:
                    save_mgr.increment_stat("matches_won", -1)
                save_mgr.increment_stat("goals_scored", -self.player_score)
                save_mgr.increment_stat("saves_made", -self.player_saves)

            if mode_mgr.active_mode == "tournament" and mode_mgr.tournament:
                # Rollback tournament stage indices
                t = mode_mgr.tournament
                if t.eliminated:
                    t.eliminated = False
                    stage = t.stages[t.current_stage_idx]
                    t.results[stage] = []
                else:
                    if t.winner == t.player_team:
                        t.winner = None
                        t.current_stage_idx = 2
                    else:
                        t.current_stage_idx = max(0, t.current_stage_idx - 1)
                    stage = t.stages[t.current_stage_idx]
                    t.results[stage] = []
                
                if save_mgr:
                    save_mgr.save_tournament(t)

            elif mode_mgr.active_mode == "career" and mode_mgr.career:
                # Rollback career index
                c = mode_mgr.career
                c.current_match_idx = max(1, c.current_match_idx - 1)
                if len(c.history) > 0:
                    last_res = c.history.pop()
                    if last_res == "win":
                        c.wins -= 1
                        c.points -= 3
                    else:
                        c.losses -= 1
                
                if save_mgr:
                    save_mgr.save_career(c)
            
            self.scene_manager.switch_scene("loading", selected_team=self.selected_team, difficulty=self.difficulty)
            
        elif self.selected_index == 1:
            # Continue -> Route based on active mode
            self.state_manager.change_state(State.SAVING)
            
            if mode_mgr.active_mode == "practice":
                self.state_manager.change_state(State.MAIN_MENU)
                self.scene_manager.switch_scene("menu")
                
            elif mode_mgr.active_mode == "tournament" and mode_mgr.tournament:
                t = mode_mgr.tournament
                if t.eliminated:
                    # Player lost/eliminated: return to Main Menu
                    self.state_manager.change_state(State.MAIN_MENU)
                    self.scene_manager.switch_scene("menu")
                elif t.winner == t.player_team:
                    # Player won the final: Championship Ceremony!
                    self.state_manager.change_state(State.MAIN_MENU)
                    self.scene_manager.switch_scene("championship")
                else:
                    # Go back to bracket screen
                    self.state_manager.change_state(State.MAIN_MENU)
                    self.scene_manager.switch_scene("tournament_bracket", difficulty=self.difficulty)
                    
            elif mode_mgr.active_mode == "career" and mode_mgr.career:
                # Go to career hub screen
                self.state_manager.change_state(State.MAIN_MENU)
                self.scene_manager.switch_scene("career_hub", difficulty=self.difficulty)
                
        elif self.selected_index == 2:
            self._go_to_menu()

    def _go_to_menu(self) -> None:
        self.state_manager.change_state(State.SAVING)
        self.state_manager.change_state(State.MAIN_MENU)
        self.scene_manager.switch_scene("menu")

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((20, 24, 32))
        
        # Outcome Header
        font_res = self.asset_manager.get_font("default", 84)
        if self.winner == "player":
            msg = "VICTORY! 🏆"
            color = (255, 215, 0)
        else:
            msg = "DEFEAT"
            color = (220, 60, 60)
            
        res_surf = font_res.render(msg, True, color)
        res_rect = res_surf.get_rect(center=(screen.get_width() // 2, 130))
        screen.blit(res_surf, res_rect)

        # Final Score
        font_sc = self.asset_manager.get_font("default", 48)
        sc_surf = font_sc.render(f"{self.selected_team} {self.player_score} - {self.opponent_score} OPPONENT", True, (255, 255, 255))
        sc_rect = sc_surf.get_rect(center=(screen.get_width() // 2, 220))
        screen.blit(sc_surf, sc_rect)

        # Options
        font_opt = self.asset_manager.get_font("default", 32)
        for idx, option in enumerate(self.options):
            col = (255, 255, 255) if idx == self.selected_index else (130, 140, 150)
            prefix = "> " if idx == self.selected_index else "  "
            opt_surf = font_opt.render(prefix + option, True, col)
            opt_rect = opt_surf.get_rect(center=(screen.get_width() // 2, 350 + idx * 60))
            screen.blit(opt_surf, opt_rect)

        # Hint
        font_help = self.asset_manager.get_font("default", 20)
        help_surf = font_help.render("UP/DOWN or W/S to navigate, ENTER to select. ESC for menu.", True, (150, 150, 150))
        help_rect = help_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40))
        screen.blit(help_surf, help_rect)

import pygame
from typing import Any
from scenes.base import Scene
from core.state_manager import State

class ExitConfirmScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.options = ["YES", "NO"]
        self.selected_index = 1  # Default to NO for safety
        self.target_action = "quit"  # "quit" or "menu"
        self.origin_scene = "pause"

    def on_enter(self, **kwargs: Any) -> None:
        self.selected_index = 1
        self.target_action = kwargs.get("target_action", "quit")
        self.origin_scene = kwargs.get("origin_scene", "pause")

    def handle_event(self, event: pygame.event.Event) -> None:
        audio_mgr = getattr(self.scene_manager, "audio_manager", None)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w):
                if self.selected_index != 0:
                    self.selected_index = 0
                    if audio_mgr:
                        audio_mgr.play_sfx("hover")
            elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s):
                if self.selected_index != 1:
                    self.selected_index = 1
                    if audio_mgr:
                        audio_mgr.play_sfx("hover")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self._confirm()
            elif event.key == pygame.K_ESCAPE:
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self._cancel()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            screen_w = 1280
            if pygame.Rect(screen_w // 2 - 200, 335, 180, 50).collidepoint(m_pos):
                self.selected_index = 0
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self._confirm()
            elif pygame.Rect(screen_w // 2 + 20, 335, 180, 50).collidepoint(m_pos):
                self.selected_index = 1
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self._confirm()

    def _confirm(self) -> None:
        if self.selected_index == 0:
            # YES clicked
            if self.target_action == "quit":
                self.state_manager.change_state(State.EXIT)
            elif self.target_action == "menu":
                mode_mgr = self.scene_manager.mode_manager
                if self.origin_scene == "tournament_bracket":
                    mode_mgr.tournament = None
                    save_mgr = self.scene_manager.save_manager
                    if save_mgr:
                        save_mgr.save_tournament(None)
                self.state_manager.change_state(State.MAIN_MENU)
                self.scene_manager.switch_scene("menu")
        else:
            # NO clicked
            self._cancel()

    def _cancel(self) -> None:
        if self.target_action == "quit":
            self.scene_manager.switch_scene("menu")
        elif self.target_action == "menu":
            self.scene_manager.switch_scene(self.origin_scene)

    def render(self, screen: pygame.Surface) -> None:
        import math
        # Dark overlay
        wash = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        wash.fill((10, 12, 16, 230))
        screen.blit(wash, (0, 0))

        font_title = self.asset_manager.get_font("default", 48)
        if self.target_action == "quit":
            prompt = "ARE YOU SURE YOU WANT TO QUIT?"
        else:
            prompt = "QUIT MATCH AND RETURN TO MENU?"
            
        title_surf = font_title.render(prompt, True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 220))
        screen.blit(title_surf, title_rect)

        # Buttons
        font_opt = self.asset_manager.get_font("default", 36)
        
        # YES button
        is_yes = (self.selected_index == 0)
        yes_col = (255, 215, 0) if is_yes else (120, 130, 140)
        yes_offset = int(6 * math.sin(pygame.time.get_ticks() * 0.008)) if is_yes else 0
        yes_prefix = "▶ " if is_yes else "  "
        
        if is_yes:
            box_rect = pygame.Rect(screen.get_width() // 2 - 200 + yes_offset, 335, 180, 50)
            pygame.draw.rect(screen, (50, 60, 75), box_rect, border_radius=6)
            pygame.draw.rect(screen, (255, 215, 0), box_rect, width=2, border_radius=6)
            
        yes_surf = font_opt.render(yes_prefix + "YES", True, yes_col)
        yes_rect = yes_surf.get_rect(center=(screen.get_width() // 2 - 110 + yes_offset, 360))
        screen.blit(yes_surf, yes_rect)

        # NO button
        is_no = (self.selected_index == 1)
        no_col = (255, 215, 0) if is_no else (120, 130, 140)
        no_offset = int(6 * math.sin(pygame.time.get_ticks() * 0.008)) if is_no else 0
        no_prefix = "▶ " if is_no else "  "
        
        if is_no:
            box_rect = pygame.Rect(screen.get_width() // 2 + 20 + no_offset, 335, 180, 50)
            pygame.draw.rect(screen, (50, 60, 75), box_rect, border_radius=6)
            pygame.draw.rect(screen, (255, 215, 0), box_rect, width=2, border_radius=6)
            
        no_surf = font_opt.render(no_prefix + "NO", True, no_col)
        no_rect = no_surf.get_rect(center=(screen.get_width() // 2 + 110 + no_offset, 360))
        screen.blit(no_surf, no_rect)

        font_help = self.asset_manager.get_font("default", 20)
        help_surf = font_help.render("LEFT/RIGHT to select, ENTER to confirm. ESC to cancel.", True, (150, 150, 150))
        help_rect = help_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40))
        screen.blit(help_surf, help_rect)

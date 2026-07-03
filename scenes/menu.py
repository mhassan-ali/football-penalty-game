import pygame
from typing import Any
from scenes.base import Scene
from core.state_manager import State

class MenuScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.options = ["PLAY GAME", "SETTINGS", "STATISTICS", "ACHIEVEMENTS", "CREDITS", "QUIT"]
        self.selected_index = 0

    def on_enter(self, **kwargs: Any) -> None:
        self.selected_index = 0
        if self.state_manager.current_state != State.MAIN_MENU:
            self.state_manager.change_state(State.MAIN_MENU)
            
        audio_mgr = getattr(self.scene_manager, "audio_manager", None)
        if audio_mgr:
            audio_mgr.play_music()

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
                self.scene_manager.switch_scene("exit_confirm", target_action="quit")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            screen_w = 1280
            for idx in range(len(self.options)):
                rect = pygame.Rect(screen_w // 2 - 200, 210 + idx * 55, 400, 45)
                if rect.collidepoint(m_pos):
                    self.selected_index = idx
                    if audio_mgr:
                        audio_mgr.play_sfx("click")
                    self._select_option()

    def _select_option(self) -> None:
        if self.selected_index == 0:
            self.scene_manager.switch_scene("mode_select")
        elif self.selected_index == 1:
            self.scene_manager.switch_scene("settings", origin_scene="menu")
        elif self.selected_index == 2:
            self.scene_manager.switch_scene("statistics", origin_scene="menu")
        elif self.selected_index == 3:
            self.scene_manager.switch_scene("achievements")
        elif self.selected_index == 4:
            self.scene_manager.switch_scene("credits")
        elif self.selected_index == 5:
            self.scene_manager.switch_scene("exit_confirm", target_action="quit")

    def render(self, screen: pygame.Surface) -> None:
        import math
        screen.fill((30, 34, 42))
        
        font_title = self.asset_manager.get_font("default", 64)
        title_surf = font_title.render("MAIN MENU", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 140))
        screen.blit(title_surf, title_rect)

        font_opt = self.asset_manager.get_font("default", 32)
        for idx, option in enumerate(self.options):
            is_sel = (idx == self.selected_index)
            color = (255, 215, 0) if is_sel else (140, 150, 165)
            
            # Slide pulse animation
            x_offset = int(6 * math.sin(pygame.time.get_ticks() * 0.008)) if is_sel else 0
            prefix = "▶ " if is_sel else "  "
            
            if is_sel:
                box_rect = pygame.Rect(screen.get_width() // 2 - 220 + x_offset, 205 + idx * 55, 440, 45)
                pygame.draw.rect(screen, (50, 60, 75), box_rect, border_radius=6)
                pygame.draw.rect(screen, (255, 215, 0), box_rect, width=2, border_radius=6)
                
            opt_surf = font_opt.render(prefix + option, True, color)
            opt_rect = opt_surf.get_rect(center=(screen.get_width() // 2 + x_offset, 227 + idx * 55))
            screen.blit(opt_surf, opt_rect)

        font_help = self.asset_manager.get_font("default", 20)
        help_surf = font_help.render("UP/DOWN or W/S to navigate, ENTER to select. ESC to quit.", True, (150, 150, 150))
        help_rect = help_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
        screen.blit(help_surf, help_rect)

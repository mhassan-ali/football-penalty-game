import pygame
from typing import Any
from scenes.base import Scene

class SettingsScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.options = ["MASTER VOLUME", "MUSIC VOLUME", "SFX VOLUME", "BACK"]
        self.volumes = [100, 80, 90]
        self.selected_index = 0
        self.origin_scene = "menu"

    def on_enter(self, **kwargs: Any) -> None:
        self.selected_index = 0
        self.origin_scene = kwargs.get("origin_scene", "menu")
        save_mgr = self.scene_manager.save_manager
        if save_mgr:
            self.volumes[0] = int(save_mgr.data["settings"]["master_volume"] * 100)
            self.volumes[1] = int(save_mgr.data["settings"]["music_volume"] * 100)
            self.volumes[2] = int(save_mgr.data["settings"]["sfx_volume"] * 100)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._adjust_volume(-10)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._adjust_volume(10)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selected_index == 3:
                    self._go_back()
            elif event.key == pygame.K_ESCAPE:
                self._go_back()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            screen_w = 1280
            for idx in range(len(self.options)):
                rect = pygame.Rect(screen_w // 2 - 200, 240 + idx * 65, 400, 50)
                if rect.collidepoint(m_pos):
                    self.selected_index = idx
                    if idx == 3:
                        self._go_back()

    def _adjust_volume(self, delta: int) -> None:
        if self.selected_index < 3:
            curr = self.volumes[self.selected_index]
            self.volumes[self.selected_index] = max(0, min(100, curr + delta))
            
            save_mgr = self.scene_manager.save_manager
            if save_mgr:
                keys = ["master_volume", "music_volume", "sfx_volume"]
                key = keys[self.selected_index]
                val = self.volumes[self.selected_index] / 100.0
                save_mgr.update_setting(key, val)

    def _go_back(self) -> None:
        # Return to origin scene (menu or pause)
        self.scene_manager.switch_scene(self.origin_scene)

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((30, 34, 42))
        
        font_title = self.asset_manager.get_font("default", 54)
        title_surf = font_title.render("SETTINGS", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 120))
        screen.blit(title_surf, title_rect)

        font_opt = self.asset_manager.get_font("default", 32)
        for idx, option in enumerate(self.options):
            color = (255, 255, 255) if idx == self.selected_index else (130, 140, 150)
            prefix = "> " if idx == self.selected_index else "  "
            
            if idx < 3:
                val_str = f"<{self.volumes[idx]}%>"
                label_str = f"{prefix}{option.ljust(15)} {val_str}"
            else:
                label_str = f"{prefix}{option}"

            opt_surf = font_opt.render(label_str, True, color)
            opt_rect = opt_surf.get_rect(center=(screen.get_width() // 2, 250 + idx * 65))
            screen.blit(opt_surf, opt_rect)

        font_help = self.asset_manager.get_font("default", 20)
        help_surf = font_help.render("UP/DOWN to select, LEFT/RIGHT to adjust. ESC/ENTER to go back.", True, (150, 150, 150))
        help_rect = help_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40))
        screen.blit(help_surf, help_rect)

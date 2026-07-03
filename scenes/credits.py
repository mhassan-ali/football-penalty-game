import pygame
from typing import Any
from scenes.base import Scene

class CreditsScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            audio_mgr = getattr(self.scene_manager, "audio_manager", None)
            if audio_mgr:
                audio_mgr.play_sfx("click")
            self.scene_manager.switch_scene("menu")

    def render(self, screen: pygame.Surface) -> None:
        import math
        screen.fill((30, 34, 42))
        
        font_title = self.asset_manager.get_font("default", 54)
        title_surf = font_title.render("CREDITS", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 120))
        screen.blit(title_surf, title_rect)

        credits_lines = [
            ("GAME ENGINE & ARCHITECTURE", (240, 240, 240)),
            ("Python 3.12 + Pygame 2.6", (180, 190, 200)),
            ("", (0,0,0)),
            ("DEVELOPMENT & DESIGN", (240, 240, 240)),
            ("Product Engineering Team", (180, 190, 200)),
            ("", (0,0,0)),
            ("SPECIAL THANKS", (240, 240, 240)),
            ("Portfolio Reviewers & Community", (180, 190, 200))
        ]

        font_text = self.asset_manager.get_font("default", 24)
        for idx, (line, col) in enumerate(credits_lines):
            if not line:
                continue
            txt_surf = font_text.render(line, True, col)
            txt_rect = txt_surf.get_rect(center=(screen.get_width() // 2, 220 + idx * 40))
            screen.blit(txt_surf, txt_rect)

        font_help = self.asset_manager.get_font("default", 20)
        # Pulsing slide animation
        x_offset = int(6 * math.sin(pygame.time.get_ticks() * 0.008))
        help_surf = font_help.render("▶ Press any key or click to return to Main Menu.", True, (255, 215, 0))
        help_rect = help_surf.get_rect(center=(screen.get_width() // 2 + x_offset, screen.get_height() - 40))
        screen.blit(help_surf, help_rect)

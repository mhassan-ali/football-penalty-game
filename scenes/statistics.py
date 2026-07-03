import pygame
from typing import Any
from scenes.base import Scene

class StatisticsScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.origin_scene = "menu"

    def on_enter(self, **kwargs: Any) -> None:
        self.origin_scene = kwargs.get("origin_scene", "menu")

    def handle_event(self, event: pygame.event.Event) -> None:
        audio_mgr = getattr(self.scene_manager, "audio_manager", None)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self._go_back()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check back button
            width = 1280
            rect = pygame.Rect(width // 2 - 100, 620, 200, 45)
            if rect.collidepoint(event.pos):
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self._go_back()

    def _go_back(self) -> None:
        self.scene_manager.switch_scene(self.origin_scene)

    def render(self, screen: pygame.Surface) -> None:
        import math
        screen.fill((30, 34, 42))
        width = screen.get_width()
        
        font_title = self.asset_manager.get_font("default", 54)
        title_surf = font_title.render("STATISTICS", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(width // 2, 80))
        screen.blit(title_surf, title_rect)

        save_mgr = self.scene_manager.save_manager
        stats = {
            "matches_played": 0,
            "matches_won": 0,
            "goals_scored": 0,
            "saves_made": 0,
            "tournaments_played": 0,
            "tournaments_won": 0,
            "careers_played": 0,
            "careers_completed": 0
        }
        if save_mgr:
            stats.update(save_mgr.data.get("statistics", {}))

        played = stats["matches_played"]
        won = stats["matches_won"]
        win_rate = (won / played * 100) if played > 0 else 0.0

        stat_lines = [
            ("Matches Played", str(played)),
            ("Matches Won", str(won)),
            ("Win Rate", f"{win_rate:.1f}%"),
            ("Goals Scored", str(stats["goals_scored"])),
            ("Saves Made", str(stats["saves_made"])),
            ("Tournaments Played", str(stats["tournaments_played"])),
            ("Tournaments Won", str(stats["tournaments_won"])),
            ("Careers Played", str(stats["careers_played"])),
            ("Careers Completed", str(stats["careers_completed"]))
        ]

        font_label = self.asset_manager.get_font("default", 24)
        font_val = self.asset_manager.get_font("default", 24)

        for idx, (label, val) in enumerate(stat_lines):
            y = 150 + idx * 45
            pygame.draw.line(screen, (50, 60, 75), (width // 2 - 250, y + 35), (width // 2 + 250, y + 35), 1)

            lbl_surf = font_label.render(label, True, (180, 190, 200))
            screen.blit(lbl_surf, (width // 2 - 240, y + 5))

            val_surf = font_val.render(val, True, (255, 255, 255))
            val_rect = val_surf.get_rect(right=width // 2 + 240, top=y + 5)
            screen.blit(val_surf, val_rect)

        # Back option (pulsing/sliding)
        x_offset = int(6 * math.sin(pygame.time.get_ticks() * 0.008))
        rect = pygame.Rect(width // 2 - 100 + x_offset, 620, 200, 45)
        pygame.draw.rect(screen, (50, 60, 75), rect, border_radius=6)
        pygame.draw.rect(screen, (255, 215, 0), rect, width=2, border_radius=6)

        font_btn = self.asset_manager.get_font("default", 20)
        btn_surf = font_btn.render("▶ BACK", True, (255, 215, 0))
        btn_rect = btn_surf.get_rect(center=rect.center)
        screen.blit(btn_surf, btn_rect)

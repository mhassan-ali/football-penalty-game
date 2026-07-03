import pygame
from typing import Any
from scenes.base import Scene

class AchievementsScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)

    def handle_event(self, event: pygame.event.Event) -> None:
        audio_mgr = getattr(self.scene_manager, "audio_manager", None)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self._go_back()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            width = 1280
            rect = pygame.Rect(width // 2 - 100, 620, 200, 45)
            if rect.collidepoint(event.pos):
                if audio_mgr:
                    audio_mgr.play_sfx("click")
                self._go_back()

    def _go_back(self) -> None:
        self.scene_manager.switch_scene("menu")

    def render(self, screen: pygame.Surface) -> None:
        import math
        screen.fill((30, 34, 42))
        width = screen.get_width()
        
        font_title = self.asset_manager.get_font("default", 54)
        title_surf = font_title.render("ACHIEVEMENTS", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(width // 2, 80))
        screen.blit(title_surf, title_rect)

        save_mgr = self.scene_manager.save_manager
        achievements_data = {}
        if save_mgr:
            achievements_data = save_mgr.data.get("achievements", {})

        # List of achievements metadata for display
        ach_meta = [
            {
                "key": "first_kick",
                "title": "First Kick",
                "desc": "Play your first match of Penalty Shootout."
            },
            {
                "key": "first_win",
                "title": "First Win",
                "desc": "Win your first penalty shootout match."
            },
            {
                "key": "goal_machine",
                "title": "Goal Machine",
                "desc": "Score a total of 50 goals across all matches."
            },
            {
                "key": "brick_wall",
                "title": "Brick Wall",
                "desc": "Make a total of 25 saves as goalkeeper."
            },
            {
                "key": "tournament_champion",
                "title": "Tournament Champion",
                "desc": "Win a full tournament bracket and trophy."
            },
            {
                "key": "career_legend",
                "title": "Career Legend",
                "desc": "Complete a full 10-match Career Mode season."
            },
            {
                "key": "perfect_shootout",
                "title": "Perfect Shootout",
                "desc": "Win a match 5-0 (score all 5, concede 0)."
            },
            {
                "key": "sharp_shooter",
                "title": "Sharp Shooter",
                "desc": "Score 5 goals in a single match."
            }
        ]

        font_name = self.asset_manager.get_font("default", 22)
        font_desc = self.asset_manager.get_font("default", 16)
        font_meta = self.asset_manager.get_font("default", 14)

        for idx, ach in enumerate(ach_meta):
            key = ach["key"]
            state = achievements_data.get(key, {"earned": False, "earned_date": ""})
            earned = state.get("earned", False)
            earned_date = state.get("earned_date", "")

            # Decide position (2 columns of 4 achievements)
            col = idx % 2
            row = idx // 2

            card_x = width // 2 - 500 if col == 0 else width // 2 + 20
            card_y = 150 + row * 105
            card_w, card_h = 480, 90

            # Draw card background
            bg_col = (40, 50, 65) if earned else (25, 29, 36)
            border_col = (255, 215, 0) if earned else (60, 70, 85)
            
            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
            pygame.draw.rect(screen, bg_col, card_rect, border_radius=6)
            pygame.draw.rect(screen, border_col, card_rect, width=2, border_radius=6)

            # Draw icon/badge placeholder on the left of card
            badge_rect = pygame.Rect(card_x + 15, card_y + 15, 60, 60)
            badge_color = (255, 215, 0) if earned else (80, 90, 100)
            pygame.draw.rect(screen, badge_color, badge_rect, border_radius=30)
            
            # Simple icon inside badge (star or lock)
            if earned:
                pygame.draw.polygon(screen, (30, 34, 42), [
                    (card_x + 45, card_y + 25),
                    (card_x + 51, card_y + 40),
                    (card_x + 65, card_y + 40),
                    (card_x + 54, card_y + 48),
                    (card_x + 59, card_y + 63),
                    (card_x + 45, card_y + 53),
                    (card_x + 31, card_y + 63),
                    (card_x + 36, card_y + 48),
                    (card_x + 25, card_y + 40),
                    (card_x + 39, card_y + 40)
                ])
            else:
                # Draw simple lock icon
                pygame.draw.rect(screen, (20, 24, 30), (card_x + 40, card_y + 45, 10, 10))
                pygame.draw.circle(screen, (20, 24, 30), (card_x + 45, card_y + 42), 6, width=2)

            # Render title
            title_col = (255, 255, 255) if earned else (140, 150, 160)
            t_surf = font_name.render(ach["title"], True, title_col)
            screen.blit(t_surf, (card_x + 90, card_y + 12))

            # Render desc
            desc_col = (200, 205, 215) if earned else (110, 115, 125)
            d_surf = font_desc.render(ach["desc"], True, desc_col)
            screen.blit(d_surf, (card_x + 90, card_y + 38))

            # Render progress or date
            if earned:
                date_str = f"Earned: {earned_date.split(' ')[0]}" if earned_date else "Earned"
                m_surf = font_meta.render(date_str, True, (0, 255, 150))
                screen.blit(m_surf, (card_x + 90, card_y + 62))
            elif "progress" in state:
                prog = state.get("progress", 0)
                target = state.get("target", 100)
                prog_str = f"Progress: {prog} / {target}"
                m_surf = font_meta.render(prog_str, True, (255, 165, 0))
                screen.blit(m_surf, (card_x + 90, card_y + 62))
            else:
                m_surf = font_meta.render("LOCKED", True, (150, 50, 50))
                screen.blit(m_surf, (card_x + 90, card_y + 62))

        # Pulsing/sliding Back button
        x_offset = int(6 * math.sin(pygame.time.get_ticks() * 0.008))
        rect = pygame.Rect(width // 2 - 100 + x_offset, 620, 200, 45)
        pygame.draw.rect(screen, (50, 60, 75), rect, border_radius=6)
        pygame.draw.rect(screen, (255, 215, 0), rect, width=2, border_radius=6)

        font_btn = self.asset_manager.get_font("default", 20)
        btn_surf = font_btn.render("▶ BACK", True, (255, 215, 0))
        btn_rect = btn_surf.get_rect(center=rect.center)
        screen.blit(btn_surf, btn_rect)

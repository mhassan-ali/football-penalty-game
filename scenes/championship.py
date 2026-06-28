import pygame
import math
from typing import Any
from scenes.base import Scene

class ChampionshipScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self._exit_to_menu()

    def _exit_to_menu(self) -> None:
        self.scene_manager.switch_scene("menu")

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((20, 24, 30))
        
        # Draw Trophy Symbol using vector shapes
        width = screen.get_width()
        height = screen.get_height()
        cx = width // 2
        cy = height // 2 - 50

        # Sine wave scale oscillation for pulsating glory
        pulse = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() * 0.005)
        
        # Gold colors
        gold = (255, 215, 0)
        dark_gold = (204, 163, 0)
        bronze = (191, 137, 112)

        # Draw cup body
        pygame.draw.polygon(screen, gold, [
            (cx - int(60 * pulse), cy - int(80 * pulse)),
            (cx + int(60 * pulse), cy - int(80 * pulse)),
            (cx + int(45 * pulse), cy + int(10 * pulse)),
            (cx - int(45 * pulse), cy + int(10 * pulse))
        ])

        # Draw handles (left & right circles/lines)
        pygame.draw.circle(screen, dark_gold, (cx - int(65 * pulse), cy - int(30 * pulse)), int(25 * pulse), width=int(6 * pulse))
        pygame.draw.circle(screen, dark_gold, (cx + int(65 * pulse), cy - int(30 * pulse)), int(25 * pulse), width=int(6 * pulse))
        
        # Re-cover with gold body to mask handles behind the cup
        pygame.draw.polygon(screen, gold, [
            (cx - int(58 * pulse), cy - int(78 * pulse)),
            (cx + int(58 * pulse), cy - int(78 * pulse)),
            (cx + int(43 * pulse), cy + int(8 * pulse)),
            (cx - int(43 * pulse), cy + int(8 * pulse))
        ])

        # Draw stand (stem & base)
        pygame.draw.rect(screen, dark_gold, (cx - int(10 * pulse), cy + int(10 * pulse), int(20 * pulse), int(40 * pulse)))
        pygame.draw.polygon(screen, bronze, [
            (cx - int(40 * pulse), cy + int(70 * pulse)),
            (cx + int(40 * pulse), cy + int(70 * pulse)),
            (cx + int(50 * pulse), cy + int(85 * pulse)),
            (cx - int(50 * pulse), cy + int(85 * pulse))
        ])

        # Celebratory texts
        font_champ = self.asset_manager.get_font("default", 64)
        c_surf = font_champ.render("CHAMPIONS!", True, gold)
        c_rect = c_surf.get_rect(center=(cx, cy + int(160 * pulse)))
        screen.blit(c_surf, c_rect)

        font_congrats = self.asset_manager.get_font("default", 28)
        congrats_surf = font_congrats.render("CONGRATULATIONS! YOU HAVE WON THE CUP!", True, (255, 255, 255))
        congrats_rect = congrats_surf.get_rect(center=(cx, cy + int(215 * pulse)))
        screen.blit(congrats_surf, congrats_rect)

        font_help = self.asset_manager.get_font("default", 22)
        help_surf = font_help.render("Press any key or click to return to Menu.", True, (150, 160, 170))
        help_rect = help_surf.get_rect(center=(cx, height - 50))
        screen.blit(help_surf, help_rect)

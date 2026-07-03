import pygame
from typing import Any
from scenes.base import Scene
from core.state_manager import State

class SplashScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.timer = 2.0  # display splash for 2 seconds
        self.skipped = False

    def on_enter(self, **kwargs: Any) -> None:
        self.timer = 2.0
        self.skipped = False
        if self.state_manager.current_state != State.LOADING:
            self.state_manager.change_state(State.LOADING)
            
        audio_mgr = getattr(self.scene_manager, "audio_manager", None)
        if audio_mgr:
            audio_mgr.play_sfx("whistle")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self._skip()

    def _skip(self) -> None:
        if self.skipped:
            return
        self.skipped = True
        self.state_manager.change_state(State.MAIN_MENU)
        self.scene_manager.switch_scene("menu")

    def update(self, dt: float) -> None:
        if self.skipped:
            return
        self.timer -= dt
        if self.timer <= 0:
            self._skip()

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((20, 24, 30))
        
        font = self.asset_manager.get_font("default", 54)
        text_surf = font.render("PENALTY SHOOTOUT", True, (255, 215, 0))
        text_rect = text_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 30))
        screen.blit(text_surf, text_rect)

        font_sub = self.asset_manager.get_font("default", 24)
        sub_text_surf = font_sub.render(f"Press any key or click to start ({max(0.0, self.timer):.1f}s)", True, (150, 160, 175))
        sub_text_rect = sub_text_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 40))
        screen.blit(sub_text_surf, sub_text_rect)

import pygame
from typing import Any
from scenes.base import Scene
from core.state_manager import State

class LoadingScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.timer = 1.0
        self.selected_team = "BRAZIL"
        self.difficulty = "medium"

    def on_enter(self, **kwargs: Any) -> None:
        self.timer = 1.0
        self.selected_team = kwargs.get("selected_team", "BRAZIL")
        self.difficulty = kwargs.get("difficulty", "medium")

    def update(self, dt: float) -> None:
        self.timer -= dt
        if self.timer <= 0:
            # Transition state to GAMEPLAY and switch scene to gameplay
            self.state_manager.change_state(State.GAMEPLAY)
            self.scene_manager.switch_scene("gameplay", selected_team=self.selected_team, difficulty=self.difficulty)

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((20, 24, 30))
        
        font_title = self.asset_manager.get_font("default", 48)
        title_surf = font_title.render("PREPARING MATCH...", True, (240, 240, 240))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 40))
        screen.blit(title_surf, title_rect)

        font_sub = self.asset_manager.get_font("default", 28)
        info_str = f"Team: {self.selected_team}  |  Difficulty: {self.difficulty.upper()}"
        sub_surf = font_sub.render(info_str, True, (255, 215, 0))
        sub_rect = sub_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 20))
        screen.blit(sub_surf, sub_rect)

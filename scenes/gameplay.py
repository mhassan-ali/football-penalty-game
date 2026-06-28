import pygame
import math
from typing import Any
from scenes.base import Scene
from core.state_manager import State
from game.entities import Goal, Ball, Goalkeeper

class GameplayScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.goal = Goal()
        self.ball = Ball()
        self.keeper = Goalkeeper()
        self.mode = "aiming"  # "aiming", "flight", "result"
        self.outcome = ""     # "GOAL", "SAVE", "MISS"
        self.result_timer = 0.0

    def on_enter(self, **kwargs: Any) -> None:
        self.ball.reset()
        self.keeper.reset()
        self.mode = "aiming"
        self.outcome = ""
        self.result_timer = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(State.MAIN_MENU)
                self.scene_manager.switch_scene("menu")
            elif self.mode == "result" and event.key == pygame.K_SPACE:
                self._reset_kick()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.mode == "aiming":
                # Shoot towards clicked position
                self.ball.shoot(event.pos)
                self.keeper.decide_dive()
                self.mode = "flight"
            elif self.mode == "result":
                self._reset_kick()

    def _reset_kick(self) -> None:
        self.ball.reset()
        self.keeper.reset()
        self.mode = "aiming"
        self.outcome = ""

    def update(self, dt: float) -> None:
        if self.mode == "flight":
            self.ball.update(dt)
            self.keeper.update(dt)
            
            if not self.ball.is_moving:
                # Ball has reached target. Calculate outcome.
                ball_center_x, ball_center_y = self.ball.pos.x, self.ball.pos.y
                
                # Check if ball center is within the goal rect
                is_in_goal = self.goal.rect.collidepoint(ball_center_x, ball_center_y)
                
                if not is_in_goal:
                    self.outcome = "MISS"
                else:
                    # Check collision between goalkeeper rect and ball rect
                    if self.keeper.rect.colliderect(self.ball.rect):
                        self.outcome = "SAVE"
                    else:
                        self.outcome = "GOAL"
                
                self.result_timer = 2.5
                self.mode = "result"
                
                # Publish outcome event
                if self.state_manager and hasattr(self.state_manager, "_event_manager"):
                    self.state_manager._event_manager.publish("penalty_concluded", {"outcome": self.outcome})

        elif self.mode == "result":
            self.result_timer -= dt
            if self.result_timer <= 0:
                self._reset_kick()

    def render(self, screen: pygame.Surface) -> None:
        width = screen.get_width()
        height = screen.get_height()
        
        # 1. Draw Sky/Stadium Background (night time dark blue/grey)
        screen.fill((20, 26, 36))
        
        # Draw stadium floodlights (white circles with glowing yellow borders)
        pygame.draw.circle(screen, (50, 50, 60), (150, 50), 30)
        pygame.draw.circle(screen, (255, 255, 200), (150, 50), 20)
        pygame.draw.circle(screen, (50, 50, 60), (width - 150, 50), 30)
        pygame.draw.circle(screen, (255, 255, 200), (width - 150, 50), 20)
        
        # 2. Draw Pitch (Green bands for premium mowed lawn effect)
        pitch_y_start = 400
        pygame.draw.rect(screen, (34, 139, 34), (0, pitch_y_start, width, height - pitch_y_start))
        
        # Draw green lawn bands
        band_height = 40
        for y in range(pitch_y_start, height, band_height * 2):
            pygame.draw.rect(screen, (40, 160, 40), (0, y, width, band_height))
            
        # Draw penalty spot
        pygame.draw.circle(screen, (255, 255, 255), (640, 600), 6)
        
        # 3. Draw Goal Area Net
        goal_rect = self.goal.rect
        # Draw net mesh inside goal rect
        net_color = (60, 70, 80)
        # Vertical net lines
        for x in range(goal_rect.left, goal_rect.right + 1, 20):
            pygame.draw.line(screen, net_color, (x, goal_rect.top), (x, goal_rect.bottom), 1)
        # Horizontal net lines
        for y in range(goal_rect.top, goal_rect.bottom + 1, 20):
            pygame.draw.line(screen, net_color, (goal_rect.left, y), (goal_rect.right, y), 1)
            
        # Draw goal posts (thick white borders)
        post_color = (255, 255, 255)
        post_thickness = 10
        # Left post
        pygame.draw.line(screen, post_color, (goal_rect.left, goal_rect.top), (goal_rect.left, goal_rect.bottom), post_thickness)
        # Right post
        pygame.draw.line(screen, post_color, (goal_rect.right, goal_rect.top), (goal_rect.right, goal_rect.bottom), post_thickness)
        # Crossbar
        pygame.draw.line(screen, post_color, (goal_rect.left - 4, goal_rect.top), (goal_rect.right + 4, goal_rect.top), post_thickness)

        # 4. Draw Goalkeeper
        keeper_rect = self.keeper.rect
        # Base body rect (blue kit)
        pygame.draw.rect(screen, (0, 102, 204), keeper_rect, border_radius=4)
        pygame.draw.rect(screen, (0, 76, 153), keeper_rect, width=2, border_radius=4)  # border
        
        # Draw goalkeeper head and gloves based on dive state orientation
        head_color = (255, 218, 185)  # peachskin tone
        glove_color = (255, 69, 0)   # orange gloves
        
        if self.keeper.state in ("diving_left", "diving_right"):
            # Horizontal keeper shape
            # Swap Head and Glove placements
            if self.keeper.state == "diving_left":
                head_pos = (keeper_rect.left + 25, keeper_rect.centery)
                left_glove = (keeper_rect.left + 5, keeper_rect.centery - 15)
                right_glove = (keeper_rect.left + 5, keeper_rect.centery + 15)
            else:
                head_pos = (keeper_rect.right - 25, keeper_rect.centery)
                left_glove = (keeper_rect.right - 5, keeper_rect.centery - 15)
                right_glove = (keeper_rect.right - 5, keeper_rect.centery + 15)
                
            pygame.draw.circle(screen, head_color, head_pos, 16)
            pygame.draw.circle(screen, glove_color, left_glove, 10)
            pygame.draw.circle(screen, glove_color, right_glove, 10)
        else:
            # Standing vertical keeper shape
            head_pos = (keeper_rect.centerx, keeper_rect.top + 20)
            left_glove = (keeper_rect.left - 10, keeper_rect.top + 45)
            right_glove = (keeper_rect.right + 10, keeper_rect.top + 45)
            
            pygame.draw.circle(screen, head_color, head_pos, 16)
            pygame.draw.circle(screen, glove_color, left_glove, 10)
            pygame.draw.circle(screen, glove_color, right_glove, 10)
            
            # Draw connection line representing arms
            pygame.draw.line(screen, (0, 102, 204), (keeper_rect.left, keeper_rect.top + 40), left_glove, 6)
            pygame.draw.line(screen, (0, 102, 204), (keeper_rect.right, keeper_rect.top + 40), right_glove, 6)

        # 5. Draw Football (White with soccer ball patterns)
        ball_pos_x = int(self.ball.pos.x)
        ball_pos_y = int(self.ball.pos.y)
        pygame.draw.circle(screen, (255, 255, 255), (ball_pos_x, ball_pos_y), self.ball.radius)
        pygame.draw.circle(screen, (0, 0, 0), (ball_pos_x, ball_pos_y), self.ball.radius, 1)  # outline
        
        # Soccer ball details
        pygame.draw.circle(screen, (20, 20, 20), (ball_pos_x, ball_pos_y), 4)
        for angle in (0, 72, 144, 216, 288):
            rad = math.radians(angle)
            end_x = ball_pos_x + int(math.cos(rad) * self.ball.radius)
            end_y = ball_pos_y + int(math.sin(rad) * self.ball.radius)
            pygame.draw.line(screen, (20, 20, 20), (ball_pos_x, ball_pos_y), (end_x, end_y), 1)

        # 6. Draw Reticle in AIMING mode
        if self.mode == "aiming":
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.circle(screen, (255, 0, 0), mouse_pos, 18, 2)
            pygame.draw.circle(screen, (255, 0, 0), mouse_pos, 2)
            pygame.draw.line(screen, (255, 0, 0), (640, 600), mouse_pos, 1)

        # 7. Draw HUD Instructions
        font_inst = self.asset_manager.get_font("default", 20)
        inst_surf = font_inst.render("ESC: Menu  |  Aim with mouse, CLICK to take penalty", True, (200, 210, 220))
        inst_rect = inst_surf.get_rect(topleft=(20, 20))
        screen.blit(inst_surf, inst_rect)

        # 8. Draw Result Overlay
        if self.mode == "result":
            # Semi-transparent wash
            wash = pygame.Surface((width, height), pygame.SRCALPHA)
            wash.fill((10, 10, 15, 180))
            screen.blit(wash, (0, 0))
            
            # Outcome text
            font_res = self.asset_manager.get_font("default", 90)
            if self.outcome == "GOAL":
                msg = "GOAL!"
                color = (0, 255, 100)
            elif self.outcome == "SAVE":
                msg = "SAVED!"
                color = (0, 153, 255)
            else:
                msg = "MISSED!"
                color = (255, 51, 51)
                
            res_surf = font_res.render(msg, True, color)
            res_rect = res_surf.get_rect(center=(width // 2, height // 2 - 40))
            screen.blit(res_surf, res_rect)
            
            # Subtext
            font_sub = self.asset_manager.get_font("default", 24)
            sub_surf = font_sub.render("Click or press SPACE to take another kick", True, (240, 240, 240))
            sub_rect = sub_surf.get_rect(center=(width // 2, height // 2 + 50))
            screen.blit(sub_surf, sub_rect)

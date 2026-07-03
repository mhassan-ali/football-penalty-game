import pygame
import math
import random
from typing import Any, Tuple, Optional
from scenes.base import Scene
from core.state_manager import State
from game.entities import Goal, Ball, Goalkeeper, decide_ai_shot
from game.shootout import Shootout

class GameplayScene(Scene):
    def __init__(self, name: str, state_manager: Any, scene_manager: Any, asset_manager: Any) -> None:
        super().__init__(name, state_manager, scene_manager, asset_manager)
        self.goal = Goal()
        self.ball = Ball()
        self.keeper = Goalkeeper()
        self.shootout = Shootout()
        
        self.selected_team = "BRAZIL"
        self.opponent = "OPPONENT"
        self.difficulty = "medium"
        self.mode = "aiming"
        self.outcome = ""
        
        self.shot_power = 0.0
        self.power_charging = False
        
        self.is_replay_flight = False
        self.last_ball_target: Tuple[float, float] = (0.0, 0.0)
        self.last_ball_speed = 0.0
        self.last_keeper_dive = "stay_center"
        self.last_keeper_dive_speed = 700.0
        
        self.result_timer = 0.0
        self.aim_target: Tuple[float, float] = (640.0, 350.0)

    def on_enter(self, **kwargs: Any) -> None:
        # Check if resuming from pause
        if kwargs.get("is_resume"):
            return

        if "selected_team" in kwargs:
            self.selected_team = kwargs["selected_team"]
        if "opponent" in kwargs:
            self.opponent = kwargs["opponent"]
        if "difficulty" in kwargs:
            self.difficulty = kwargs["difficulty"]

        self.shootout.reset()
        self._reset_attempt()
        self.mode = "aiming"
        self.camera_shake = 0.0

        audio_mgr = getattr(self.scene_manager, "audio_manager", None)
        if audio_mgr:
            audio_mgr.stop_music()
            audio_mgr.play_ambience()
            audio_mgr.play_sfx("whistle")

    def _reset_attempt(self) -> None:
        self.ball.reset()
        self.keeper.reset()
        self.shot_power = 0.0
        self.power_charging = False
        self.is_replay_flight = False
        self.outcome = ""

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Open Pause Scene
                self.state_manager.change_state(State.PAUSED)
                self.scene_manager.switch_scene("pause")
                
            elif event.key == pygame.K_F1:
                self.difficulty = "easy"
            elif event.key == pygame.K_F2:
                self.difficulty = "medium"
            elif event.key == pygame.K_F3:
                self.difficulty = "hard"
                
            elif self.mode == "result" and event.key == pygame.K_SPACE:
                self._advance_after_result()
                
            elif self.mode == "defending_aim":
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self._execute_defense("diving_left")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self._execute_defense("stay_center")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self._execute_defense("diving_right")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.mode == "aiming":
                self.power_charging = True
                self.shot_power = 0.0
                self.aim_target = event.pos
            elif self.mode == "defending_aim":
                dive = self._get_clicked_defense_zone(event.pos)
                if dive:
                    self._execute_defense(dive)
            elif self.mode == "result":
                self._advance_after_result()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.mode == "aiming" and self.power_charging:
                self._execute_player_shot()

    def _get_clicked_defense_zone(self, pos: Tuple[int, int]) -> Optional[str]:
        x, y = pos
        if 200 <= y <= 500:
            if 340 <= x < 540:
                return "diving_left"
            elif 540 <= x < 740:
                return "stay_center"
            elif 740 <= x <= 940:
                return "diving_right"
        return None

    def _execute_player_shot(self) -> None:
        self.power_charging = False
        speed = 600.0 + self.shot_power * 8.0
        
        target_x, target_y = self.aim_target
        if self.shot_power > 90.0:
            overpower_ratio = (self.shot_power - 90.0)
            target_y -= overpower_ratio * 6.5
            target_x += random.uniform(-overpower_ratio * 4.0, overpower_ratio * 4.0)

        keeper_dive = self.keeper.decide_dive(target_x, self.difficulty)
        
        self.last_ball_target = (target_x, target_y)
        self.last_ball_speed = speed
        self.last_keeper_dive = keeper_dive
        self.last_keeper_dive_speed = self.keeper.dive_speed
        
        self.ball.shoot((target_x, target_y), speed)
        audio_mgr = getattr(self.scene_manager, "audio_manager", None)
        if audio_mgr:
            audio_mgr.play_sfx("kick")
        self.is_replay_flight = False
        self.mode = "flight"

    def _execute_defense(self, player_dive: str) -> None:
        self.keeper.commit_to_dive_state(player_dive)
        
        ai_target = decide_ai_shot(self.difficulty)
        ai_speed = random.uniform(700.0, 1100.0)
        
        self.last_ball_target = ai_target
        self.last_ball_speed = ai_speed
        self.last_keeper_dive = player_dive
        self.last_keeper_dive_speed = self.keeper.dive_speed
        
        self.ball.shoot(ai_target, ai_speed)
        audio_mgr = getattr(self.scene_manager, "audio_manager", None)
        if audio_mgr:
            audio_mgr.play_sfx("kick")
        self.is_replay_flight = False
        self.mode = "flight"

    def _advance_after_result(self) -> None:
        if self.shootout.is_over:
            # Transition to Results Scene
            audio_mgr = getattr(self.scene_manager, "audio_manager", None)
            if audio_mgr:
                audio_mgr.play_sfx("whistle")
                audio_mgr.stop_ambience()
                audio_mgr.play_music()
            self.state_manager.change_state(State.RESULT)
            self.scene_manager.switch_scene(
                "results", 
                winner=self.shootout.winner,
                player_score=self.shootout.player_score,
                opponent_score=self.shootout.opponent_score,
                selected_team=self.selected_team,
                difficulty=self.difficulty,
                player_saves=self.shootout.opponent_kicks.count("save")
            )
        else:
            self._reset_attempt()
            if self.shootout.current_turn == "player":
                self.mode = "aiming"
            else:
                self.mode = "defending_aim"

    def update(self, dt: float) -> None:
        if getattr(self, "camera_shake", 0) > 0:
            self.camera_shake = max(0.0, self.camera_shake - dt * 25.0)

        if self.mode == "aiming" and self.power_charging:
            self.shot_power += dt * 95.0
            if self.shot_power >= 100.0:
                self.shot_power = 100.0
                self._execute_player_shot()
                return

        if self.mode == "flight":
            sim_dt = dt * 0.35 if self.is_replay_flight else dt
            self.ball.update(sim_dt)
            self.keeper.update(sim_dt)
            
            if not self.ball.is_moving:
                if self.is_replay_flight:
                    self.shootout.record_outcome(self.outcome)
                    self.is_replay_flight = False
                    self.result_timer = 2.0
                    self.mode = "result"
                else:
                    ball_x, ball_y = self.ball.pos.x, self.ball.pos.y
                    is_in_goal = self.goal.rect.collidepoint(ball_x, ball_y)
                    
                    audio_mgr = getattr(self.scene_manager, "audio_manager", None)
                    if not is_in_goal:
                        self.outcome = "MISS"
                        if audio_mgr:
                            audio_mgr.play_sfx("hover")
                    else:
                        if self.keeper.rect.colliderect(self.ball.rect):
                            self.outcome = "SAVE"
                            if audio_mgr:
                                audio_mgr.play_sfx("save")
                        else:
                            self.outcome = "GOAL"
                            self.camera_shake = 12.0
                            if audio_mgr:
                                audio_mgr.play_sfx("goal")
                    
                    if self.outcome == "GOAL":
                        self.is_replay_flight = True
                        self.ball.reset()
                        self.keeper.reset()
                        self.keeper.commit_to_dive_state(self.last_keeper_dive)
                        self.keeper.dive_speed = self.last_keeper_dive_speed
                        self.ball.shoot(self.last_ball_target, self.last_ball_speed)
                    else:
                        self.shootout.record_outcome(self.outcome)
                        self.result_timer = 2.0
                        self.mode = "result"

        elif self.mode == "result":
            self.result_timer -= dt
            if self.result_timer <= 0:
                self._advance_after_result()

    def _draw_flag_procedural(self, screen: pygame.Surface, x: int, y: int, w: int, h: int, country: str) -> None:
        country = country.upper()
        pygame.draw.rect(screen, (20, 24, 30), (x, y, w, h))
        pygame.draw.rect(screen, (60, 70, 80), (x, y, w, h), 1)
        
        if "BRAZIL" in country:
            pygame.draw.rect(screen, (0, 156, 59), (x + 1, y + 1, w - 2, h - 2))
            # Yellow diamond
            pygame.draw.polygon(screen, (255, 223, 0), [
                (x + w // 2, y + 2),
                (x + w - 3, y + h // 2),
                (x + w // 2, y + h - 2),
                (x + 3, y + h // 2)
            ])
            # Blue circle
            pygame.draw.circle(screen, (0, 34, 108), (x + w // 2, y + h // 2), h // 5)
        elif "ARGENTINA" in country:
            pygame.draw.rect(screen, (116, 172, 223), (x + 1, y + 1, w - 2, h - 2))
            pygame.draw.rect(screen, (255, 255, 255), (x + 1, y + h // 3, w - 2, h // 3))
            pygame.draw.circle(screen, (246, 180, 14), (x + w // 2, y + h // 2), h // 7)
        elif "GERMANY" in country:
            pygame.draw.rect(screen, (0, 0, 0), (x + 1, y + 1, w - 2, h // 3))
            pygame.draw.rect(screen, (221, 0, 0), (x + 1, y + h // 3, w - 2, h // 3))
            pygame.draw.rect(screen, (255, 204, 0), (x + 1, y + 2 * h // 3, w - 2, h // 3 - 1))
        elif "FRANCE" in country:
            pygame.draw.rect(screen, (0, 35, 125), (x + 1, y + 1, w // 3, h - 2))
            pygame.draw.rect(screen, (255, 255, 255), (x + w // 3, y + 1, w // 3, h - 2))
            pygame.draw.rect(screen, (239, 65, 53), (x + 2 * w // 3, y + 1, w // 3 - 1, h - 2))
        elif "ENGLAND" in country:
            pygame.draw.rect(screen, (255, 255, 255), (x + 1, y + 1, w - 2, h - 2))
            pygame.draw.rect(screen, (207, 20, 43), (x + w // 2 - 2, y + 1, 4, h - 2))
            pygame.draw.rect(screen, (207, 20, 43), (x + 1, y + h // 2 - 2, w - 2, 4))
        elif "SPAIN" in country:
            pygame.draw.rect(screen, (170, 21, 27), (x + 1, y + 1, w - 2, h - 2))
            pygame.draw.rect(screen, (241, 191, 0), (x + 1, y + h // 4, w - 2, h // 2))
        else:
            # Generic opponent
            pygame.draw.rect(screen, (130, 140, 150), (x + 1, y + 1, w - 2, h - 2))
            pygame.draw.rect(screen, (170, 180, 190), (x + w // 2, y + 1, w // 2 - 1, h - 2))

    def _draw_keeper_procedural(self, screen: pygame.Surface, x: float, y: float, state: str, ticks: int) -> None:
        jersey_col = (180, 255, 0)      # Neon Yellow/Green
        shorts_col = (35, 38, 45)       # Dark Grey
        skin_col = (245, 200, 170)      # Skin tone
        glove_col = (255, 80, 0)        # Bright Orange
        hair_col = (85, 50, 30)         # Brown hair
        sock_col = (220, 220, 220)      # White socks
        shoe_col = (20, 20, 25)

        if state in ("diving_left", "diving_right"):
            is_left = (state == "diving_left")
            sign = -1 if is_left else 1
            cy = y - 35
            
            # Head
            pygame.draw.circle(screen, skin_col, (int(x + 36 * sign), int(cy)), 11)
            pygame.draw.rect(screen, hair_col, (int(x + 36 * sign - 9), int(cy - 12), 18, 6), border_radius=2)
            
            # Torso / Jersey
            pygame.draw.rect(screen, jersey_col, (int(x - 22 if is_left else x - 13), int(cy - 13), 35, 26), border_radius=4)
            
            # Shorts
            pygame.draw.rect(screen, shorts_col, (int(x + 13 if is_left else x - 28), int(cy - 13), 15, 26), border_radius=2)
            
            # Extended diving legs
            pygame.draw.line(screen, skin_col, (x + 28 * sign, cy - 6), (x + 72 * sign, cy - 6), 7)
            pygame.draw.line(screen, sock_col, (x + 58 * sign, cy - 6), (x + 72 * sign, cy - 6), 7)
            pygame.draw.rect(screen, shoe_col, (int(x + 72 * sign - 3), int(cy - 10), 8, 8), border_radius=2)
            
            pygame.draw.line(screen, skin_col, (x + 28 * sign, cy + 6), (x + 64 * sign, cy + 9), 7)
            pygame.draw.line(screen, sock_col, (x + 50 * sign, cy + 8), (x + 64 * sign, cy + 9), 7)
            pygame.draw.rect(screen, shoe_col, (int(x + 64 * sign - 3), int(cy + 6), 8, 8), border_radius=2)
            
            # Fully extended arms reaching for ball
            pygame.draw.line(screen, jersey_col, (x - 18 * sign, cy - 8), (x - 68 * sign, cy - 22), 6)
            pygame.draw.circle(screen, skin_col, (int(x - 68 * sign), int(cy - 22)), 5)
            pygame.draw.circle(screen, glove_col, (int(x - 72 * sign), int(cy - 23)), 8)
            
            pygame.draw.line(screen, jersey_col, (x - 18 * sign, cy + 8), (x - 58 * sign, cy + 3), 6)
            pygame.draw.circle(screen, skin_col, (int(x - 58 * sign), int(cy + 3)), 5)
            pygame.draw.circle(screen, glove_col, (int(x - 62 * sign), int(cy + 2)), 8)
      
      # Diving high or stay center
        elif state == "stay_center":
            # Ready stance, arms out
            pygame.draw.line(screen, skin_col, (x - 16, y - 42), (x - 22, y), 8)
            pygame.draw.line(screen, skin_col, (x + 16, y - 42), (x + 22, y), 8)
            pygame.draw.circle(screen, shoe_col, (x - 22, y), 6)
            pygame.draw.circle(screen, shoe_col, (x + 22, y), 6)
            
            pygame.draw.rect(screen, shorts_col, (x - 20, y - 54, 40, 16), border_radius=3)
            pygame.draw.rect(screen, jersey_col, (x - 16, y - 88, 32, 38), border_radius=4)
            
            pygame.draw.circle(screen, skin_col, (x, y - 99), 11)
            pygame.draw.rect(screen, hair_col, (x - 9, y - 110, 18, 7), border_radius=2)
            
            # Arms raised to sides
            pygame.draw.line(screen, jersey_col, (x - 16, y - 80), (x - 32, y - 90), 6)
            pygame.draw.line(screen, skin_col, (x - 32, y - 90), (x - 42, y - 98), 5)
            pygame.draw.circle(screen, glove_col, (x - 42, y - 98), 8)
            
            pygame.draw.line(screen, jersey_col, (x + 16, y - 80), (x + 32, y - 90), 6)
            pygame.draw.line(screen, skin_col, (x + 32, y - 90), (x + 42, y - 98), 5)
            pygame.draw.circle(screen, glove_col, (x + 42, y - 98), 8)

        else:
            # Idle ready breathing animation
            b_y = math.sin(ticks * 0.007) * 2.2
            
            # Legs
            pygame.draw.line(screen, skin_col, (x - 12, y - 45), (x - 12, y), 8)
            pygame.draw.line(screen, skin_col, (x + 12, y - 45), (x + 12, y), 8)
            pygame.draw.circle(screen, shoe_col, (x - 12, y), 7)
            pygame.draw.circle(screen, shoe_col, (x + 12, y), 7)
            
            # Shorts & Torso
            pygame.draw.rect(screen, shorts_col, (x - 18, y - 56, 36, 16), border_radius=3)
            pygame.draw.rect(screen, jersey_col, (x - 15, y - 90 + b_y, 30, 36), border_radius=4)
            
            # Head
            pygame.draw.circle(screen, skin_col, (x, y - 101 + b_y), 10)
            pygame.draw.rect(screen, hair_col, (x - 8, y - 111 + b_y, 16, 6), border_radius=2)
            
            # Arms bent down ready
            pygame.draw.line(screen, jersey_col, (x - 15, y - 82 + b_y), (x - 25, y - 64 + b_y), 6)
            pygame.draw.line(screen, skin_col, (x - 25, y - 64 + b_y), (x - 23, y - 46 + b_y), 5)
            pygame.draw.circle(screen, glove_col, (x - 23, y - 44 + b_y), 8)
            
            pygame.draw.line(screen, jersey_col, (x + 15, y - 82 + b_y), (x + 26, y - 64 + b_y), 6)
            pygame.draw.line(screen, skin_col, (x + 26, y - 64 + b_y), (x + 24, y - 46 + b_y), 5)
            pygame.draw.circle(screen, glove_col, (x + 24, y - 44 + b_y), 8)

    def _draw_football_procedural(self, screen: pygame.Surface, x: int, y: int, radius: int) -> None:
        # Base soccer ball surface
        pygame.draw.circle(screen, (248, 248, 248), (x, y), radius)
        
        # Center pentagon stitching coordinates
        pts = [
            (x, y - int(radius * 0.28)),
            (x + int(radius * 0.26), y - int(radius * 0.08)),
            (x + int(radius * 0.16), y + int(radius * 0.22)),
            (x - int(radius * 0.16), y + int(radius * 0.22)),
            (x - int(radius * 0.26), y - int(radius * 0.08))
        ]
        pygame.draw.polygon(screen, (40, 40, 42), pts)
        
        # Grid/stitch lines connecting center to edges
        pygame.draw.line(screen, (40, 40, 42), pts[0], (x, y - radius), 1)
        pygame.draw.line(screen, (40, 40, 42), pts[1], (x + int(radius * 0.8), y - int(radius * 0.58)), 1)
        pygame.draw.line(screen, (40, 40, 42), pts[2], (x + int(radius * 0.5), y + int(radius * 0.8)), 1)
        pygame.draw.line(screen, (40, 40, 42), pts[3], (x - int(radius * 0.5), y + int(radius * 0.8)), 1)
        pygame.draw.line(screen, (40, 40, 42), pts[4], (x - int(radius * 0.8), y - int(radius * 0.58)), 1)
        
        # Border pentagon overlays
        pygame.draw.circle(screen, (40, 40, 42), (x, y - radius), int(radius * 0.22))
        pygame.draw.circle(screen, (40, 40, 42), (x + int(radius * 0.86), y - int(radius * 0.52)), int(radius * 0.22))
        pygame.draw.circle(screen, (40, 40, 42), (x - int(radius * 0.86), y - int(radius * 0.52)), int(radius * 0.22))
        pygame.draw.circle(screen, (40, 40, 42), (x + int(radius * 0.55), y + int(radius * 0.82)), int(radius * 0.22))
        pygame.draw.circle(screen, (40, 40, 42), (x - int(radius * 0.55), y + int(radius * 0.82)), int(radius * 0.22))
        
        # 3D shading mask overlay
        mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius):
            val = int(130 * (r / radius) ** 1.8)
            pygame.draw.circle(mask, (0, 0, 0, val), (radius, radius), radius - r)
        
        screen.blit(mask, (x - radius, y - radius))
        pygame.draw.circle(screen, (20, 20, 20), (x, y), radius, 2)

    def render(self, screen: pygame.Surface) -> None:
        width = screen.get_width()
        height = screen.get_height()
        ticks = pygame.time.get_ticks()
        
        # Render onto visual backbuffer for shake effect support
        canvas = pygame.Surface((width, height))
        canvas.fill((20, 26, 36))
        
        # 1. Render Sky & Crowd Stadium Background
        for y in range(0, 150):
            # Gradient sky
            ratio = y / 150.0
            r = int(15 * (1 - ratio) + 38 * ratio)
            g = int(20 * (1 - ratio) + 44 * ratio)
            b = int(32 * (1 - ratio) + 56 * ratio)
            pygame.draw.line(canvas, (r, g, b), (0, y), (width, y))
            
        # Slanted gray stands filled with animated crowd
        pygame.draw.rect(canvas, (55, 60, 72), (0, 150, width, 250))
        for sy in range(150, 400, 8):
            pygame.draw.line(canvas, (42, 46, 56), (0, sy), (width, sy), 1)
            for sx in range(0, width, 14):
                h = int(math.sin(sx * 0.04 + sy * 0.95) * 1234)
                if h % 3 == 0:
                    col = (190, 45, 45)     # Team Color 1 (Red fans)
                elif h % 3 == 1:
                    col = (50, 95, 185)     # Team Color 2 (Blue fans)
                else:
                    col = (180, 180, 185)   # Neutral color
                
                # Randomized camera flashes
                if (h + int(ticks * 0.0016)) % 75 == 0:
                    col = (255, 255, 255)
                    
                pygame.draw.rect(canvas, col, (sx + (sy % 5), sy, 4, 3))

        # Advertising Boards right behind goal line
        pygame.draw.rect(canvas, (32, 32, 38), (0, 395, width, 15))
        font_board = self.asset_manager.get_font("default", 14)
        brands = ["SOCCER PRO", "CHAMPION", "GOAL!!!", "SPORTS NET", "KICKOFF"]
        for i in range(10):
            brand_txt = font_board.render(brands[i % len(brands)], True, (255, 215, 0))
            canvas.blit(brand_txt, (50 + i * 150, 396))

        # 2. Render Grass Field with Perspective bands
        pitch_y = 410
        pygame.draw.rect(canvas, (34, 139, 34), (0, pitch_y, width, height - pitch_y))
        
        # Alternating perspective grass stripes
        stripes = [410, 417, 426, 438, 453, 472, 496, 528, 568, 622, 720]
        for idx in range(len(stripes) - 1):
            sy = stripes[idx]
            sh = stripes[idx + 1] - sy
            col = (34, 139, 34) if idx % 2 == 0 else (40, 160, 40)
            pygame.draw.rect(canvas, col, (0, sy, width, sh))
            
        # Draw perspective lines for penalty area
        # Goal line
        pygame.draw.line(canvas, (255, 255, 255), (140, 500), (1140, 500), 2)
        # Six-yard box
        pygame.draw.line(canvas, (255, 255, 255), (420, 500), (380, 560), 2)
        pygame.draw.line(canvas, (255, 255, 255), (860, 500), (900, 560), 2)
        pygame.draw.line(canvas, (255, 255, 255), (380, 560), (900, 560), 2)
        # 18-yard box
        pygame.draw.line(canvas, (255, 255, 255), (240, 500), (60, 720), 3)
        pygame.draw.line(canvas, (255, 255, 255), (1040, 500), (1220, 720), 3)
        pygame.draw.line(canvas, (255, 255, 255), (60, 720), (1220, 720), 3)
        # Penalty spot
        pygame.draw.ellipse(canvas, (255, 255, 255), (634, 597, 12, 6))

        # 3. Render Floodlights & Glow beams
        pygame.draw.polygon(canvas, (65, 70, 80), [(70, 100), (80, 100), (100, 400), (90, 400)])
        pygame.draw.polygon(canvas, (65, 70, 80), [(1210, 100), (1200, 100), (1180, 400), (1190, 400)])
        
        # Draw lights
        pygame.draw.rect(canvas, (40, 40, 45), (55, 75, 40, 25), border_radius=4)
        pygame.draw.rect(canvas, (40, 40, 45), (1185, 75, 40, 25), border_radius=4)
        for i in range(4):
            pygame.draw.circle(canvas, (255, 255, 200), (63 + i * 8, 87), 4)
            pygame.draw.circle(canvas, (255, 255, 200), (1193 + i * 8, 87), 4)

        # Beam lighting overlay
        beams = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.polygon(beams, (255, 255, 240, 16), [(75, 87), (300, 500), (980, 500)])
        pygame.draw.polygon(beams, (255, 255, 240, 16), [(1205, 87), (300, 500), (980, 500)])
        canvas.blit(beams, (0, 0))

        # 4. Render Goal Net & Depth mesh
        goal_rect = self.goal.rect
        net_col = (85, 95, 105)
        back_col = (45, 52, 62)
        
        # 3D Back support structure
        top_y_offset = 25
        bottom_y_offset = 5
        # Top support lines (front to back)
        pygame.draw.line(canvas, back_col, (goal_rect.left, goal_rect.top), (goal_rect.left + 35, goal_rect.top + top_y_offset), 4)
        pygame.draw.line(canvas, back_col, (goal_rect.right, goal_rect.top), (goal_rect.right - 35, goal_rect.top + top_y_offset), 4)
        # Bottom support lines
        pygame.draw.line(canvas, back_col, (goal_rect.left, goal_rect.bottom), (goal_rect.left + 35, goal_rect.bottom - bottom_y_offset), 4)
        pygame.draw.line(canvas, back_col, (goal_rect.right, goal_rect.bottom), (goal_rect.right - 35, goal_rect.bottom - bottom_y_offset), 4)
        
        # Back crossbar and posts
        pygame.draw.line(canvas, back_col, (goal_rect.left + 35, goal_rect.top + top_y_offset), (goal_rect.right - 35, goal_rect.top + top_y_offset), 3)
        pygame.draw.line(canvas, back_col, (goal_rect.left + 35, goal_rect.top + top_y_offset), (goal_rect.left + 35, goal_rect.bottom - bottom_y_offset), 3)
        pygame.draw.line(canvas, back_col, (goal_rect.right - 35, goal_rect.top + top_y_offset), (goal_rect.right - 35, goal_rect.bottom - bottom_y_offset), 3)

        # Net grid rendering
        # Draw perspective grid meshes
        for x in range(0, 601, 24):
            # Front X on crossbar
            fx = goal_rect.left + x
            # Slanted back X
            bx = goal_rect.left + 35 + int(x * (goal_rect.width - 70) / goal_rect.width)
            # Mesh line from front to back
            pygame.draw.line(canvas, net_col, (fx, goal_rect.top), (bx, goal_rect.top + top_y_offset), 1)
            # Vertical mesh line down to ground
            pygame.draw.line(canvas, net_col, (bx, goal_rect.top + top_y_offset), (bx, goal_rect.bottom - bottom_y_offset), 1)
            
        for y in range(0, 301, 20):
            # Horizontal lines on back net mesh
            by = goal_rect.top + top_y_offset + int(y * (goal_rect.height - top_y_offset - bottom_y_offset) / goal_rect.height)
            pygame.draw.line(canvas, net_col, (goal_rect.left + 35, by), (goal_rect.right - 35, by), 1)
            # Side mesh horizontal lines
            pygame.draw.line(canvas, net_col, (goal_rect.left, goal_rect.top + y), (goal_rect.left + 35, goal_rect.top + top_y_offset + int(y * top_y_offset / goal_rect.height)), 1)
            pygame.draw.line(canvas, net_col, (goal_rect.right, goal_rect.top + y), (goal_rect.right - 35, goal_rect.top + top_y_offset + int(y * top_y_offset / goal_rect.height)), 1)

        # Front White Goal Frame Posts (With 3D cylindrical highlight)
        pygame.draw.line(canvas, (240, 240, 240), (goal_rect.left, goal_rect.top), (goal_rect.left, goal_rect.bottom), 12) # Left
        pygame.draw.line(canvas, (180, 180, 185), (goal_rect.left + 4, goal_rect.top), (goal_rect.left + 4, goal_rect.bottom), 3)
        
        pygame.draw.line(canvas, (240, 240, 240), (goal_rect.right, goal_rect.top), (goal_rect.right, goal_rect.bottom), 12) # Right
        pygame.draw.line(canvas, (180, 180, 185), (goal_rect.right + 4, goal_rect.top), (goal_rect.right + 4, goal_rect.bottom), 3)
        
        pygame.draw.line(canvas, (240, 240, 240), (goal_rect.left - 5, goal_rect.top), (goal_rect.right + 5, goal_rect.top), 12) # Crossbar
        pygame.draw.line(canvas, (180, 180, 185), (goal_rect.left, goal_rect.top + 3), (goal_rect.right, goal_rect.top + 3), 3)

        # Highlight defense columns if in defending aim state
        if self.mode == "defending_aim":
            mouse_pos = pygame.mouse.get_pos()
            hovered_zone = self._get_clicked_defense_zone(mouse_pos)
            if hovered_zone:
                wash_surf = pygame.Surface((200, 300), pygame.SRCALPHA)
                wash_surf.fill((255, 255, 0, 45))
                if hovered_zone == "diving_left":
                    canvas.blit(wash_surf, (340, 200))
                elif hovered_zone == "stay_center":
                    canvas.blit(wash_surf, (540, 200))
                elif hovered_zone == "diving_right":
                    canvas.blit(wash_surf, (740, 200))

        # 5. Render Goalkeeper
        self._draw_keeper_procedural(canvas, self.keeper.pos.x, self.keeper.pos.y, self.keeper.state, ticks)

        # 6. Draw dynamic Ball Shadow on Pitch
        ball_x, ball_y = int(self.ball.pos.x), int(self.ball.pos.y)
        t_progress = 0.0
        if self.last_ball_target and (self.last_ball_target[1] - 600) != 0:
            t_progress = (self.ball.pos.y - 600) / (self.last_ball_target[1] - 600)
        t_progress = max(0.0, min(1.0, t_progress))
        ground_y = 600 + (500 - 600) * t_progress
        height_diff = ground_y - self.ball.pos.y
        
        # Scaling shadow size and transparency with height
        sh_radius = max(5, int(self.ball.radius * (1.1 - height_diff / 320.0)))
        sh_alpha = max(15, int(130 * (1.0 - height_diff / 280.0)))
        
        shadow_surf = pygame.Surface((sh_radius * 2, sh_radius), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, sh_alpha), (0, 0, sh_radius * 2, sh_radius))
        canvas.blit(shadow_surf, (ball_x - sh_radius, int(ground_y) - sh_radius // 2))

        # 7. Render Soccer Ball
        self._draw_football_procedural(canvas, ball_x, ball_y, self.ball.radius)

        # 8. Render Aiming Crosshair / Power Gauge
        if self.mode == "aiming" or self.mode == "powering":
            m_pos = pygame.mouse.get_pos()
            
            # Pulse glow target
            g_r = int(18 + 4 * math.sin(ticks * 0.012))
            pygame.draw.circle(canvas, (255, 50, 50), m_pos, g_r, 2)
            pygame.draw.circle(canvas, (255, 50, 50), m_pos, 3)
            # Dashed target line
            pygame.draw.line(canvas, (255, 50, 50), (640, 600), m_pos, 1)

            if self.power_charging:
                bar_x, bar_y, bar_w, bar_h = 590, 630, 100, 14
                pygame.draw.rect(canvas, (40, 40, 45), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
                fill_w = int(self.shot_power)
                r_col = int(self.shot_power * 2.55)
                g_col = int((100 - self.shot_power) * 2.55)
                # Draw neon bar
                pygame.draw.rect(canvas, (r_col, g_col, 0), (bar_x + 1, bar_y + 1, max(1, fill_w - 2), bar_h - 2), border_radius=2)
                # Outer white focus ring
                pygame.draw.rect(canvas, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

        # 9. Draw HUD
        self._render_hud(canvas, width)

        # Replay indicator
        if self.is_replay_flight:
            font_rep = self.asset_manager.get_font("default", 36)
            alpha = int(127 + 128 * math.sin(ticks * 0.015))
            rep_text = font_rep.render("● REPLAY", True, (255, 215, 0))
            rep_text.set_alpha(alpha)
            canvas.blit(rep_text, (30, 130))

        # 10. Result Overlay
        if self.mode == "result":
            wash = pygame.Surface((width, height), pygame.SRCALPHA)
            wash.fill((10, 12, 18, 160))
            canvas.blit(wash, (0, 0))
            
            font_res = self.asset_manager.get_font("default", 90)
            if self.outcome == "GOAL":
                msg = "GOAL!"
                col = (0, 255, 100)
            elif self.outcome == "SAVE":
                msg = "SAVED!"
                col = (0, 153, 255)
            else:
                msg = "MISSED!"
                col = (255, 51, 51)
            res_s = font_res.render(msg, True, col)
            res_r = res_s.get_rect(center=(width // 2, height // 2 - 40))
            canvas.blit(res_s, res_r)
            
            font_sub = self.asset_manager.get_font("default", 24)
            sub_s = font_sub.render("Click or press SPACE to continue", True, (240, 240, 240))
            sub_r = sub_s.get_rect(center=(width // 2, height // 2 + 50))
            canvas.blit(sub_s, sub_r)

        # 11. Final output blit supporting camera shake offsets
        dx = 0
        dy = 0
        if getattr(self, "camera_shake", 0) > 0:
            dx = int(random.uniform(-self.camera_shake, self.camera_shake))
            dy = int(random.uniform(-self.camera_shake, self.camera_shake))
            
        screen.blit(canvas, (dx, dy))

    def _render_hud(self, screen: pygame.Surface, width: int) -> None:
        # Scoreboard card box
        board_w, board_h = 440, 80
        board_x = (width - board_w) // 2
        
        # Transparent glassmorphism scoreboard background
        glass = pygame.Surface((board_w, board_h), pygame.SRCALPHA)
        glass.fill((25, 30, 42, 210))
        screen.blit(glass, (board_x, 15))
        pygame.draw.rect(screen, (70, 85, 110), (board_x, 15, board_w, board_h), width=2, border_radius=8)
        
        # Flags drawing
        self._draw_flag_procedural(screen, board_x + 15, 27, 40, 26, self.selected_team)
        self._draw_flag_procedural(screen, board_x + board_w - 55, 27, 40, 26, self.opponent)

        # Scores
        font_sc = self.asset_manager.get_font("default", 36)
        p_score_text = font_sc.render(str(self.shootout.player_score), True, (255, 255, 255))
        o_score_text = font_sc.render(str(self.shootout.opponent_score), True, (255, 255, 255))
        screen.blit(p_score_text, (board_x + 65, 23))
        screen.blit(o_score_text, (board_x + board_w - 85, 23))
        
        # Team Names
        font_nm = self.asset_manager.get_font("default", 20)
        p_name = font_nm.render(self.selected_team[:10], True, (240, 240, 240))
        o_name = font_nm.render(self.opponent[:10], True, (240, 240, 240))
        screen.blit(p_name, (board_x + 15, 57))
        screen.blit(o_name, (board_x + board_w - 95, 57))

        # VS divider
        vs_text = font_nm.render("VS", True, (255, 215, 0))
        screen.blit(vs_text, (board_x + board_w // 2 - 12, 33))
        
        # Checkmark/cross circle indicators for penalties
        dot_r = 9
        spacing = 24
        
        # Player attempts
        start_p_x = board_x - 15
        for i in range(5):
            x = start_p_x - (4 - i) * spacing
            pygame.draw.circle(screen, (30, 34, 45), (x, 50), dot_r + 2)
            pygame.draw.circle(screen, (60, 72, 90), (x, 50), dot_r, 1)
            if i < len(self.shootout.player_kicks):
                col = (0, 230, 90) if self.shootout.player_kicks[i] == "goal" else (240, 45, 45)
                pygame.draw.circle(screen, col, (x, 50), dot_r)
                # Draw check/cross details inside dot
                if self.shootout.player_kicks[i] == "goal":
                    pygame.draw.line(screen, (255, 255, 255), (x - 3, 50), (x - 1, 52), 2)
                    pygame.draw.line(screen, (255, 255, 255), (x - 1, 52), (x + 3, 47), 2)
                else:
                    pygame.draw.line(screen, (255, 255, 255), (x - 3, 47), (x + 3, 53), 2)
                    pygame.draw.line(screen, (255, 255, 255), (x + 3, 47), (x - 3, 53), 2)
                
        # Opponent attempts
        start_o_x = board_x + board_w + 15
        for i in range(5):
            x = start_o_x + i * spacing
            pygame.draw.circle(screen, (30, 34, 45), (x, 50), dot_r + 2)
            pygame.draw.circle(screen, (60, 72, 90), (x, 50), dot_r, 1)
            if i < len(self.shootout.opponent_kicks):
                col = (0, 230, 90) if self.shootout.opponent_kicks[i] == "goal" else (240, 45, 45)
                pygame.draw.circle(screen, col, (x, 50), dot_r)
                if self.shootout.opponent_kicks[i] == "goal":
                    pygame.draw.line(screen, (255, 255, 255), (x - 3, 50), (x - 1, 52), 2)
                    pygame.draw.line(screen, (255, 255, 255), (x - 1, 52), (x + 3, 47), 2)
                else:
                    pygame.draw.line(screen, (255, 255, 255), (x - 3, 47), (x + 3, 53), 2)
                    pygame.draw.line(screen, (255, 255, 255), (x + 3, 47), (x - 3, 53), 2)

        # Turn indicator
        font_turn = self.asset_manager.get_font("default", 22)
        if self.mode == "defending_aim":
            turn_msg = "CHOOSE DIVE DIRECTION!"
            turn_col = (255, 150, 50)
        elif self.mode == "aiming" or self.mode == "powering":
            turn_msg = "YOUR TURN: HOLD CLICK TO POWER!"
            turn_col = (0, 255, 100)
        else:
            turn_msg = "SIMULATING ATTEMPT..."
            turn_col = (200, 200, 200)
            
        if self.shootout.sudden_death:
            turn_msg += " (SUDDEN DEATH)"
            turn_col = (255, 50, 50)
            
        turn_surf = font_turn.render(turn_msg, True, turn_col)
        turn_rect = turn_surf.get_rect(center=(width // 2, 115))
        screen.blit(turn_surf, turn_rect)

        # DifficultyBadge
        font_diff = self.asset_manager.get_font("default", 16)
        diff_text = font_diff.render(f"DIFFICULTY: {self.difficulty.upper()}", True, (255, 215, 0))
        diff_w, diff_h = diff_text.get_width() + 16, diff_text.get_height() + 8
        diff_x = width - diff_w - 20
        # Draw Glass pill box for difficulty
        pygame.draw.rect(screen, (25, 30, 42, 180), (diff_x, 15, diff_w, diff_h), border_radius=6)
        pygame.draw.rect(screen, (70, 85, 110), (diff_x, 15, diff_w, diff_h), width=1, border_radius=6)
        screen.blit(diff_text, (diff_x + 8, 19))

        # Defending instructions
        if self.mode == "defending_aim":
            font_def = self.asset_manager.get_font("default", 24)
            def_text1 = font_def.render("Click columns in goal, or use keys:", True, (240, 240, 240))
            def_text2 = font_def.render("[A] DIVE LEFT   [S] STAY CENTER   [D] DIVE RIGHT", True, (255, 215, 0))
            screen.blit(def_text1, (board_x - 10, 155))
            screen.blit(def_text2, (board_x - 70, 185))

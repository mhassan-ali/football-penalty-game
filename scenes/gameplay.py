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
        
        self.difficulty = "medium"  # Default difficulty
        self.mode = "aiming"        # "aiming", "powering", "flight", "result", "defending_aim", "match_over"
        self.outcome = ""           # "GOAL", "SAVE", "MISS"
        
        # Shot power values
        self.shot_power = 0.0
        self.power_charging = False
        
        # Replay triggers
        self.is_replay_flight = False
        self.last_ball_target: Tuple[float, float] = (0.0, 0.0)
        self.last_ball_speed = 0.0
        self.last_keeper_dive = "stay_center"
        self.last_keeper_dive_speed = 700.0
        
        self.result_timer = 0.0
        self.aim_target: Tuple[float, float] = (640.0, 350.0)

    def on_enter(self, **kwargs: Any) -> None:
        self.shootout.reset()
        self._reset_attempt()
        self.mode = "aiming"

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
                self.state_manager.change_state(State.MAIN_MENU)
                self.scene_manager.switch_scene("menu")
                
            # Difficulty hotkeys (F1, F2, F3) for manual testing / verification
            elif event.key == pygame.K_F1:
                self.difficulty = "easy"
            elif event.key == pygame.K_F2:
                self.difficulty = "medium"
            elif event.key == pygame.K_F3:
                self.difficulty = "hard"
                
            # Reset/Play Again in match_over
            elif self.mode == "match_over" and event.key == pygame.K_SPACE:
                self.shootout.reset()
                self._reset_attempt()
                self.mode = "aiming"
                
            # Skip results or trigger next round
            elif self.mode == "result" and event.key == pygame.K_SPACE:
                self._advance_after_result()
                
            # Defending keyboard shortcuts
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
                # Check column clicks
                dive = self._get_clicked_defense_zone(event.pos)
                if dive:
                    self._execute_defense(dive)
            elif self.mode == "result":
                self._advance_after_result()
            elif self.mode == "match_over":
                self.shootout.reset()
                self._reset_attempt()
                self.mode = "aiming"

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.mode == "aiming" and self.power_charging:
                self._execute_player_shot()

    def _get_clicked_defense_zone(self, pos: Tuple[int, int]) -> Optional[str]:
        # Columns inside goal area [340 to 940]
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
        
        # Calculate speed based on shot power
        speed = 600.0 + self.shot_power * 8.0
        
        # Add risk/dispersion if overpower (> 90%)
        target_x, target_y = self.aim_target
        if self.shot_power > 90.0:
            overpower_ratio = (self.shot_power - 90.0)
            # Blast it upwards/wide
            target_y -= overpower_ratio * 6.5
            target_x += random.uniform(-overpower_ratio * 4.0, overpower_ratio * 4.0)

        # Goalkeeper decides dive direction based on shot position and difficulty
        keeper_dive = self.keeper.decide_dive(target_x, self.difficulty)
        
        # Save flight parameters for possible replay
        self.last_ball_target = (target_x, target_y)
        self.last_ball_speed = speed
        self.last_keeper_dive = keeper_dive
        self.last_keeper_dive_speed = self.keeper.dive_speed
        
        # Shoot ball
        self.ball.shoot((target_x, target_y), speed)
        
        self.is_replay_flight = False
        self.mode = "flight"

    def _execute_defense(self, player_dive: str) -> None:
        # User commits to dive
        self.keeper.commit_to_dive_state(player_dive)
        
        # AI shoots the ball
        ai_target = decide_ai_shot(self.difficulty)
        ai_speed = random.uniform(700.0, 1100.0)
        
        # Save flight parameters for possible replay
        self.last_ball_target = ai_target
        self.last_ball_speed = ai_speed
        self.last_keeper_dive = player_dive
        self.last_keeper_dive_speed = self.keeper.dive_speed
        
        # Shoot
        self.ball.shoot(ai_target, ai_speed)
        
        self.is_replay_flight = False
        self.mode = "flight"

    def _advance_after_result(self) -> None:
        if self.shootout.is_over:
            self.mode = "match_over"
        else:
            self._reset_attempt()
            if self.shootout.current_turn == "player":
                self.mode = "aiming"
            else:
                self.mode = "defending_aim"

    def update(self, dt: float) -> None:
        # Increment shot power while holding
        if self.mode == "aiming" and self.power_charging:
            self.shot_power += dt * 95.0
            if self.shot_power >= 100.0:
                self.shot_power = 100.0
                # Auto-release shot when it hits max power
                self._execute_player_shot()
                return

        if self.mode == "flight":
            # Scale physics delta-time for slow-mo replay simulation
            sim_dt = dt * 0.35 if self.is_replay_flight else dt
            
            self.ball.update(sim_dt)
            self.keeper.update(sim_dt)
            
            if not self.ball.is_moving:
                # Calculate outcomes at the end of flight
                if self.is_replay_flight:
                    # Replay has ended: advance to result screen
                    self.shootout.record_outcome(self.outcome)
                    self.is_replay_flight = False
                    self.result_timer = 2.0
                    self.mode = "result"
                else:
                    # Live attempt flight has ended.
                    ball_x, ball_y = self.ball.pos.x, self.ball.pos.y
                    is_in_goal = self.goal.rect.collidepoint(ball_x, ball_y)
                    
                    if not is_in_goal:
                        self.outcome = "MISS"
                    else:
                        if self.keeper.rect.colliderect(self.ball.rect):
                            self.outcome = "SAVE"
                        else:
                            self.outcome = "GOAL"
                    
                    # Trigger Replay if goal is scored
                    if self.outcome == "GOAL":
                        self.is_replay_flight = True
                        self.ball.reset()
                        self.keeper.reset()
                        
                        # Set up slow-mo shot
                        self.keeper.commit_to_dive_state(self.last_keeper_dive)
                        self.keeper.dive_speed = self.last_keeper_dive_speed
                        self.ball.shoot(self.last_ball_target, self.last_ball_speed)
                    else:
                        # Direct to result on MISS or SAVE
                        self.shootout.record_outcome(self.outcome)
                        self.result_timer = 2.0
                        self.mode = "result"

        elif self.mode == "result":
            self.result_timer -= dt
            if self.result_timer <= 0:
                self._advance_after_result()

    def render(self, screen: pygame.Surface) -> None:
        width = screen.get_width()
        height = screen.get_height()
        
        # 1. Background
        screen.fill((20, 26, 36))
        
        # Floodlights
        pygame.draw.circle(screen, (50, 50, 60), (150, 50), 30)
        pygame.draw.circle(screen, (255, 255, 200), (150, 50), 20)
        pygame.draw.circle(screen, (50, 50, 60), (width - 150, 50), 30)
        pygame.draw.circle(screen, (255, 255, 200), (width - 150, 50), 20)
        
        # Grass Pitch
        pitch_y = 400
        pygame.draw.rect(screen, (34, 139, 34), (0, pitch_y, width, height - pitch_y))
        band_h = 40
        for y in range(pitch_y, height, band_h * 2):
            pygame.draw.rect(screen, (40, 160, 40), (0, y, width, band_h))
            
        # Penalty spot
        pygame.draw.circle(screen, (255, 255, 255), (640, 600), 6)
        
        # 2. Goal Area Net and Frame
        goal_rect = self.goal.rect
        net_col = (60, 70, 80)
        for x in range(goal_rect.left, goal_rect.right + 1, 20):
            pygame.draw.line(screen, net_col, (x, goal_rect.top), (x, goal_rect.bottom), 1)
        for y in range(goal_rect.top, goal_rect.bottom + 1, 20):
            pygame.draw.line(screen, net_col, (goal_rect.left, y), (goal_rect.right, y), 1)
            
        # Draw columns wash in Defending mode
        if self.mode == "defending_aim":
            mouse_pos = pygame.mouse.get_pos()
            hovered_zone = self._get_clicked_defense_zone(mouse_pos)
            if hovered_zone:
                wash_surf = pygame.Surface((200, 300), pygame.SRCALPHA)
                wash_surf.fill((255, 255, 255, 30))
                if hovered_zone == "diving_left":
                    screen.blit(wash_surf, (340, 200))
                elif hovered_zone == "stay_center":
                    screen.blit(wash_surf, (540, 200))
                elif hovered_zone == "diving_right":
                    screen.blit(wash_surf, (740, 200))

        # Goal Frame
        pygame.draw.line(screen, (255, 255, 255), (goal_rect.left, goal_rect.top), (goal_rect.left, goal_rect.bottom), 10)
        pygame.draw.line(screen, (255, 255, 255), (goal_rect.right, goal_rect.top), (goal_rect.right, goal_rect.bottom), 10)
        pygame.draw.line(screen, (255, 255, 255), (goal_rect.left - 4, goal_rect.top), (goal_rect.right + 4, goal_rect.top), 10)

        # 3. Goalkeeper
        k_rect = self.keeper.rect
        # Draw goalkeeper body rect (blue kit)
        pygame.draw.rect(screen, (0, 102, 204), k_rect, border_radius=4)
        pygame.draw.rect(screen, (0, 76, 153), k_rect, width=2, border_radius=4)
        
        head_col = (255, 218, 185)
        glove_col = (255, 69, 0)
        
        if self.keeper.state in ("diving_left", "diving_right"):
            if self.keeper.state == "diving_left":
                head_pos = (k_rect.left + 25, k_rect.centery)
                lg = (k_rect.left + 5, k_rect.centery - 15)
                rg = (k_rect.left + 5, k_rect.centery + 15)
            else:
                head_pos = (k_rect.right - 25, k_rect.centery)
                lg = (k_rect.right - 5, k_rect.centery - 15)
                rg = (k_rect.right - 5, k_rect.centery + 15)
            pygame.draw.circle(screen, head_col, head_pos, 16)
            pygame.draw.circle(screen, glove_col, lg, 10)
            pygame.draw.circle(screen, glove_col, rg, 10)
        else:
            # Standing position
            head_pos = (k_rect.centerx, k_rect.top + 20)
            lg = (k_rect.left - 10, k_rect.top + 45)
            rg = (k_rect.right + 10, k_rect.top + 45)
            pygame.draw.circle(screen, head_col, head_pos, 16)
            pygame.draw.circle(screen, glove_col, lg, 10)
            pygame.draw.circle(screen, glove_col, rg, 10)
            pygame.draw.line(screen, (0, 102, 204), (k_rect.left, k_rect.top + 40), lg, 6)
            pygame.draw.line(screen, (0, 102, 204), (k_rect.right, k_rect.top + 40), rg, 6)

        # 4. Football
        ball_x, ball_y = int(self.ball.pos.x), int(self.ball.pos.y)
        pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), self.ball.radius)
        pygame.draw.circle(screen, (0, 0, 0), (ball_x, ball_y), self.ball.radius, 1)
        pygame.draw.circle(screen, (20, 20, 20), (ball_x, ball_y), 4)
        for angle in (0, 72, 144, 216, 288):
            rad = math.radians(angle)
            ex = ball_x + int(math.cos(rad) * self.ball.radius)
            ey = ball_y + int(math.sin(rad) * self.ball.radius)
            pygame.draw.line(screen, (20, 20, 20), (ball_x, ball_y), (ex, ey), 1)

        # 5. Aiming HUD details
        if self.mode == "aiming" or self.mode == "powering":
            m_pos = pygame.mouse.get_pos()
            pygame.draw.circle(screen, (255, 0, 0), m_pos, 18, 2)
            pygame.draw.circle(screen, (255, 0, 0), m_pos, 2)
            pygame.draw.line(screen, (255, 0, 0), (640, 600), m_pos, 1)

            # Draw charging power bar below ball
            if self.power_charging:
                bar_x = 590
                bar_y = 630
                bar_w = 100
                bar_h = 12
                # draw frame
                pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
                # fill
                fill_w = int(self.shot_power)
                # color turns red as power charges
                r = int(self.shot_power * 2.55)
                g = int((100 - self.shot_power) * 2.55)
                pygame.draw.rect(screen, (r, g, 0), (bar_x, bar_y, fill_w, bar_h), border_radius=3)

        # 6. Scoreboard and HUD presentation
        self._render_hud(screen, width)

        # 7. Slow-mo Replay flashing watermark
        if self.is_replay_flight:
            font_rep = self.asset_manager.get_font("default", 36)
            # Flashing visual effect using sine
            alpha = int(127 + 128 * math.sin(pygame.time.get_ticks() * 0.01))
            rep_text = font_rep.render("● REPLAY", True, (255, 255, 0))
            rep_text.set_alpha(alpha)
            screen.blit(rep_text, (20, 100))

        # 8. Result display overlay
        if self.mode == "result":
            wash = pygame.Surface((width, height), pygame.SRCALPHA)
            wash.fill((10, 10, 15, 180))
            screen.blit(wash, (0, 0))
            
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
            screen.blit(res_s, res_r)
            
            font_sub = self.asset_manager.get_font("default", 24)
            sub_s = font_sub.render("Click or press SPACE to continue", True, (240, 240, 240))
            sub_r = sub_s.get_rect(center=(width // 2, height // 2 + 50))
            screen.blit(sub_s, sub_r)

        # 9. Match Over Overlay
        elif self.mode == "match_over":
            wash = pygame.Surface((width, height), pygame.SRCALPHA)
            wash.fill((10, 10, 15, 230))
            screen.blit(wash, (0, 0))
            
            font_mo = self.asset_manager.get_font("default", 96)
            winner = self.shootout.winner
            if winner == "player":
                msg = "YOU WIN! 🏆"
                col = (255, 215, 0)
            else:
                msg = "OPPONENT WINS"
                col = (200, 50, 50)
            
            mo_s = font_mo.render(msg, True, col)
            mo_r = mo_s.get_rect(center=(width // 2, height // 2 - 80))
            screen.blit(mo_s, mo_r)

            font_sc = self.asset_manager.get_font("default", 48)
            sc_s = font_sc.render(f"Final Score: {self.shootout.player_score} - {self.shootout.opponent_score}", True, (255, 255, 255))
            sc_r = sc_s.get_rect(center=(width // 2, height // 2 + 10))
            screen.blit(sc_s, sc_r)

            font_sub = self.asset_manager.get_font("default", 24)
            sub_s = font_sub.render("Click or press SPACE to Play Again  |  ESC to Menu", True, (200, 200, 200))
            sub_r = sub_s.get_rect(center=(width // 2, height // 2 + 90))
            screen.blit(sub_s, sub_r)

    def _render_hud(self, screen: pygame.Surface, width: int) -> None:
        # Draw central scoreboard box
        board_w = 400
        board_h = 75
        board_x = (width - board_w) // 2
        pygame.draw.rect(screen, (30, 36, 46), (board_x, 15, board_w, board_h), border_radius=8)
        pygame.draw.rect(screen, (50, 60, 75), (board_x, 15, board_w, board_h), width=2, border_radius=8)
        
        # Display scores
        font_sc = self.asset_manager.get_font("default", 36)
        p_score_text = font_sc.render(str(self.shootout.player_score), True, (255, 255, 255))
        o_score_text = font_sc.render(str(self.shootout.opponent_score), True, (255, 255, 255))
        
        screen.blit(p_score_text, (board_x + 50, 30))
        screen.blit(o_score_text, (board_x + board_w - 70, 30))
        
        # Names
        font_nm = self.asset_manager.get_font("default", 20)
        p_name = font_nm.render("PLAYER", True, (200, 200, 200))
        o_name = font_nm.render("OPPONENT", True, (200, 200, 200))
        screen.blit(p_name, (board_x + 35, 60))
        screen.blit(o_name, (board_x + board_w - 110, 60))

        # VS indicator
        vs_text = font_nm.render("VS", True, (255, 215, 0))
        screen.blit(vs_text, (board_x + board_w // 2 - 10, 38))
        
        # Draw attempt dots/circles for player & opponent
        dot_r = 8
        spacing = 22
        # Player dots left aligned
        start_p_x = board_x - 10
        for i in range(5):
            x = start_p_x - (4 - i) * spacing
            pygame.draw.circle(screen, (60, 60, 60), (x, 50), dot_r, 1) # border
            
            if i < len(self.shootout.player_kicks):
                kick = self.shootout.player_kicks[i]
                col = (0, 255, 100) if kick == "goal" else (255, 50, 50)
                pygame.draw.circle(screen, col, (x, 50), dot_r - 2)
                
        # Opponent dots right aligned
        start_o_x = board_x + board_w + 10
        for i in range(5):
            x = start_o_x + i * spacing
            pygame.draw.circle(screen, (60, 60, 60), (x, 50), dot_r, 1) # border
            
            if i < len(self.shootout.opponent_kicks):
                kick = self.shootout.opponent_kicks[i]
                col = (0, 255, 100) if kick == "goal" else (255, 50, 50)
                pygame.draw.circle(screen, col, (x, 50), dot_r - 2)

        # Active turn & round status below scoreboard
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
        turn_rect = turn_surf.get_rect(center=(width // 2, 110))
        screen.blit(turn_surf, turn_rect)

        # Difficulty & Keybind reminders
        font_diff = self.asset_manager.get_font("default", 18)
        diff_text = font_diff.render(f"DIFFICULTY: {self.difficulty.upper()} (F1/F2/F3 to change)", True, (150, 160, 180))
        screen.blit(diff_text, (width - 320, 20))

        # Defending instructions
        if self.mode == "defending_aim":
            font_def = self.asset_manager.get_font("default", 24)
            def_text1 = font_def.render("Click columns in goal, or use keys:", True, (240, 240, 240))
            def_text2 = font_def.render("[A] DIVE LEFT   [S] STAY CENTER   [D] DIVE RIGHT", True, (255, 215, 0))
            screen.blit(def_text1, (board_x - 10, 150))
            screen.blit(def_text2, (board_x - 70, 180))

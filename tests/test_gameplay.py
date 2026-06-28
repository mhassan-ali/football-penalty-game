import unittest
import pygame
from game.entities import Goal, Ball, Goalkeeper, decide_ai_shot
from game.shootout import Shootout

class TestGameplayEntities(unittest.TestCase):
    def setUp(self) -> None:
        pygame.init()

    def test_ball_shoot_and_update(self):
        ball = Ball(start_pos=(640, 600))
        self.assertFalse(ball.is_moving)

        ball.shoot((640, 200))
        self.assertTrue(ball.is_moving)

        # Update by 0.1 seconds (speed is 1000px/s, travels 100px upwards)
        ball.update(0.1)
        self.assertAlmostEqual(ball.pos.y, 500.0)
        self.assertEqual(ball.pos.x, 640.0)

        # Snap to target on arrival
        ball.update(1.0)
        self.assertEqual(ball.pos, pygame.math.Vector2(640, 200))
        self.assertFalse(ball.is_moving)

    def test_ball_reset(self):
        ball = Ball(start_pos=(640, 600))
        ball.shoot((640, 200))
        ball.update(0.1)
        self.assertTrue(ball.is_moving)
        
        ball.reset()
        self.assertFalse(ball.is_moving)
        self.assertEqual(ball.pos, pygame.math.Vector2(640, 600))

    def test_goalkeeper_dive_and_update(self):
        keeper = Goalkeeper(start_pos=(640, 500))
        self.assertEqual(keeper.state, "idle")

        dive = keeper.decide_dive(640.0, "easy")
        self.assertIn(dive, ["diving_left", "diving_right", "stay_center"])

        keeper.update(0.1)
        if dive == "diving_left":
            self.assertTrue(keeper.pos.x < 640.0)
        elif dive == "diving_right":
            self.assertTrue(keeper.pos.x > 640.0)
        else:
            self.assertEqual(keeper.pos.x, 640.0)

    def test_keeper_horizontal_collision_rect(self):
        keeper = Goalkeeper(start_pos=(640, 500), width=80, height=120)
        self.assertEqual(keeper.rect, pygame.Rect(600, 380, 80, 120))

        keeper.state = "diving_left"
        self.assertEqual(keeper.rect, pygame.Rect(580, 420, 120, 80))

    def test_ai_shooter_targeting(self):
        # Easy AI target
        tx, ty = decide_ai_shot("easy")
        self.assertTrue(150 <= ty <= 480)
        
        # Hard AI target (corner aims)
        tx_hard, ty_hard = decide_ai_shot("hard")
        self.assertTrue(210 <= ty_hard <= 280)
        # Should target either left corner (355-450) or right corner (830-925)
        self.assertTrue((355 <= tx_hard <= 450) or (830 <= tx_hard <= 925))


class TestShootoutRules(unittest.TestCase):
    def test_initial_rules_state(self):
        so = Shootout()
        self.assertEqual(so.player_score, 0)
        self.assertEqual(so.opponent_score, 0)
        self.assertEqual(so.current_round, 0)
        self.assertEqual(so.current_turn, "player")
        self.assertFalse(so.is_over)
        self.assertFalse(so.sudden_death)

    def test_scoring_sequence(self):
        so = Shootout()
        
        # Round 1: Player scores, Opponent saves
        so.record_outcome("GOAL")  # player turn
        self.assertEqual(so.player_score, 1)
        self.assertEqual(so.current_turn, "opponent")
        
        so.record_outcome("SAVE")  # opponent turn
        self.assertEqual(so.opponent_score, 0)
        self.assertEqual(so.current_round, 1)
        self.assertEqual(so.current_turn, "player")

    def test_early_win_detection(self):
        so = Shootout()
        # Simulate Player scoring 3, Opponent missing 3 in first 3 rounds
        # Round 1
        so.record_outcome("GOAL")
        so.record_outcome("MISS")
        # Round 2
        so.record_outcome("GOAL")
        so.record_outcome("MISS")
        # Round 3
        so.record_outcome("GOAL")
        so.record_outcome("MISS")
        
        # After Round 3: Score is 3 - 0. Opponent has only 2 rounds left (max points possible: 2).
        # Player wins early!
        self.assertTrue(so.is_over)
        self.assertEqual(so.winner, "player")

    def test_sudden_death_transition_and_completion(self):
        so = Shootout()
        # Alternate goals so it's tied 5-5 after 5 rounds
        for _ in range(5):
            so.record_outcome("GOAL")
            so.record_outcome("GOAL")

        self.assertEqual(so.player_score, 5)
        self.assertEqual(so.opponent_score, 5)
        self.assertTrue(so.sudden_death)
        self.assertFalse(so.is_over)

        # Sudden death round 1: Player scores, Opponent misses
        so.record_outcome("GOAL")
        self.assertFalse(so.is_over)  # wait for opponent turn in sudden death
        
        so.record_outcome("MISS")
        self.assertTrue(so.is_over)
        self.assertEqual(so.winner, "player")

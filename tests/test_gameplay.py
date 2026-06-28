import unittest
import pygame
from game.entities import Goal, Ball, Goalkeeper

class TestGameplayEntities(unittest.TestCase):
    def setUp(self) -> None:
        # Initialize pygame for pygame.Rect and math vector operations
        pygame.init()

    def test_ball_shoot_and_update(self):
        ball = Ball(start_pos=(640, 600))
        self.assertFalse(ball.is_moving)
        self.assertEqual(ball.pos, pygame.math.Vector2(640, 600))

        # Shoot to the top center (640, 200)
        ball.shoot((640, 200))
        self.assertTrue(ball.is_moving)
        self.assertEqual(ball.target, pygame.math.Vector2(640, 200))

        # Update by 0.1 seconds
        # Speed is 1000px/s, so in 0.1s it moves 100px upwards
        ball.update(0.1)
        self.assertAlmostEqual(ball.pos.y, 500.0)
        self.assertEqual(ball.pos.x, 640.0)
        self.assertTrue(ball.is_moving)

        # Update by 1.0s (should pass and snap to the target)
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
        self.assertIsNone(ball.target)

    def test_goalkeeper_dive_and_update(self):
        keeper = Goalkeeper(start_pos=(640, 500))
        self.assertEqual(keeper.state, "idle")

        dive = keeper.decide_dive()
        self.assertIn(dive, ["diving_left", "diving_right", "stay_center"])
        self.assertIn(keeper.state, ["diving_left", "diving_right", "stay_center"])

        # Update position
        keeper.update(0.1)
        if dive == "diving_left":
            self.assertTrue(keeper.pos.x < 640.0)
        elif dive == "diving_right":
            self.assertTrue(keeper.pos.x > 640.0)
        else:
            self.assertEqual(keeper.pos.x, 640.0)

    def test_keeper_horizontal_collision_rect(self):
        # Idle keeper (vertical shape: width 80, height 120)
        keeper = Goalkeeper(start_pos=(640, 500), width=80, height=120)
        self.assertEqual(keeper.rect, pygame.Rect(600, 380, 80, 120))

        # Dive keeper (horizontal shape: width 120, height 80)
        keeper.state = "diving_left"
        self.assertEqual(keeper.rect, pygame.Rect(580, 420, 120, 80))

    def test_collision_detection_logic(self):
        goal = Goal(left=340, top=200, width=600, height=300)
        
        # Test aim inside goal
        self.assertTrue(goal.rect.collidepoint(640, 300))
        self.assertTrue(goal.rect.collidepoint(350, 210))
        
        # Test aim outside goal
        self.assertFalse(goal.rect.collidepoint(300, 300))  # too far left
        self.assertFalse(goal.rect.collidepoint(640, 100))  # too high
        
        # Test collision between ball and diving keeper
        ball = Ball(start_pos=(640, 600))
        keeper = Goalkeeper(start_pos=(640, 500), width=80, height=120)
        
        # Scenario 1: Keeper dives right (covering X=860), ball is shot to top right (X=860, Y=300)
        keeper.state = "diving_right"
        keeper.pos.x = 860.0
        ball.pos = pygame.math.Vector2(860, 450)  # near keeper dive position
        self.assertTrue(keeper.rect.colliderect(ball.rect))

        # Scenario 2: Keeper dives left (covering X=420), ball is shot to top right (X=860, Y=300)
        keeper.state = "diving_left"
        keeper.pos.x = 420.0
        ball.pos = pygame.math.Vector2(860, 450)
        self.assertFalse(keeper.rect.colliderect(ball.rect))

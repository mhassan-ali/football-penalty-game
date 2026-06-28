import pygame
import random
from typing import Tuple, Optional

class Goal:
    def __init__(self, left: float = 340, top: float = 200, width: float = 600, height: float = 300) -> None:
        self.rect = pygame.Rect(left, top, width, height)


class Ball:
    def __init__(self, start_pos: Tuple[float, float] = (640, 600), radius: float = 15) -> None:
        self.start_pos = pygame.math.Vector2(start_pos)
        self.pos = pygame.math.Vector2(start_pos)
        self.target: Optional[pygame.math.Vector2] = None
        self.velocity = pygame.math.Vector2(0, 0)
        self.radius = radius
        self.speed = 1000.0  # Pixels per second
        self.is_moving = False

    def shoot(self, target_pos: Tuple[float, float], custom_speed: Optional[float] = None) -> None:
        """Launches the ball towards the target coordinates at a given speed."""
        self.target = pygame.math.Vector2(target_pos)
        to_target = self.target - self.start_pos
        if to_target.length() > 0:
            direction = to_target.normalize()
        else:
            direction = pygame.math.Vector2(0, -1)
        
        speed = custom_speed if custom_speed is not None else self.speed
        self.velocity = direction * speed
        self.is_moving = True

    def update(self, dt: float) -> None:
        """Updates position. Stops moving when target is reached or passed."""
        if not self.is_moving or self.target is None:
            return

        next_pos = self.pos + self.velocity * dt
        
        # Check if we reached or overshot the target
        dist_to_target = (self.target - self.pos).length()
        step_len = (self.velocity * dt).length()
        
        if step_len >= dist_to_target:
            self.pos = pygame.math.Vector2(self.target)
            self.velocity = pygame.math.Vector2(0, 0)
            self.is_moving = False
        else:
            self.pos = next_pos

    def reset(self) -> None:
        self.pos = pygame.math.Vector2(self.start_pos)
        self.velocity = pygame.math.Vector2(0, 0)
        self.target = None
        self.is_moving = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)


class Goalkeeper:
    def __init__(self, start_pos: Tuple[float, float] = (640, 500), width: float = 80, height: float = 120) -> None:
        self.start_pos = pygame.math.Vector2(start_pos)
        self.pos = pygame.math.Vector2(start_pos)
        self.width = width
        self.height = height
        self.state = "idle"  # idle, diving_left, diving_right, stay_center
        self.target_x = start_pos[0]
        self.dive_speed = 700.0  # Pixels per second

    def decide_dive(self, shot_target_x: float, difficulty: str) -> str:
        """Goalkeeper decides dive direction based on difficulty and player shot direction."""
        # Determine the side of the player's shot
        if shot_target_x < 540:
            shot_side = "diving_left"
        elif shot_target_x > 740:
            shot_side = "diving_right"
        else:
            shot_side = "stay_center"

        rand_val = random.random()
        
        if difficulty == "easy":
            # 33% chance for each side (completely ignores shot target)
            choice = random.choice(["diving_left", "diving_right", "stay_center"])
            self.dive_speed = 550.0
        elif difficulty == "medium":
            # 40% chance of diving correct way, 60% random
            if rand_val < 0.40:
                choice = shot_side
            else:
                choice = random.choice(["diving_left", "diving_right", "stay_center"])
            self.dive_speed = 700.0
        else:  # hard
            # 75% chance of diving correct way, 25% random
            if rand_val < 0.75:
                choice = shot_side
            else:
                choice = random.choice(["diving_left", "diving_right", "stay_center"])
            self.dive_speed = 850.0

        self.state = choice
        self.commit_to_dive_state(choice)
        return choice

    def commit_to_dive_state(self, dive_state: str) -> None:
        """Sets Goalkeeper state and destination target_x."""
        self.state = dive_state
        if dive_state == "diving_left":
            self.target_x = 420.0
        elif dive_state == "diving_right":
            self.target_x = 860.0
        else:
            self.target_x = 640.0

    def update(self, dt: float) -> None:
        """Updates keeper's position towards target_x during the dive."""
        if self.state == "idle":
            return

        # Smooth horizontal slide
        if self.pos.x != self.target_x:
            direction = 1.0 if self.target_x > self.pos.x else -1.0
            move_step = direction * self.dive_speed * dt
            
            # Check if we reach target
            if abs(self.target_x - self.pos.x) <= abs(move_step):
                self.pos.x = self.target_x
            else:
                self.pos.x += move_step

    def reset(self) -> None:
        self.pos = pygame.math.Vector2(self.start_pos)
        self.state = "idle"
        self.target_x = self.start_pos.x

    @property
    def rect(self) -> pygame.Rect:
        # Bounding box is centered around pos.x, and sits on the ground (base at pos.y)
        # swap width/height if diving left/right
        if self.state in ("diving_left", "diving_right"):
            w = self.height
            h = self.width
            return pygame.Rect(self.pos.x - w / 2, self.pos.y - h, w, h)
        else:
            return pygame.Rect(self.pos.x - self.width / 2, self.pos.y - self.height, self.width, self.height)


def decide_ai_shot(difficulty: str) -> Tuple[float, float]:
    """Generates a shot target (X, Y) for the AI kicker based on difficulty."""
    # Goal rect: [340, 200, 600, 300] (Left: 340, Top: 200, Right: 940, Bottom: 500)
    rand_val = random.random()
    
    if difficulty == "easy":
        # 25% chance of missing wide or high
        if rand_val < 0.25:
            tx = random.choice([random.uniform(200, 320), random.uniform(960, 1100)])
            ty = random.uniform(150, 480)
        else:
            # Shot is near center
            tx = random.uniform(500, 780)
            ty = random.uniform(280, 450)
    elif difficulty == "medium":
        # 10% chance of missing
        if rand_val < 0.10:
            tx = random.choice([random.uniform(250, 330), random.uniform(950, 1050)])
            ty = random.uniform(150, 480)
        else:
            tx = random.uniform(400, 880)
            ty = random.uniform(220, 450)
    else:  # hard
        # Rarely misses, aims for corners (top left or top right)
        if random.choice([True, False]):
            tx = random.uniform(355, 450)  # Left corner
        else:
            tx = random.uniform(830, 925)  # Right corner
        ty = random.uniform(210, 280)      # High corner
        
    return tx, ty

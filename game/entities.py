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

    def shoot(self, target_pos: Tuple[float, float]) -> None:
        """Launches the ball towards the target coordinates."""
        self.target = pygame.math.Vector2(target_pos)
        to_target = self.target - self.start_pos
        if to_target.length() > 0:
            direction = to_target.normalize()
        else:
            direction = pygame.math.Vector2(0, -1)
        self.velocity = direction * self.speed
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

    def decide_dive(self) -> str:
        """Selects a random dive state and sets target X position. Returns the chosen choice."""
        choice = random.choice(["diving_left", "diving_right", "stay_center"])
        self.state = choice
        if choice == "diving_left":
            self.target_x = 420.0  # Dive to the left side
        elif choice == "diving_right":
            self.target_x = 860.0  # Dive to the right side
        else:
            self.target_x = 640.0  # Stay center
        return choice

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
            # Standing center goes down, horizontal body spans left/right
            # Lets center it around pos.x, and base at pos.y (ground Y)
            return pygame.Rect(self.pos.x - w / 2, self.pos.y - h, w, h)
        else:
            return pygame.Rect(self.pos.x - self.width / 2, self.pos.y - self.height, self.width, self.height)

import random
import math
from typing import List, Tuple, Optional
import pygame

class Particle:
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        radius: float,
        lifetime: float,
        gravity: float = 0.0,
        drag: float = 1.0,
        shape: str = "circle",
        rotation_speed: float = 0.0,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.initial_radius = radius
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.drag = drag
        self.shape = shape
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = rotation_speed

    def update(self, dt: float) -> bool:
        """Updates particle physics. Returns False if particle is dead."""
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False

        self.vx *= self.drag
        self.vy *= self.drag
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation += self.rotation_speed * dt
        
        # Shrink over lifetime
        progress = self.lifetime / self.max_lifetime
        self.radius = max(0.5, self.initial_radius * progress)
        return True

    def draw(self, surface: pygame.Surface) -> None:
        if self.lifetime <= 0 or self.radius <= 0.5:
            return
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        alpha = max(0, min(255, alpha))

        if self.shape == "rect" or self.shape == "confetti":
            size = max(2, int(self.radius * 2))
            rect_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            rect_surf.fill(color_with_alpha)
            if self.rotation_speed != 0:
                rotated_surf = pygame.transform.rotate(rect_surf, self.rotation)
                rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
                surface.blit(rotated_surf, rect)
            else:
                surface.blit(rect_surf, (int(self.x - size // 2), int(self.y - size // 2)))
        else:
            # Circle / spark particle
            int_radius = int(self.radius)
            if int_radius <= 0:
                return
            surf = pygame.Surface((int_radius * 2 + 2, int_radius * 2 + 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(surf, color_with_alpha, (int_radius + 1, int_radius + 1), int_radius)
            surface.blit(surf, (int(self.x - int_radius - 1), int(self.y - int_radius - 1)))


class ParticleSystem:
    def __init__(self) -> None:
        self.particles: List[Particle] = []

    def clear(self) -> None:
        self.particles.clear()

    def update(self, dt: float) -> None:
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface: pygame.Surface) -> None:
        for p in self.particles:
            p.draw(surface)

    def spawn_confetti(self, x: float, y: float, count: int = 60, colors: Optional[List[Tuple[int, int, int]]] = None) -> None:
        if not colors:
            colors = [
                (255, 215, 0), (230, 50, 50), (50, 150, 255),
                (50, 220, 100), (240, 240, 240), (255, 140, 0)
            ]
        for _ in range(count):
            color = random.choice(colors)
            angle = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
            speed = random.uniform(180, 550)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(1.2, 2.5)
            radius = random.uniform(3.0, 6.0)
            rot_speed = random.uniform(-360, 360)
            self.particles.append(
                Particle(
                    x=x + random.uniform(-50, 50),
                    y=y + random.uniform(-20, 20),
                    vx=vx,
                    vy=vy,
                    color=color,
                    radius=radius,
                    lifetime=lifetime,
                    gravity=350.0,
                    drag=0.98,
                    shape="confetti",
                    rotation_speed=rot_speed
                )
            )

    def spawn_sparks(self, x: float, y: float, count: int = 25, color: Tuple[int, int, int] = (255, 230, 120)) -> None:
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 400)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.2, 0.6)
            radius = random.uniform(2.0, 4.0)
            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=vx,
                    vy=vy,
                    color=color,
                    radius=radius,
                    lifetime=lifetime,
                    gravity=150.0,
                    drag=0.92,
                    shape="circle"
                )
            )

    def spawn_dust(self, x: float, y: float, count: int = 15) -> None:
        for _ in range(count):
            angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2)
            speed = random.uniform(40, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.3, 0.7)
            radius = random.uniform(3.0, 7.0)
            dust_color = (200, 220, 180)
            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=vx,
                    vy=vy,
                    color=dust_color,
                    radius=radius,
                    lifetime=lifetime,
                    gravity=-20.0,
                    drag=0.90,
                    shape="circle"
                )
            )

    def spawn_trail(self, x: float, y: float, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        self.particles.append(
            Particle(
                x=x + random.uniform(-2, 2),
                y=y + random.uniform(-2, 2),
                vx=random.uniform(-10, 10),
                vy=random.uniform(-10, 10),
                color=color,
                radius=random.uniform(4.0, 8.0),
                lifetime=0.25,
                gravity=0.0,
                drag=0.85,
                shape="circle"
            )
        )

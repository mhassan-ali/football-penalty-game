import unittest
import pygame
from game.particles import Particle, ParticleSystem

class TestParticleSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_particle_update(self):
        p = Particle(100, 100, 10, 20, (255, 0, 0), 5.0, 1.0, gravity=100.0)
        alive = p.update(0.1)
        self.assertTrue(alive)
        self.assertAlmostEqual(p.x, 101.0)
        self.assertTrue(p.y > 100.0)

    def test_particle_system_spawning(self):
        ps = ParticleSystem()
        self.assertEqual(len(ps.particles), 0)

        ps.spawn_confetti(640, 360, count=20)
        self.assertEqual(len(ps.particles), 20)

        ps.spawn_sparks(400, 200, count=10)
        self.assertEqual(len(ps.particles), 30)

        ps.spawn_dust(640, 600, count=5)
        self.assertEqual(len(ps.particles), 35)

        ps.spawn_trail(640, 500)
        self.assertEqual(len(ps.particles), 36)

        # Update until particles expire
        ps.update(3.0)
        self.assertEqual(len(ps.particles), 0)

    def test_particle_draw(self):
        ps = ParticleSystem()
        ps.spawn_confetti(640, 360, count=5)
        surface = pygame.Surface((1280, 720))
        # Draw shouldn't throw error
        ps.draw(surface)

if __name__ == "__main__":
    unittest.main()

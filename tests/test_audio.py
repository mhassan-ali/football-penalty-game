import unittest
import pygame
from managers.audio_manager import AudioManager
from managers.save_manager import SaveManager
from core.scene_manager import SceneManager
from scenes.base import Scene

class MockScene(Scene):
    def __init__(self, name: str):
        super().__init__(name)
        self.entered = False
        self.exited = False

    def on_enter(self, **kwargs):
        self.entered = True

    def on_exit(self):
        self.exited = True

class TestAudioAndTransitions(unittest.TestCase):
    def setUp(self) -> None:
        pygame.init()
        # Initialize mixer if not already initialized
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                pass

    def test_audio_manager_synth_and_volumes(self):
        # Test creation and sound synthesis
        am = AudioManager()
        
        # Verify synthesized sound objects exist
        self.assertIn("music", am.sounds)
        self.assertIn("kick", am.sounds)
        self.assertIn("whistle", am.sounds)
        self.assertIn("post_hit", am.sounds)
        self.assertIn("fanfare", am.sounds)
        self.assertIn("gasp", am.sounds)
        
        # Test updating volumes with mock save manager
        class MockSaveManager:
            def __init__(self):
                self.data = {
                    "settings": {
                        "master_volume": 0.5,
                        "music_volume": 0.6,
                        "sfx_volume": 0.7
                    }
                }
        
        sm = MockSaveManager()
        am.save_manager = sm
        am.update_volumes()
        
        # Play calls (should run without error)
        am.play_music()
        am.play_ambience()
        am.play_sfx("kick")
        am.stop_music()
        am.stop_ambience()

    def test_scene_transitions_flow(self):
        sm = SceneManager()
        scene_a = MockScene("A")
        scene_b = MockScene("B")
        
        sm.register_scene("A", scene_a)
        sm.register_scene("B", scene_b)
        
        # Boot initial scene
        sm.switch_scene("A")
        self.assertEqual(sm.active_scene.name, "A")
        self.assertTrue(scene_a.entered)
        
        # Switch to B with transition enabled
        sm.transitions_enabled = True
        sm.switch_scene("B")
        
        # Immediately, active scene is STILL A (fading out)
        self.assertEqual(sm.active_scene.name, "A")
        self.assertEqual(sm._transition_state, "fade_out")
        
        # Update part-way through fade out
        sm.update(0.1)
        self.assertEqual(sm.active_scene.name, "A")
        
        # Update past the transition speed to complete fade out
        # Transition speed is 650.0 alpha/sec, so 0.5s is 325 alpha, which completes it
        sm.update(0.5)
        
        # Now active scene is B, and we are in fade_in state
        self.assertEqual(sm.active_scene.name, "B")
        self.assertTrue(scene_a.exited)
        self.assertTrue(scene_b.entered)
        self.assertEqual(sm._transition_state, "fade_in")
        
        # Update to complete fade_in
        sm.update(0.5)
        self.assertEqual(sm._transition_state, None)
        self.assertIsNone(sm._transition_target)

import unittest
import os
import shutil
import json
from typing import Any
from core.event_manager import EventManager
from core.state_manager import StateManager, State
from core.scene_manager import SceneManager
from scenes.base import Scene
from managers.config_manager import ConfigManager

class MockScene(Scene):
    def __init__(self, name: str):
        super().__init__(name)
        self.entered = False
        self.exited = False
        self.enter_args = {}
        self.update_dt = None
        self.events_handled = []

    def on_enter(self, **kwargs: Any) -> None:
        self.entered = True
        self.enter_args = kwargs

    def on_exit(self) -> None:
        self.exited = True

    def update(self, dt: float) -> None:
        self.update_dt = dt

    def handle_event(self, event: Any) -> None:
        self.events_handled.append(event)


class TestEventManager(unittest.TestCase):
    def test_pub_sub(self):
        em = EventManager()
        called = False
        payload = None

        def handler(data):
            nonlocal called, payload
            called = True
            payload = data

        em.subscribe("test_event", handler)
        em.publish("test_event", "hello")

        self.assertTrue(called)
        self.assertEqual(payload, "hello")

    def test_unsubscribe(self):
        em = EventManager()
        call_count = 0

        def handler(data):
            nonlocal call_count
            call_count += 1

        em.subscribe("test_event", handler)
        em.publish("test_event")
        em.unsubscribe("test_event", handler)
        em.publish("test_event")

        self.assertEqual(call_count, 1)

    def test_handler_error_isolation(self):
        em = EventManager()
        called_good = False

        def handler_bad(data):
            raise RuntimeError("Something failed")

        def handler_good(data):
            nonlocal called_good
            called_good = True

        em.subscribe("test_event", handler_bad)
        em.subscribe("test_event", handler_good)
        
        # Publish should not crash and should execute the good handler
        em.publish("test_event")
        self.assertTrue(called_good)


class TestStateManager(unittest.TestCase):
    def test_initial_state(self):
        em = EventManager()
        sm = StateManager(em, State.LOADING)
        self.assertEqual(sm.current_state, State.LOADING)

    def test_valid_transition(self):
        em = EventManager()
        sm = StateManager(em, State.LOADING)
        
        event_fired = False
        def on_change(data):
            nonlocal event_fired
            self.assertEqual(data["old_state"], State.LOADING)
            self.assertEqual(data["new_state"], State.MAIN_MENU)
            event_fired = True
            
        em.subscribe("state_changed", on_change)
        
        self.assertTrue(sm.change_state(State.MAIN_MENU))
        self.assertEqual(sm.current_state, State.MAIN_MENU)
        self.assertTrue(event_fired)

    def test_invalid_transition(self):
        em = EventManager()
        sm = StateManager(em, State.LOADING)
        
        with self.assertRaises(ValueError):
            sm.change_state(State.PAUSED)  # Loading -> Paused is invalid


class TestSceneManager(unittest.TestCase):
    def test_registration_and_switching(self):
        sm = SceneManager()
        scene_a = MockScene("a")
        scene_b = MockScene("b")

        sm.register_scene("a", scene_a)
        sm.register_scene("b", scene_b)

        # Initially no active scene
        self.assertIsNone(sm.active_scene)

        # Switch to A
        sm.switch_scene("a", x=10)
        self.assertEqual(sm.active_scene, scene_a)
        self.assertTrue(scene_a.entered)
        self.assertEqual(scene_a.enter_args, {"x": 10})

        # Switch to B
        sm.switch_scene("b")
        self.assertEqual(sm.active_scene, scene_b)
        self.assertTrue(scene_a.exited)
        self.assertTrue(scene_b.entered)

    def test_routing(self):
        sm = SceneManager()
        scene = MockScene("a")
        sm.register_scene("a", scene)
        sm.switch_scene("a")

        sm.update(0.16)
        self.assertEqual(scene.update_dt, 0.16)

        sm.handle_event("test_event")
        self.assertIn("test_event", scene.events_handled)


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_config"
        self.test_file = os.path.join(self.test_dir, "settings.json")
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_default_creation(self):
        cm = ConfigManager(self.test_file)
        self.assertTrue(os.path.exists(self.test_file))
        self.assertEqual(cm.get("display.width"), 1280)
        self.assertEqual(cm.get("gameplay.target_fps"), 60)

    def test_custom_loading_and_validation(self):
        # Create directory
        os.makedirs(self.test_dir, exist_ok=True)
        # Write valid custom settings
        custom = {
            "display": {
                "width": 1920,
                "height": 1080,
                "fullscreen": True,
                "title": "Custom Title"
            },
            "gameplay": {
                "target_fps": 120
            },
            "audio": {
                "master_volume": 0.5
            }
        }
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(custom, f)

        cm = ConfigManager(self.test_file)
        self.assertEqual(cm.get("display.width"), 1920)
        self.assertEqual(cm.get("display.height"), 1080)
        self.assertTrue(cm.get("display.fullscreen"))
        self.assertEqual(cm.get("display.title"), "Custom Title")
        self.assertEqual(cm.get("gameplay.target_fps"), 120)
        self.assertEqual(cm.get("audio.master_volume"), 0.5)
        # Checks if unmodified field holds default
        self.assertEqual(cm.get("audio.music_volume"), 0.8)

    def test_validation_fallback(self):
        os.makedirs(self.test_dir, exist_ok=True)
        # Write invalid settings
        custom = {
            "display": {
                "width": 99999,  # Invalid: out of bounds
                "height": "not an int",  # Invalid: type
            },
            "audio": {
                "master_volume": -0.5  # Invalid: out of range
            }
        }
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(custom, f)

        cm = ConfigManager(self.test_file)
        # Should fallback to defaults
        self.assertEqual(cm.get("display.width"), 1280)
        self.assertEqual(cm.get("display.height"), 720)
        self.assertEqual(cm.get("audio.master_volume"), 1.0)

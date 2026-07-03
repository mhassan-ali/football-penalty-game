import math
import struct
import pygame
import logging
from typing import Any, Optional, Dict

logger = logging.getLogger("AudioManager")

class AudioManager:
    def __init__(self, save_manager: Optional[Any] = None) -> None:
        self.save_manager = save_manager
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_channel: Optional[pygame.mixer.Channel] = None
        self.ambience_channel: Optional[pygame.mixer.Channel] = None
        self.mixer_initialized = pygame.mixer.get_init() is not None
        
        if self.mixer_initialized:
            self._generate_sounds()
            self._setup_channels()
            self.update_volumes()
            logger.info("AudioManager successfully initialized and synthesized sounds.")
        else:
            logger.warning("Pygame mixer not initialized. AudioManager running in silent mode.")

    def _setup_channels(self) -> None:
        if not self.mixer_initialized:
            return
        # Channel 0 for looping background music
        self.music_channel = pygame.mixer.Channel(0)
        # Channel 1 for looping crowd ambience
        self.ambience_channel = pygame.mixer.Channel(1)

    def _generate_sounds(self) -> None:
        """Synthesizes PCM audio data in memory for self-contained, lightweight audio."""
        try:
            self.sounds["music"] = self._create_music_track()
            self.sounds["ambience"] = self._create_ambience()
            self.sounds["kick"] = self._create_kick()
            self.sounds["whistle"] = self._create_whistle()
            self.sounds["goal"] = self._create_goal_cheer()
            self.sounds["save"] = self._create_save_clap()
            self.sounds["click"] = self._create_click()
            self.sounds["hover"] = self._create_hover()
        except Exception as e:
            logger.error(f"Error generating synthesized sounds: {e}")

    def update_volumes(self) -> None:
        """Applies volume settings from save_manager configuration to the mixer channels."""
        if not self.mixer_initialized:
            return
        
        master_vol = 1.0
        music_vol = 0.8
        sfx_vol = 0.9

        if self.save_manager and "settings" in self.save_manager.data:
            settings = self.save_manager.data["settings"]
            master_vol = settings.get("master_volume", 1.0)
            music_vol = settings.get("music_volume", 0.8)
            sfx_vol = settings.get("sfx_volume", 0.9)

        # Apply volumes
        effective_music = master_vol * music_vol
        effective_sfx = master_vol * sfx_vol

        if self.music_channel:
            self.music_channel.set_volume(effective_music)
        if self.ambience_channel:
            self.ambience_channel.set_volume(effective_sfx * 0.6) # ambient background hum should be softer

        # Update volume on all standalone sound objects
        for name, snd in self.sounds.items():
            if name == "music":
                snd.set_volume(effective_music)
            elif name == "ambience":
                snd.set_volume(effective_sfx * 0.6)
            else:
                snd.set_volume(effective_sfx)

    def play_music(self) -> None:
        if not self.mixer_initialized or not self.music_channel:
            return
        if "music" in self.sounds and not self.music_channel.get_busy():
            self.music_channel.play(self.sounds["music"], loops=-1)
            logger.debug("Playing background music.")

    def stop_music(self) -> None:
        if not self.mixer_initialized or not self.music_channel:
            return
        self.music_channel.stop()
        logger.debug("Stopped background music.")

    def play_ambience(self) -> None:
        if not self.mixer_initialized or not self.ambience_channel:
            return
        if "ambience" in self.sounds and not self.ambience_channel.get_busy():
            self.ambience_channel.play(self.sounds["ambience"], loops=-1)
            logger.debug("Playing crowd ambience.")

    def stop_ambience(self) -> None:
        if not self.mixer_initialized or not self.ambience_channel:
            return
        self.ambience_channel.stop()
        logger.debug("Stopped crowd ambience.")

    def play_sfx(self, name: str) -> None:
        if not self.mixer_initialized:
            return
        snd = self.sounds.get(name)
        if snd:
            # Find a free channel or let pygame pick a channel (channels 2 and above)
            channel = pygame.mixer.find_channel(True)
            if channel:
                # Make sure we don't play sfx on music/ambience reserved channels
                if channel.get_id() >= 2:
                    channel.play(snd)
            else:
                # Fallback to direct play if no free channels
                snd.play()

    # --- PCM Audio Synthesizers ---

    def _create_music_track(self, duration: float = 8.0, sample_rate: int = 22050) -> pygame.mixer.Sound:
        num_samples = int(duration * sample_rate)
        buffer = bytearray()
        chords = [
            [130.81, 155.56, 196.00, 261.63], # Cm (C3, Eb3, G3, C4)
            [103.83, 130.81, 155.56, 207.65], # Ab
            [87.31, 103.83, 130.81, 174.61],  # Fm
            [98.00, 123.47, 146.83, 196.00]   # G
        ]
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            beat = int(t / 0.5) % 16
            chord_idx = (beat // 4) % 4
            chord = chords[chord_idx]
            
            arp_step = int(t / 0.125) % 4
            freq = chord[arp_step]
            
            note_t = t % 0.125
            env = math.exp(-25.0 * note_t)
            
            wave = math.sin(2.0 * math.pi * freq * t)
            if wave > 0:
                wave = 0.5
            else:
                wave = -0.5
                
            bass_freq = chord[0] / 2.0
            bass_env = math.exp(-10.0 * (t % 0.5))
            bass_wave = math.sin(2.0 * math.pi * bass_freq * t)
            
            mix = (wave * 0.12 * env + bass_wave * 0.22 * bass_env)
            val = int(32767 * mix)
            buffer.extend(struct.pack("<h", val))
            
        return pygame.mixer.Sound(buffer=bytes(buffer))

    def _create_ambience(self, duration: float = 4.0, sample_rate: int = 22050) -> pygame.mixer.Sound:
        num_samples = int(duration * sample_rate)
        buffer = bytearray()
        import random
        for i in range(num_samples):
            t = float(i) / sample_rate
            rumble = (math.sin(2.0 * math.pi * 55.0 * t) + 
                      math.sin(2.0 * math.pi * 73.0 * t) + 
                      math.sin(2.0 * math.pi * 98.0 * t)) / 3.0
            noise = random.uniform(-1.0, 1.0) * 0.15
            mod = 0.8 + 0.2 * math.sin(2.0 * math.pi * 0.5 * t)
            val = int(32767 * 0.35 * (rumble + noise) * mod)
            buffer.extend(struct.pack("<h", val))
        return pygame.mixer.Sound(buffer=bytes(buffer))

    def _create_kick(self, duration: float = 0.2, sample_rate: int = 22050) -> pygame.mixer.Sound:
        num_samples = int(duration * sample_rate)
        buffer = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            freq = 150.0 * math.exp(-20.0 * t) + 30.0
            env = math.exp(-15.0 * t)
            val = int(32767 * 0.85 * env * math.sin(2.0 * math.pi * freq * t))
            buffer.extend(struct.pack("<h", val))
        return pygame.mixer.Sound(buffer=bytes(buffer))

    def _create_whistle(self, duration: float = 0.4, sample_rate: int = 22050) -> pygame.mixer.Sound:
        num_samples = int(duration * sample_rate)
        buffer = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            wave1 = math.sin(2.0 * math.pi * 1000.0 * t)
            wave2 = math.sin(2.0 * math.pi * 1030.0 * t)
            vib = 1.0 + 0.12 * math.sin(2.0 * math.pi * 60.0 * t)
            val = int(32767 * 0.45 * (wave1 + wave2) * vib)
            if t > duration - 0.08:
                val = int(val * (duration - t) / 0.08)
            buffer.extend(struct.pack("<h", val))
        return pygame.mixer.Sound(buffer=bytes(buffer))

    def _create_goal_cheer(self, duration: float = 1.5, sample_rate: int = 22050) -> pygame.mixer.Sound:
        num_samples = int(duration * sample_rate)
        buffer = bytearray()
        import random
        for i in range(num_samples):
            t = float(i) / sample_rate
            noise = random.uniform(-1.0, 1.0)
            rumble = math.sin(2.0 * math.pi * 80.0 * t)
            chord = (math.sin(2.0 * math.pi * 261.63 * t) + 
                     math.sin(2.0 * math.pi * 329.63 * t) + 
                     math.sin(2.0 * math.pi * 392.00 * t)) / 3.0
            if t < 0.1:
                env = t / 0.1
            else:
                env = math.exp(-1.5 * (t - 0.1))
            mix = (noise * 0.45 + rumble * 0.25 + chord * 0.3) * env
            val = int(32767 * 0.75 * mix)
            buffer.extend(struct.pack("<h", val))
        return pygame.mixer.Sound(buffer=bytes(buffer))

    def _create_save_clap(self, duration: float = 0.25, sample_rate: int = 22050) -> pygame.mixer.Sound:
        num_samples = int(duration * sample_rate)
        buffer = bytearray()
        import random
        for i in range(num_samples):
            t = float(i) / sample_rate
            noise = random.uniform(-1.0, 1.0)
            freq = 300.0 * math.exp(-35.0 * t) + 50.0
            thud = math.sin(2.0 * math.pi * freq * t)
            env = math.exp(-25.0 * t)
            mix = (noise * 0.35 + thud * 0.65) * env
            val = int(32767 * 0.85 * mix)
            buffer.extend(struct.pack("<h", val))
        return pygame.mixer.Sound(buffer=bytes(buffer))

    def _create_click(self, duration: float = 0.05, sample_rate: int = 22050) -> pygame.mixer.Sound:
        num_samples = int(duration * sample_rate)
        buffer = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            val = int(32767 * 0.35 * math.exp(-50.0 * t) * math.sin(2.0 * math.pi * 1000.0 * t))
            buffer.extend(struct.pack("<h", val))
        return pygame.mixer.Sound(buffer=bytes(buffer))

    def _create_hover(self, duration: float = 0.03, sample_rate: int = 22050) -> pygame.mixer.Sound:
        num_samples = int(duration * sample_rate)
        buffer = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            val = int(32767 * 0.18 * math.exp(-80.0 * t) * math.sin(2.0 * math.pi * 600.0 * t))
            buffer.extend(struct.pack("<h", val))
        return pygame.mixer.Sound(buffer=bytes(buffer))

import logging
import pygame
from typing import Dict, Optional, Tuple

logger = logging.getLogger("AssetManager")

class AssetManager:
    def __init__(self) -> None:
        self._image_cache: Dict[str, pygame.Surface] = {}
        self._font_cache: Dict[Tuple[str, int], pygame.font.Font] = {}
        
        # Ensure pygame font module is initialized
        if not pygame.font.get_init():
            try:
                pygame.font.init()
            except Exception as e:
                logger.error(f"Failed to initialize pygame font module: {e}")
                
        logger.info("AssetManager initialized (basic structure only, no real assets loaded).")

    def get_image(self, name: str, size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
        """
        Retrieves a cached image surface or generates a colored placeholder surface.
        
        Args:
            name: Logical asset key.
            size: Dimension tuple to scale/size the placeholder.
        """
        cache_key = f"{name}_{size}"
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        # Generate a placeholder surface (solid color)
        width, height = size if size else (64, 64)
        surf = pygame.Surface((width, height))
        
        # Deterministic color based on the name hash
        col_r = (hash(name) % 180) + 50
        col_g = (hash(name + "g") % 180) + 50
        col_b = (hash(name + "b") % 180) + 50
        surf.fill((col_r, col_g, col_b))
        
        self._image_cache[cache_key] = surf
        logger.debug(f"Generated placeholder image for key '{name}' (size: {width}x{height})")
        return surf

    def get_font(self, name: str, size: int) -> pygame.font.Font:
        """
        Retrieves a cached Font instance. Falls back to default system font.
        
        Args:
            name: Logical font key (ignored in placeholder mode).
            size: Font size in pixels.
        """
        cache_key = (name, size)
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        # Fallback to Pygame's default system font
        try:
            # None loads the default Pygame font
            font = pygame.font.Font(None, size)
        except Exception as e:
            logger.warning(f"Could not load Pygame default font: {e}. Trying system font...")
            try:
                font = pygame.font.SysFont("arial", size)
            except Exception as se:
                logger.error(f"Failed to load any fallback font: {se}")
                raise se

        self._font_cache[cache_key] = font
        return font

    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """
        Mock retrieval of a Sound asset.
        
        Args:
            name: Logical sound key.
        """
        logger.debug(f"Mock loading sound: {name}")
        return None

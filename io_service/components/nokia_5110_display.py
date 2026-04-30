from __future__ import annotations

from typing import Any, Dict, Optional

from io_service.components.nokia_5110_display_config import Nokia5110DisplayConfig


class Nokia5110Display:

    # --------------------------------------------------------------------------------
    # CONSTRUCTORS
    # --------------------------------------------------------------------------------

    def __init__(self, config: Nokia5110DisplayConfig) -> None:
        self._config = config
        self._device = None
        self._image = None
        self._draw = None
        self._available = False
        self._last_text = ''
        self._last_error: Optional[str] = None

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    def config(self) -> None:
        if not self._config.enabled:
            self._last_error = 'Display is disabled by configuration.'
            return

        try:
            from luma.core.interface.serial import spi
            from luma.lcd.device import pcd8544
            from PIL import Image, ImageDraw
        except ImportError as e:
            self._last_error = f'Display libraries are not installed: {e.name}'
            return

        try:
            serial = spi(
                port=self._config.spi_port,
                device=self._config.spi_device,
                gpio_DC=self._config.dc_pin,
                gpio_RST=self._config.rst_pin,
            )
            self._device = pcd8544(serial, width=self._config.width, height=self._config.height)
            self._device.contrast(self._config.contrast)
            self._image = Image.new('1', (self._config.width, self._config.height), 0)
            self._draw = ImageDraw.Draw(self._image)
            self._available = True
            self.clear()
        except Exception as e:
            self._last_error = f'Failed to initialize Nokia 5110 display: {e}'

    def loop(self) -> None:
        return None

    def clear(self) -> None:
        if not self._available:
            self._last_text = ''
            return
        self._draw.rectangle((0, 0, self._config.width, self._config.height), outline=0, fill=0)
        self._device.display(self._image)
        self._last_text = ''

    def show_text(self, text: str, x: int = 0, y: int = 0, clear: bool = True) -> Dict[str, Any]:
        self._last_text = text
        if not self._available:
            return self.status()

        if clear:
            self._draw.rectangle((0, 0, self._config.width, self._config.height), outline=0, fill=0)
        self._draw.text((x, y), text, fill=255)
        self._device.display(self._image)
        return self.status()

    def status(self) -> Dict[str, Any]:
        return {
            'name': 'nokia_5110_display',
            'available': self._available,
            'enabled': self._config.enabled,
            'width': self._config.width,
            'height': self._config.height,
            'last_text': self._last_text,
            'last_error': self._last_error,
        }

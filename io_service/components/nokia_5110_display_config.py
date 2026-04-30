from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Nokia5110DisplayConfig:
    width: int
    height: int
    contrast: int
    spi_port: int
    spi_device: int
    dc_pin: int
    rst_pin: int
    backlight_pin: Optional[str] = None
    enabled: bool = True

from __future__ import annotations

from datetime import datetime
import signal
import time

from io_service import config as service_config
from io_service.components.nokia_5110_display import Nokia5110Display
from io_service.components.nokia_5110_display_config import Nokia5110DisplayConfig
from io_service.core.http_client import HttpClient
from io_service.core.internal_server import InternalServer
from io_service.models.display_text import DisplayText
from io_service.models.io_command import IOCommand
from io_service.models.io_response import IOResponse
from io_service.models.io_status import IOStatus


class IOService:

    # --------------------------------------------------------------------------------
    # CONSTRUCTORS
    # --------------------------------------------------------------------------------

    def __init__(self) -> None:
        self._running = False
        self._loop_count = 0
        self._display = Nokia5110Display(Nokia5110DisplayConfig(
            enabled=service_config.DISPLAY_ENABLED,
            width=service_config.DISPLAY_WIDTH,
            height=service_config.DISPLAY_HEIGHT,
            contrast=service_config.DISPLAY_CONTRAST,
            spi_port=service_config.DISPLAY_SPI_PORT,
            spi_device=service_config.DISPLAY_SPI_DEVICE,
            dc_pin=service_config.DISPLAY_DC_PIN,
            rst_pin=service_config.DISPLAY_RST_PIN,
            backlight_pin=service_config.DISPLAY_BACKLIGHT_PIN,
        ))
        self._internal_server = InternalServer(service_config.SOCKET_PATH, self._handle_command)
        self._api_client = HttpClient(service_config.API_SERVICE_URL, timeout=service_config.HTTP_TIMEOUT_SECONDS)

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    def config(self) -> None:
        signal.signal(signal.SIGTERM, self._handle_stop_signal)
        signal.signal(signal.SIGINT, self._handle_stop_signal)
        self._display.config()
        self._internal_server.start()

    def run(self) -> None:
        self._running = True
        while self._running:
            self.loop()
            time.sleep(service_config.LOOP_INTERVAL_SECONDS)
        self._internal_server.stop()

    def loop(self) -> None:
        self._loop_count += 1
        self._display.loop()

    # --------------------------------------------------------------------------------
    # COMMANDS
    # --------------------------------------------------------------------------------

    def _handle_command(self, command: IOCommand) -> IOResponse:
        action = command.action.strip().casefold()
        if action == 'status':
            return IOResponse(ok=True, data=self._status().to_public())
        if action == 'display.clear':
            self._display.clear()
            return IOResponse(ok=True, data=self._display.status())
        if action == 'display.text':
            text = DisplayText.from_dict(command.payload)
            return IOResponse(ok=True, data=self._display.show_text(text.text, x=text.x, y=text.y, clear=text.clear))
        if action == 'stop':
            self._running = False
            return IOResponse(ok=True, data={'stopping': True})

        return IOResponse(ok=False, error=f'Unknown IO command: {command.action}')

    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    def _status(self) -> IOStatus:
        return IOStatus(
            service=service_config.SERVICE_NAME,
            running=self._running,
            loop_count=self._loop_count,
            updated_at=datetime.now(),
            components={
                'display': self._display.status(),
            },
        )

    def _handle_stop_signal(self, _signum, _frame) -> None:
        self._running = False

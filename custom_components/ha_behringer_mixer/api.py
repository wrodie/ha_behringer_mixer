"""Sample API Client."""
from __future__ import annotations
import logging
import asyncio
from .behringer_mixer import mixer_api


class BehringerMixerApiClientError(Exception):
    """Exception to indicate a general API error."""


class BehringerMixerApiClientCommunicationError(BehringerMixerApiClientError):
    """Exception to indicate a communication error."""


class BehringerMixerApiClientAuthenticationError(BehringerMixerApiClientError):
    """Exception to indicate an authentication error."""


class BehringerMixerApiClient:
    """Sample API Client."""

    def __init__(self, mixer_ip: str, mixer_type: str) -> None:
        """Sample API Client."""
        self._mixer_ip = mixer_ip
        self._mixer_type = mixer_type
        self._state = {}
        self._num_channels = 0
        self._num_bus = 0
        self._num_matrix = 0
        self._num_dca = 0
        self._mixer = None
        self.tasks = set()
        self.coordinator = None

    async def setup(self):
        """Setup the server"""
        print(f"CONNECT {self._mixer_type} : {self._mixer_ip}")
        self._mixer = mixer_api.connect(
            self._mixer_type, ip=self._mixer_ip, logLevel=logging.WARNING
        )
        await self._mixer.connectserver()
        # Get Initial state first
        await self._mixer.reload()
        # Setup subscription for live updates
        task = asyncio.create_task(self._mixer.subscribe(self.new_data_callback))
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

        return True

    async def async_get_data(self) -> any:
        """Get data from the API."""
        return self._mixer.state()

    async def async_set_value(self, address: str, value: str) -> any:
        """Set data"""
        return await self._mixer.set_value(address, value)

    def new_data_callback(self, data: dict):
        """Callback function to receive new data from the mixer"""
        if self.coordinator:
            self.coordinator.async_update_listeners()
        return True

    def register_coordinator(self, coordinator):
        """ register the coordinator object """
        self.coordinator = coordinator

"""API Client. to connect to Behringer mixer."""
from __future__ import annotations
import logging
import asyncio
from behringer_mixer import mixer_api


class BehringerMixerApiClientError(Exception):
    """Exception to indicate a general API error."""


class BehringerMixerApiClientCommunicationError(BehringerMixerApiClientError):
    """Exception to indicate a communication error."""


class BehringerMixerApiClientAuthenticationError(BehringerMixerApiClientError):
    """Exception to indicate an authentication error."""


class BehringerMixerApiClient:
    """Behringer Mixer API Client."""

    def __init__(self, mixer_ip: str, mixer_type: str) -> None:
        """Initialise the API Client."""
        self._mixer_ip = mixer_ip
        self._mixer_type = mixer_type
        self._state = {}
        self._mixer = None
        self.tasks = set()
        self.coordinator = None

    async def setup(self):
        """Set up everything necessary."""
        self._mixer = mixer_api.create(
            self._mixer_type, ip=self._mixer_ip, logLevel=logging.WARNING, delay=0.002
        )
        await self._mixer.start()
        # Get Initial state first
        await self._mixer.reload()
        # Setup subscription for live updates
        task = asyncio.create_task(self._mixer.subscribe(self.new_data_callback))
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return True

    def mixer_info(self):
        """Return the mixer info."""
        return self._mixer.info()

    async def async_get_data(self) -> any:
        """Get data from the API."""
        return self._mixer.state()

    async def async_set_value(self, address: str, value: str) -> any:
        """Set a specific value on the mixer."""
        return await self._mixer.set_value(address, value)

    async def load_scene(self, scene_number):
        """Change the scene."""
        return await self._mixer.load_scene(scene_number)

    def new_data_callback(self, data: dict):  # pylint: disable=unused-argument
        """Handle the callback indicating new data has been received."""
        if self.coordinator:
            self.coordinator.async_update_listeners()
        return True

    def register_coordinator(self, coordinator):
        """Register the coordinator object."""
        self.coordinator = coordinator

    def stop(self):
        """Shutdown the client."""
        self._mixer.unsubscribe()
        self._mixer.stop()

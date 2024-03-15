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

    async def setup(self, test_connection_only=False):
        """Set up everything necessary."""
        self._mixer = mixer_api.create(
            self._mixer_type, ip=self._mixer_ip, logLevel=logging.WARNING, delay=0.002
        )
        await self._mixer.start()
        if not test_connection_only:
            # Get Initial state first
            await self._mixer.reload()
            # Setup subscription for live updates
            task = asyncio.create_task(self._mixer.subscribe(self.new_data_callback))
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)
            task_sub_status = asyncio.create_task(
                self._mixer.subscription_status_register(
                    self.subscription_status_callback
                )
            )
            self.tasks.add(task_sub_status)
            task_sub_status.add_done_callback(self.tasks.discard)
        return True

    def mixer_info(self):
        """Return the mixer info."""
        return self._mixer.info()

    def mixer_network_name(self):
        """Return the mixer network_name."""
        return self._mixer.name()

    async def async_get_data(self) -> any:
        """Get data from the API."""
        return self._get_data()

    def _get_data(self) -> any:
        """Process the internal data from the API."""
        data = self._mixer.state()
        data["/firmware"] = self._mixer.firmware()
        data["/available"] = self._mixer.subscription_connected()
        return data

    async def async_set_value(self, address: str, value: str) -> any:
        """Set a specific value on the mixer."""
        return await self._mixer.set_value(address, value)

    async def load_scene(self, scene_number):
        """Change the scene."""
        return await self._mixer.load_scene(scene_number)

    def new_data_callback(self, data: dict):
        """Handle the callback indicating new data has been received."""
        if data and data.get("property") and data.get("property").endswith("_db"):
            return True
        if self.coordinator:
            self.coordinator.async_set_updated_data(self._get_data())
        return True

    def subscription_status_callback(self, subscription_connection):
        """Handle the callback indicating the status of the subscription connection."""
        if self.coordinator:
            self.coordinator.sub_connected = subscription_connection
        self.new_data_callback({})
        return True

    def register_coordinator(self, coordinator):
        """Register the coordinator object."""
        self.coordinator = coordinator

    async def stop(self):
        """Shutdown the client."""
        await self._mixer.unsubscribe()
        await self._mixer.stop()

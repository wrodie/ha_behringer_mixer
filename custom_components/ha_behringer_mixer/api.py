"""Sample API Client."""
from __future__ import annotations
import logging
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

    async def setup(self):
        """Setup the server"""
        print(f"CONNECT {self._mixer_type} : {self._mixer_ip}")
        self._mixer = mixer_api.connect(
            self._mixer_type, ip=self._mixer_ip, logLevel=logging.WARNING
        )
        await self._mixer.connectserver()
        # await self._mixer.subscribe(self.new_data_callback)
        return True

    async def async_get_data(self) -> any:
        """Get data from the API."""
        await self._mixer.reload()
        return self._mixer.state()

    async def async_set_value(self, address: str, value: str) -> any:
        """Set data"""
        return await self._mixer.set_value(address, value)

    async def new_data_callback(self, data: dict):
        """Callback function to receive new data from the mixer"""
        print("CB")
        print(data)
        return True

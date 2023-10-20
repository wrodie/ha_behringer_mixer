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
        print(f"CONNECT {self._mixer_type} : {self._mixer_ip}")
        self._mixer = mixer_api.connect(
            self._mixer_type, ip=self._mixer_ip, logLevel=logging.WARNING
        )

    async def async_get_data(self) -> any:
        """Get data from the API."""
        await self._mixer.connectserver()
        await self._mixer.reload()
        #self._generate_state()
        #self._update_mixer_counts()
        return self._mixer.state()

    async def async_set_value(self, address: str, value: str) -> any:
        """Set data"""
        return await self._mixer.set_value(address, value)

    def _update_mixer_counts(self):
        "Using the data coming back from the state set number of channels etc"
        self._num_channels = len(self._state.get("ch") or [])
        self._num_bus = len(self._state.get("bus") or [])
        self._num_dca = len(self._state.get("dca") or [])

    def _generate_state(self):
        "Split the incoming data into groups and save as state"
        state = self._mixer.state()
        split_state = {}
        for key in sorted(state.keys()):
            value = state[key]
            key_path = key.split('/') or []
            state_level = split_state
            for key_part in key_path[1:-1]:
                state_level.setdefault(key_part, {})
                state_level = state_level[key_part]
            state_level[key_path[-1]] = value
        self._state = split_state
        return True

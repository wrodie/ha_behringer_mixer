"""Adds config flow for BehringerMixer."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers import config_validation as cv

from .api import (
    BehringerMixerApiClient,
    BehringerMixerApiClientAuthenticationError,
    BehringerMixerApiClientCommunicationError,
    BehringerMixerApiClientError,
)
from .const import DOMAIN, LOGGER


class BehringerMixerFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for BehringerMixer."""

    VERSION = 4

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                user_input["NAME_DEFAULT"] = await self._test_connect(
                    mixer_ip=user_input["MIXER_IP"],
                    mixer_type=user_input["MIXER_TYPE"],
                )
            except BehringerMixerApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except BehringerMixerApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except BehringerMixerApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                self.init_info = user_input
                return await self.async_step_name(user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("MIXER_IP"): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required("MIXER_TYPE", default="X32"): vol.In(
                        ["X32", "XR12", "XR16", "XR18"]
                    ),
                }
            ),
            errors=_errors,
        )

    @staticmethod
    def create_list(max_number):
        """Create a list of numbers."""
        return list(range(1, max_number + 1))

    async def async_step_name(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""

        _errors = {}
        if user_input is not None and user_input.get("NAME"):
            self.init_info["NAME"] = user_input["NAME"]
            self.init_info["CHANNEL_CONFIG"] = user_input["CHANNELS"]
            self.init_info["BUS_CONFIG"] = user_input["BUSSES"]
            self.init_info["DCA_CONFIG"] = user_input["DCAS"]
            self.init_info["MATRIX_CONFIG"] = user_input["MATRICES"]
            self.init_info["AUXIN_CONFIG"] = user_input["AUXINS"]
            self.init_info["MAIN_CONFIG"] = user_input["MAIN"] or False
            self.init_info["CHANNELSENDS_CONFIG"] = user_input["CHANNELSENDS"] or False
            self.init_info["BUSSENDS_CONFIG"] = user_input["BUSSENDS"] or False
            self.init_info["DBSENSORS"] = user_input["DBSENSORS"] or False
            self.init_info["UPSCALE_100"] = user_input["UPSCALE_100"] or False
            self.init_info["HEADAMPS_CONFIG"] = user_input["HEADAMPS"]
            return self.async_create_entry(
                title=self.init_info["NAME"],
                data=self.init_info,
            )

        mixer_info = await self._mixer_info(
            mixer_ip=user_input["MIXER_IP"],
            mixer_type=user_input["MIXER_TYPE"],
        )
        channel_options = self.create_list(mixer_info["channel"]["number"])
        bus_options = self.create_list(mixer_info["bus"]["number"])
        matrix_options = self.create_list(mixer_info["matrix"]["number"])
        dca_options = self.create_list(mixer_info["dca"]["number"])
        auxin_options = self.create_list(mixer_info["auxin"]["number"])
        headamps_options = self.create_list(mixer_info["head_amps"]["number"])

        return self.async_show_form(
            step_id="name",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "NAME", default=user_input.get("NAME_DEFAULT")
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Optional("CHANNELS", default=channel_options): cv.multi_select(
                        channel_options
                    ),
                    vol.Optional("BUSSES", default=bus_options): cv.multi_select(
                        bus_options
                    ),
                    vol.Optional("DCAS", default=dca_options): cv.multi_select(
                        dca_options
                    ),
                    vol.Optional("MATRICES", default=matrix_options): cv.multi_select(
                        matrix_options
                    ),
                    vol.Optional("AUXINS", default=auxin_options): cv.multi_select(
                        auxin_options
                    ),
                    vol.Optional("HEADAMPS", default=[]): cv.multi_select(
                        headamps_options
                    ),
                    vol.Optional("MAIN", default=True): cv.boolean,
                    vol.Optional("CHANNELSENDS", default=False): cv.boolean,
                    vol.Optional("BUSSENDS", default=False): cv.boolean,
                    vol.Optional("DBSENSORS", default=True): cv.boolean,
                    vol.Optional("UPSCALE_100", default=False): cv.boolean,
                }
            ),
            errors=_errors,
        )

    async def _test_connect(self, mixer_ip: str, mixer_type: str) -> None:
        """Validate IP/Type."""
        client = BehringerMixerApiClient(mixer_ip=mixer_ip, mixer_type=mixer_type)
        await client.setup(test_connection_only=True)
        await client.async_get_data()
        await client.stop()
        if not client.mixer_network_name():
            raise BehringerMixerApiClientCommunicationError
        return client.mixer_network_name()

    async def _mixer_info(self, mixer_ip: str, mixer_type: str) -> None:
        """Load Mixer Information."""
        client = BehringerMixerApiClient(mixer_ip=mixer_ip, mixer_type=mixer_type)
        await client.setup(test_connection_only=True)
        await client.async_get_data()
        await client.stop()
        return client.mixer_info()

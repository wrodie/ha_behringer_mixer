"""Adds config flow for BehringerMixer."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
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
                user_input["NAME_DEFAULT"] = await self.test_connect(
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
        return await show_options_form("name", self, _errors, {"NAME": user_input["NAME_DEFAULT"]})

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowHandler:
        """Create the options flow."""
        return OptionsFlowHandler()

    @staticmethod
    async def test_connect(mixer_ip: str, mixer_type: str) -> None:
        """Validate IP/Type."""
        try:
            client = BehringerMixerApiClient(mixer_ip=mixer_ip, mixer_type=mixer_type)
            await client.setup(test_connection_only=True)
            await client.async_get_data()
            await client.stop()
            if not client.mixer_network_name():
                raise BehringerMixerApiClientCommunicationError
            return client.mixer_network_name()
        except Exception as e:
            LOGGER.error("Error during test_connect: %s", e)
            raise

    @staticmethod
    async def mixer_info(mixer_ip: str, mixer_type: str) -> None:
        """Load Mixer Information."""
        try:
            client = BehringerMixerApiClient(mixer_ip=mixer_ip, mixer_type=mixer_type)
            await client.setup(test_connection_only=True)
            await client.async_get_data()
            await client.stop()
            return client.mixer_info()
        except Exception as e:
            LOGGER.error("Error during test_connect: %s", e)
            raise

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for BehringerMixer."""

    async def async_step_init(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Manage the options."""

        _errors = {}
        if user_input is not None:
            user_input["MIXER_TYPE"] = self.config_entry.data.get("MIXER_TYPE")
            try:
                await BehringerMixerFlowHandler.test_connect(
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
                return await self.async_step_name()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("MIXER_IP", default=self.config_entry.data.get("MIXER_IP", "")): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def async_step_name(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Manage the options."""

        _errors = {}
        if user_input is not None:
            try:
                user_input.update(self.init_info)
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=user_input
                )
                return self.async_create_entry(data=user_input)
            except Exception as e:
                LOGGER.error("Error updating entry: %s", e)
                _errors["base"] = "update_failed"

        return await show_options_form("name", self, _errors, self.config_entry.data)

async def show_options_form(form_id, object, errors, existing_values) -> config_entries.FlowResult:
    """Show the options form to the user."""
    mixer_info = await BehringerMixerFlowHandler.mixer_info(
        mixer_ip=object.init_info["MIXER_IP"],
        mixer_type=object.init_info["MIXER_TYPE"],
    )
    return object.async_show_form(
        step_id=form_id,
        data_schema=vol.Schema(
            {
                vol.Required("NAME", default=existing_values.get("NAME")): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT
                    ),
                ),
                #vol.Optional("CHANNELS", default=existing_values.get("CHANNELS", [])): select(
                #    BehringerMixerFlowHandler.create_list(mixer_info["channel"]["number"])
                #),
                vol.Optional("CHANNELS", default=existing_values.get("CHANNEL_CONFIG", [])): cv.multi_select(
                    BehringerMixerFlowHandler.create_list(mixer_info["channel"]["number"])
                ),
                vol.Optional("BUSSES", default=existing_values.get("BUS_CONFIG", [])): cv.multi_select(
                    BehringerMixerFlowHandler.create_list(mixer_info["bus"]["number"])
                ),
                vol.Optional("DCAS", default=existing_values.get("DCA_CONFIG", [])): cv.multi_select(
                    BehringerMixerFlowHandler.create_list(mixer_info["dca"]["number"])
                ),
                vol.Optional("MATRICES", default=existing_values.get("MATRIX_CONFIG", [])): cv.multi_select(
                    BehringerMixerFlowHandler.create_list(mixer_info["matrix"]["number"])
                ),
                vol.Optional("AUXINS", default=existing_values.get("AUXIN_CONFIG", [])): cv.multi_select(
                    BehringerMixerFlowHandler.create_list(mixer_info["auxin"]["number"])
                ),
                vol.Optional("HEADAMPS", default=existing_values.get("HEADAMPS_CONFIG", [])): cv.multi_select(
                    BehringerMixerFlowHandler.create_list(mixer_info["head_amps"]["number"])
                ),
                vol.Optional("MAIN", default=existing_values.get("MAIN_CONFIG", True)): cv.boolean,
                vol.Optional("CHANNELSENDS", default=existing_values.get("CHANNELSENDS_CONFIG", False)): cv.boolean,
                vol.Optional("BUSSENDS", default=existing_values.get("BUSSENDS_CONFIG", False)): cv.boolean,
                vol.Optional("DBSENSORS", default=existing_values.get("DBSENSORS", True)): cv.boolean,
                vol.Optional("UPSCALE_100", default=existing_values.get("UPSCALE_100", False)): cv.boolean,
            }
        ),
        errors=errors,
    )
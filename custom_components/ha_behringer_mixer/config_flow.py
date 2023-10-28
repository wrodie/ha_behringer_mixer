"""Adds config flow for BehringerMixer."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .api import (
    BehringerMixerApiClient,
    BehringerMixerApiClientAuthenticationError,
    BehringerMixerApiClientCommunicationError,
    BehringerMixerApiClientError,
)
from .const import DOMAIN, LOGGER


class BehringerMixerFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for BehringerMixer."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_connect(
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
                return self.async_create_entry(
                    title=user_input["MIXER_IP"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("MIXER_IP"): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required("MIXER_TYPE", default="X32"): vol.In(["X32", "XR12", "XR16", "XR18"]),
                }
            ),
            errors=_errors,
        )

    async def _test_connect(self, mixer_ip: str, mixer_type: str) -> None:
        """Validate credentials."""
        client = BehringerMixerApiClient(mixer_ip=mixer_ip, mixer_type=mixer_type)
        await client.async_get_data()

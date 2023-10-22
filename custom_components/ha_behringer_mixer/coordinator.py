"""DataUpdateCoordinator for integration_blueprint."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import (
    BehringerMixerApiClient,
    BehringerMixerApiClientAuthenticationError,
    BehringerMixerApiClientError,
)
from .const import DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class BlueprintDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: BehringerMixerApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
        )

#    async def async_set_updated_data(self):
#        print("SET UPDATED DATA")
#        pass

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.client.async_get_data()
        except BehringerMixerApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except BehringerMixerApiClientError as exception:
            raise UpdateFailed(exception) from exception


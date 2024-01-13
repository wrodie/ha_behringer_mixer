"""DataUpdateCoordinator for Behringer Mixer Integration."""
from __future__ import annotations

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


class MixerDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry
    entity_catalog: {}

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
        self.sub_connected = False
        self.entity_base_id = self.config_entry.data["NAME"]
        self.entity_catalog = self.build_entity_catalog(self.client.mixer_info())

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.client.async_get_data()
        except BehringerMixerApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except BehringerMixerApiClientError as exception:
            raise UpdateFailed(exception) from exception

    def build_entity_catalog(self, mixer_info):
        """Build a list of entities."""
        types = ["channel", "bus", "dca", "matrix", "auxin"]
        entities = {
            "SENSOR": [],
            "NUMBER": [],
            "SWITCH": [],
        }
        if self.config_entry.data.get("MAIN_CONFIG"):
            self.fader_group(entities, "main", 0, "main/st")
        for entity_type in types:
            # num_type = mixer_info.get(entity_type, {}).get("number")
            base_key = mixer_info.get(entity_type, {}).get("base_address")
            for index_number in self.config_entry.data[entity_type.upper() + "_CONFIG"]:
                self.fader_group(entities, entity_type, index_number, base_key)
        entities["NUMBER"].append(
            {
                "type": "scene",
                "key": f"{self.entity_base_id}_scene_current",
                "default_name": "Current Scene",
                "base_address": "/scene/current",
            }
        )
        entities["SENSOR"].append(
            {
                "type": "generic",
                "key": f"{self.entity_base_id}_firmware",
                "default_name": "Firmware Version",
                "base_address": "/firmware",
            }
        )
        return entities

    def fader_group(self, entities, entity_type, index_number, base_key):
        """Generate entities for a fader."""
        entity_part = entity_type
        base_address = f"/{base_key}"
        default_name = entity_type
        if index_number:
            entity_part = entity_type + "_" + str(index_number)
            base_address = base_address + "/" + str(index_number)
            default_name = default_name + " " + str(index_number or 0)
        entities["SWITCH"].append(
            {
                "type": "on",
                "key": f"{self.entity_base_id}_{entity_part}_on",
                "default_name": default_name,
                "name_suffix": "On",
                "base_address": base_address,
            }
        )
        entities["NUMBER"].append(
            {
                "type": "fader",
                "key": f"{self.entity_base_id}_{entity_part}_fader",
                "default_name": default_name,
                "name_suffix": "Fader",
                "base_address": base_address,
            }
        )
        entities["SENSOR"].append(
            {
                "type": "faderdb",
                "key": f"{self.entity_base_id}_{entity_part}_fader_db",
                "default_name": default_name,
                "name_suffix": "Fader (dB)",
                "base_address": base_address,
            }
        )

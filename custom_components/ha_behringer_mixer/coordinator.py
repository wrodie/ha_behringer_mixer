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
        self.sub_connected = True
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
            "SELECT": [],
        }
        if self.config_entry.data.get("MAIN_CONFIG"):
            self.fader_group(entities, "main", 0, "main/st")
            if mixer_info.get("has_mono", False):
                self.fader_group(entities, "mono", 0, "main/m")
        # Input channels
        for entity_type in types:
            # num_type = mixer_info.get(entity_type, {}).get("number")
            base_key = mixer_info.get(entity_type, {}).get("base_address")
            config_key = entity_type.upper() + "_CONFIG"
            for index_number in self.config_entry.data.get(config_key, []):
                self.fader_group(entities, entity_type, index_number, base_key)
        # Channel to bus sends
        if self.config_entry.data.get("CHANNELSENDS_CONFIG"):
            base_key = mixer_info.get("channel_sends", {}).get("base_address")
            for channel_number in self.config_entry.data.get("CHANNEL_CONFIG", []):
                for bus_number in self.config_entry.data.get("BUS_CONFIG", []):
                    self.fader_group(
                        entities,
                        "chsend",
                        f"{channel_number}/{bus_number}",
                        base_key,
                        f"channel {channel_number} -> bus {bus_number}",
                    )

        # Bus to matrix sends
        num_matrix = mixer_info.get("matrix", {}).get("number")
        if num_matrix and self.config_entry.data.get("BUSSENDS_CONFIG"):
            base_key = mixer_info.get("bus_sends", {}).get("base_address")
            for bus_number in self.config_entry.data["BUS_CONFIG"]:
                for matrix_number in self.config_entry.data["MATRIX_CONFIG"]:
                    self.fader_group(
                        entities,
                        "bussend",
                        f"{bus_number}/{matrix_number}",
                        base_key,
                        f"bus {bus_number} -> matrix {matrix_number}",
                    )
        # Head Amps
        if self.config_entry.data.get("HEADAMPS_CONFIG"):
            base_key = mixer_info.get("head_amps", {}).get("base_address")
            for headamp_number in self.config_entry.data.get("HEADAMPS_CONFIG", []):
                self.headamp_group(
                    entities,
                    "headamp",
                    headamp_number,
                    base_key
                )

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
        ),
        entities["SENSOR"].append(
            {
                "type": "generic",
                "key": f"{self.entity_base_id}_usb_filename",
                "default_name": "USB Filename",
                "base_address": "/usb/file",
            }
        )
        entities["SELECT"].append(
            {
                "type": "generic",
                "key": f"{self.entity_base_id}_tape_state",
                "default_name": "USB Tape State",
                "base_address": "/usb/state",
            }
        )
        return entities

    def fader_group(self, entities, entity_type, index_number, base_key, name=""):
        """Generate entities for a fader."""
        entity_part = entity_type
        base_address = f"/{base_key}"
        default_name = entity_type
        if index_number:
            entity_part = entity_type + "_" + str(index_number)
            base_address = base_address + "/" + str(index_number)
            default_name = default_name + " " + str(index_number or 0)
        default_name = name or default_name
        entities["SWITCH"].append(
            {
                "type": "mute",
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
        if self.config_entry.data.get("DBSENSORS"):
            entities["SENSOR"].append(
                {
                    "type": "faderdb",
                    "key": f"{self.entity_base_id}_{entity_part}_fader_db",
                    "default_name": default_name,
                    "name_suffix": "Fader (dB)",
                    "base_address": base_address,
                }
            )

    def headamp_group(self, entities, entity_type, index_number, base_key, name=""):
        """Generate entities for a headamp."""
        entity_part = entity_type
        base_address = f"/{base_key}"
        default_name = "HeadAmp"
        if index_number:
            entity_part = entity_type + "_" + str(index_number)
            base_address = base_address + "/" + str(index_number)
            default_name = default_name + " " + str(index_number or 0)
        default_name = name or default_name
        entities["SWITCH"].append(
            {
                "type": "on",
                "key": f"{self.entity_base_id}_{entity_part}_phantom",
                "default_name": default_name,
                "name_suffix": "Phantom Power",
                "base_address": f"{base_address}/phantom",
            }
        )
        entities["NUMBER"].append(
            {
                "type": "headamp_gain",
                "key": f"{self.entity_base_id}_{entity_part}_gain",
                "default_name": default_name,
                "name_suffix": "Gain",
                "base_address": f"{base_address}/gain",
            }
        )

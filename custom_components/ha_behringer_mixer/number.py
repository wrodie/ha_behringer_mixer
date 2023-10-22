"""Number platform for behringer_mixer."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberEntityDescription

from .const import DOMAIN
from .entity import BehringerMixerEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    devices_list = build_entities(coordinator)
    async_add_devices(devices_list)


def build_entities(coordinator):
    """Build up the entities"""
    entities = []
    number_channels = 3  # coordinator.numberOfChannels
    for index_number in range(1, number_channels + 1):
        description = NumberEntityDescription(
            key=f"{coordinator.config_entry.entry_id}_channel_{index_number}_fader",
            name=f"Channel {index_number} Fader",
            icon="mdi:volume-high",
        )
        entities.append(
            BehringerMixerNumber(
                coordinator=coordinator,
                entity_description=description,
                base_address=f"/ch/{index_number}",
            )
        )
    return entities


class BehringerMixerNumber(BehringerMixerEntity, NumberEntity):
    """behringer_mixer Number class."""

    _attr_native_max_value = 1
    _attr_native_min_value = 0


    @property
    def name(self) -> str | None:
        """Name  of the entity."""
        value = (
            self.coordinator.data.get(self.base_address + "/config_name", "") + " Fader"
        )
        return value

    @property
    def native_value(self) -> float | None:
        """Value of the entity."""
        return self.coordinator.data.get(self.base_address + "/mix_fader", "")

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        await self.coordinator.client.async_set_value(
            self.base_address + "/mix_fader", value
        )
        #await self.coordinator.async_request_refresh()
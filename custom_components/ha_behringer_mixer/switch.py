"""Switch platform for behringer_mixer."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .const import DOMAIN
from .coordinator import BlueprintDataUpdateCoordinator
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
        description = SwitchEntityDescription(
            key=f"{coordinator.config_entry.entry_id}_channel_{index_number}_on",
            name=f"Channel {index_number} On",
            icon="mdi:volume-high",
        )
        entities.append(
            BehringerMixerSwitch(
                coordinator=coordinator,
                entity_description=description,
                base_address=f"/ch/{index_number}",
            )
        )
    return entities


class BehringerMixerSwitch(BehringerMixerEntity, SwitchEntity):
    """behringer_mixer switch class."""

    @property
    def name(self) -> str | None:
        """Name  of the entity."""
        return self.coordinator.data.get(self.base_address + "/config_name", "")

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        if self.is_on:
            return "mdi:volume-high"
        return "mdi:volume-mute"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.coordinator.data.get(self.base_address + "/mix_on", False)

    async def async_turn_on(self, **_: any) -> None:
        """Turn on the switch."""
        await self.coordinator.client.async_set_value(
            self.base_address + "/mix_on", True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_: any) -> None:
        """Turn off the switch."""
        await self.coordinator.client.async_set_value(
            self.base_address + "/mix_on", False
        )
        await self.coordinator.async_request_refresh()

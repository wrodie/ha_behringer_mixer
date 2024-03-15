"""Select entity platform for behringer_mixer."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity, SelectEntityDescription

from .const import DOMAIN
from .entity import BehringerMixerEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    devices_list = build_entities(coordinator)
    async_add_devices(devices_list)


def build_entities(coordinator):
    """Build up the entities."""
    entities = []
    for entity in coordinator.entity_catalog.get("SELECT"):
        entities.append(
            BehringerMixerUSBState(
                coordinator=coordinator,
                entity_description=SelectEntityDescription(
                    key=entity.get("key"),
                    name=entity.get("default_name"),
                ),
                entity_setup=entity,
            )
        )
    return entities


class BehringerMixerUSBState(BehringerMixerEntity, SelectEntity):
    """Behringer_mixer select class."""

    _attr_icon = "mdi:play-pause"
    _attr_options = [
        "STOP",
        "PAUSE",
        "PLAY",
        "PAUSE_RECORD",
        "RECORD",
        "FAST_FORWARD",
        "REWIND",
    ]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.coordinator.client.async_set_value(self.base_address, option)
        return True

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        if self.base_address in self.coordinator.data:
            return self.coordinator.data[self.base_address]
        return None

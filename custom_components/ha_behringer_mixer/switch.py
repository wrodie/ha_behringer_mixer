"""Switch platform for behringer_mixer."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

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
    for entity in coordinator.entity_catalog.get("SWITCH"):

        if entity.get("type") == "mute":
            entities.append(
                BehringerMixerSwitch(
                    coordinator=coordinator,
                    entity_description=SwitchEntityDescription(
                        key=entity.get("key"),
                        name=entity.get("default_name"),
                    ),
                    entity_setup=entity,
                )
            )
        else:
            entities.append(
                BehringerMixerSwitchGeneric(
                    coordinator=coordinator,
                    entity_description=SwitchEntityDescription(
                        key=entity.get("key"),
                        name=entity.get("default_name"),
                    ),
                    entity_setup=entity,
                )
            )
    return entities

class BehringerMixerSwitchGeneric(BehringerMixerEntity, SwitchEntity):
    """Behringer_mixer switch generic class."""

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.coordinator.data.get(self.base_address, False)

    async def async_turn_on(self, **_: any) -> None:
        """Turn on the switch."""
        await self.coordinator.client.async_set_value(
            self.base_address, True
        )

    async def async_turn_off(self, **_: any) -> None:
        """Turn off the switch."""
        await self.coordinator.client.async_set_value(
            self.base_address, False
        )

class BehringerMixerSwitch(BehringerMixerEntity, SwitchEntity):
    """Behringer_mixer switch class."""

    _attr_icon = "mdi:volume-high"

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

    async def async_turn_off(self, **_: any) -> None:
        """Turn off the switch."""
        await self.coordinator.client.async_set_value(
            self.base_address + "/mix_on", False
        )

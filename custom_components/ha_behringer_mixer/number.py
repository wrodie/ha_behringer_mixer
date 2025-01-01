"""Number platform for behringer_mixer."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberEntityDescription

# from homeassistant.helpers import config_validation as cv, entity_platform
# import voluptuous as vol

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
    for entity in coordinator.entity_catalog.get("NUMBER"):
        if entity.get("type") == "scene":
            entities.append(
                BehringerMixerSceneNumber(
                    coordinator=coordinator,
                    entity_description=NumberEntityDescription(
                        key=entity.get("key"),
                        name=entity.get("default_name"),
                    ),
                    entity_setup=entity,
                )
            )
        elif entity.get("type") == "headamp_gain":
            entities.append(
                BehringerMixerHeadAmpGain(
                    coordinator=coordinator,
                    entity_description=NumberEntityDescription(
                        key=entity.get("key"),
                        name=entity.get("default_name"),
                    ),
                    entity_setup=entity,
                )
            )
        else:
            entities.append(
                BehringerMixerFader(
                    coordinator=coordinator,
                    entity_description=NumberEntityDescription(
                        key=entity.get("key"),
                        name=entity.get("default_name"),
                    ),
                    entity_setup=entity,
                )
            )
    return entities


class BehringerMixerSceneNumber(BehringerMixerEntity, NumberEntity):
    """Behringer_mixer Scene Number class."""

    _attr_mode = "box"

    @property
    def native_value(self) -> float | None:
        """Value of the entity."""
        return self.coordinator.data.get(self.base_address, "")

    @property
    def name(self) -> str | None:
        """Name  of the entity."""
        return self.default_name

    async def async_set_native_value(self, value: float) -> None:
        """Update the current scene."""
        await self.coordinator.client.load_scene(int(value))

class BehringerMixerHeadAmpGain(BehringerMixerEntity, NumberEntity):
    """Behringer_mixer Float Number class."""

    _attr_native_min_value = 0
    _attr_native_max_value = 1
    @property
    def native_value(self) -> float | None:
        """Value of the entity."""
        return self.coordinator.data.get(self.base_address, "")

    @property
    def name(self) -> str | None:
        """Name  of the entity."""
        return self.default_name

    async def async_set_native_value(self, value: float) -> None:
        """Update the current scene."""
        await self.coordinator.client.async_set_value(
            self.base_address, value
        )
    @property
    def extra_state_attributes(self):
        """Generate extra state attributes."""
        attrs = {}
        attrs["db"] = self.coordinator.data.get(self.base_address + "_db", "") or -12
        return attrs

class BehringerMixerFader(BehringerMixerEntity, NumberEntity):
    """Behringer_mixer Number class."""

    _attr_native_min_value = 0
    _attr_icon = "mdi:volume-source"

    @property
    def native_max_value(self) -> float | None:
        """Maximum value of the entity."""
        if self.coordinator.config_entry.data.get("UPSCALE_100"):
            return 100
        return 1

    @property
    def native_value(self) -> float | None:
        """Value of the entity."""
        value = self.coordinator.data.get(self.base_address + "/mix_fader", "")
        if self.coordinator.config_entry.data.get("UPSCALE_100"):
            return 100 * value
        return value

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        if self.coordinator.config_entry.data.get("UPSCALE_100"):
            value = value / 100
        await self.coordinator.client.async_set_value(
            self.base_address + "/mix_fader", value
        )

    @property
    def extra_state_attributes(self):
        """Generate extra state attributes."""
        attrs = {}
        attrs["db"] = self.coordinator.data.get(self.base_address + "/mix_fader_db", "") or -90
        return attrs

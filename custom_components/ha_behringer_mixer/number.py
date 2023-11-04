"""Number platform for behringer_mixer."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberEntityDescription
#from homeassistant.helpers import config_validation as cv, entity_platform
#import voluptuous as vol

from .const import DOMAIN
from .entity import BehringerMixerEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    devices_list = build_entities(coordinator)
    async_add_devices(devices_list)

    # Register service to change scenes
    # platform = entity_platform.async_get_current_platform()
    # platform.async_register_entity_service(
    #    "SERVICE_CHANGE_SCENE",
    #    {
    #        vol.Required("scene_number"): cv.Number,
    #    },
    #    "change_scene",
    # )


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


class BehringerMixerFader(BehringerMixerEntity, NumberEntity):
    """Behringer_mixer Number class."""

    _attr_native_max_value = 1
    _attr_native_min_value = 0
    _attr_icon = "mdi:volume-source"

    @property
    def native_value(self) -> float | None:
        """Value of the entity."""
        return self.coordinator.data.get(self.base_address + "/mix_fader", "")

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        await self.coordinator.client.async_set_value(
            self.base_address + "/mix_fader", value
        )

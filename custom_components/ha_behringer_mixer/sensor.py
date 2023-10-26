"""Sensor platform for behringer_mixer."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

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
    for entity in coordinator.entity_catalog.get("SENSOR"):
        entities.append(
            BehringerMixerSensor(
                coordinator=coordinator,
                entity_description=SensorEntityDescription(
                    key=entity.get("key"),
                    name=entity.get("default_name"),
                ),
                entity_setup=entity,
            )
        )
    return entities

class BehringerMixerSensor(BehringerMixerEntity, SensorEntity):
    """behringer_mixer Sensor class."""

    _attr_device_class = "SensorDeviceClass.SOUND_PRESSURE"
    _attr_native_unit_of_measurement = "dB"
    _attr_icon = "mdi:volume-source"

    @property
    def native_value(self) -> float | None:
        """Value of the entity."""
        return self.coordinator.data.get(self.base_address + "/mix_fader_db", "")

"""Sensor platform for behringer_mixer."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

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
    number_channels = 3  # coordinator.SensorOfChannels
    for index_number in range(1, number_channels + 1):
        description = SensorEntityDescription(
            key=f"{coordinator.config_entry.entry_id}_channel_{index_number}_fader_db",
            name=f"Channel {index_number} Fader (dB)",
            icon="mdi:volume-high",
        )
        entities.append(
            BehringerMixerSensor(
                coordinator=coordinator,
                entity_description=description,
                base_address=f"/ch/{index_number}",
            )
        )
    return entities


class BehringerMixerSensor(BehringerMixerEntity, SensorEntity):
    """behringer_mixer Sensor class."""

    _attr_device_class = "SensorDeviceClass.SOUND_PRESSURE"
    _attr_native_unit_of_measurement = "dB"


    @property
    def name(self) -> str | None:
        """Name  of the entity."""
        value = (
            self.coordinator.data.get(self.base_address + "/config_name", "")
            + " Fader dB"
        )
        return value

    @property
    def native_value(self) -> float | None:
        """Value of the entity."""
        return self.coordinator.data.get(self.base_address + "/mix_fader_db", "")

"""BlueprintEntity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, VERSION
from .coordinator import BlueprintDataUpdateCoordinator


class BehringerMixerEntity(CoordinatorEntity):
    """BlueprintEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init2__(self, coordinator: BlueprintDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"Mixer - {coordinator.config_entry.data['MIXER_TYPE']} - {coordinator.config_entry.data['MIXER_IP']}",
            model=VERSION,
            manufacturer="Behringer",
        )
        self.base_address = ""

    def __init__(
        self,
        coordinator: BlueprintDataUpdateCoordinator,
        entity_description,
        base_address: str,
    ) -> None:
        """Initialize the entity class."""
        super().__init__(coordinator)
        self.base_address = base_address
        self._attr_unique_id = entity_description.key
        self._attr_entity_id = DOMAIN + "." + entity_description.key
        self.entity_id = self._attr_entity_id
        self.entity_description = entity_description
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"Mixer - {coordinator.config_entry.data['MIXER_TYPE']} - {coordinator.config_entry.data['MIXER_IP']}",
            model=VERSION,
            manufacturer="Behringer",
        )

    # @property
    # def name(self) -> str | None:
    #    """Name  of the entity."""
    #    return self.coordinator.data.get(self.base_address + "/config_name", "")

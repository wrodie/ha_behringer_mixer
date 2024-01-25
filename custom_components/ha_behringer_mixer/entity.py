"""BlueprintEntity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, VERSION
from .coordinator import MixerDataUpdateCoordinator


class BehringerMixerEntity(CoordinatorEntity):
    """BlueprintEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: MixerDataUpdateCoordinator,
        entity_description: EntityDescription,
        entity_setup: dict,
    ) -> None:
        """Initialize the entity class."""
        super().__init__(coordinator)
        self.base_address = entity_setup.get("base_address")
        self.default_name = entity_setup.get("default_name") or ""
        self.name_suffix = entity_setup.get("name_suffix") or ""
        key = entity_setup.get("key")
        self._attr_unique_id = key
        self._attr_entity_id = DOMAIN + "." + key
        self.entity_id = self._attr_entity_id
        self.entity_description = entity_description
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"Mixer - {coordinator.config_entry.data['MIXER_TYPE']} - {coordinator.config_entry.data['MIXER_IP']}",
            model=VERSION,
            manufacturer="Behringer",
        )

    @property
    def name(self) -> str | None:
        """Name  of the entity."""
        return (
            (
                self.coordinator.data.get(self.base_address + "/config_name", "")
                or self.default_name
            )
            + " "
            + self.name_suffix
        )

    @property
    def available(self) -> bool:
        """Return True if the mixer is available."""
        return self.coordinator.sub_connected

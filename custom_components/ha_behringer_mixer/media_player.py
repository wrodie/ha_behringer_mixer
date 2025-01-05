"""Media player platform for behringer_mixer."""

from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityDescription,
    MediaPlayerDeviceClass,
)
from homeassistant.components.media_player.const import (
    MediaType,
    MediaPlayerEntityFeature,
)
from homeassistant.const import (
    STATE_OK,
)

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
    for entity in coordinator.entity_catalog.get("MEDIA_PLAYER"):
        entities.append(
            BehringerMixerFaderMediaPlayer(
                coordinator=coordinator,
                entity_description=MediaPlayerEntityDescription(
                    key=entity.get("key"),
                    name=entity.get("default_name"),
                ),
                entity_setup=entity,
            )
        )
    return entities


class BehringerMixerFaderMediaPlayer(BehringerMixerEntity, MediaPlayerEntity):
    """Behringer_mixer Fader Media Player class."""

    _attr_native_min_value = 0
    _attr_icon = "mdi:speaker"

    @property
    def device_class(self) -> MediaPlayerDeviceClass | None:
        """Return the device class of the media player."""
        return MediaPlayerDeviceClass.SPEAKER

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag media player features that are supported."""
        return (
            MediaPlayerEntityFeature.VOLUME_SET | MediaPlayerEntityFeature.VOLUME_MUTE
        )

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return MediaType.MUSIC

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self.coordinator.data.get(self.base_address + "/mix_fader", "")

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return not self.coordinator.data.get(self.base_address + "/mix_on", False)

    async def async_set_volume_level(self, volume):
        """Set volume level."""
        await self.coordinator.client.async_set_value(
            self.base_address + "/mix_fader", volume
        )

    async def async_mute_volume(self, mute):
        """Mute."""
        await self.coordinator.client.async_set_value(
            self.base_address + "/mix_on", not mute
        )

    @property
    def state(self):
        """Return the state of the device."""
        return STATE_OK

    @property
    def extra_state_attributes(self):
        """Generate extra state attributes."""
        attrs = {}
        attrs["db"] = (
            self.coordinator.data.get(self.base_address + "/mix_fader_db", "") or -90
        )
        return attrs

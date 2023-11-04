"""Custom integration to integrate a Behringer mixer into Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import BehringerMixerApiClient
from .const import DOMAIN
from .coordinator import MixerDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    client = BehringerMixerApiClient(
        mixer_ip=entry.data["MIXER_IP"], mixer_type=entry.data["MIXER_TYPE"]
    )
    if not await client.setup():
        raise ConfigEntryNotReady(
            f"Timeout while connecting to {entry.data['MIXER_IP']}"
        )

    hass.data[DOMAIN][entry.entry_id] = coordinator = MixerDataUpdateCoordinator(
        hass=hass,
        client=client,
    )
    await coordinator.async_config_entry_first_refresh()
    client.register_coordinator(coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN][entry.entry_id].client.stop()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

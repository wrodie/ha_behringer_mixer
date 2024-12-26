"""Custom integration to integrate a Behringer mixer into Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import BehringerMixerApiClient
from .const import DOMAIN, LOGGER
from .coordinator import MixerDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SELECT,
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


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version < 2:
        """Update Config data to include valid channels/bussses etc."""
        client = BehringerMixerApiClient(
            mixer_ip=config_entry.data.get("MIXER_IP"),
            mixer_type=config_entry.data.get("MIXER_TYPE"),
        )
        await client.setup(test_connection_only=True)
        await client.async_get_data()
        await client.stop()
        mixer_info = client.mixer_info()
        new = {**config_entry.data}
        new["CHANNEL_CONFIG"] = list(
            range(1, mixer_info.get("channel", {}).get("number") + 1)
        )
        new["BUS_CONFIG"] = list(range(1, mixer_info.get("bus", {}).get("number") + 1))
        new["DCA_CONFIG"] = list(range(1, mixer_info.get("dca", {}).get("number") + 1))
        new["MATRIX_CONFIG"] = list(
            range(1, mixer_info.get("matrix", {}).get("number") + 1)
        )
        new["AUXIN_CONFIG"] = list(
            range(1, mixer_info.get("auxin", {}).get("number") + 1)
        )
        new["MAIN_CONFIG"] = True
        new["CHANNELSENDS_CONFIG"] = False
        new["BUSSENDS_CONFIG"] = False
        hass.config_entries.async_update_entry(config_entry, data=new, version =2)
    if config_entry.version < 3:
        new = {**config_entry.data}
        new["DBSENSORS"] = True
        new["UPSCALE_100"] = False
        hass.config_entries.async_update_entry(config_entry, data=new, version =3)
    if config_entry.version < 4:
        new = {**config_entry.data}
        new["HEADAMPS_CONFIG"] = 0
        hass.config_entries.async_update_entry(config_entry, data=new, version =4)

    LOGGER.debug("Migration to version %s successful", config_entry.version)

    return True

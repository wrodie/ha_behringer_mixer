"""Utility functions for Behringer Mixer integration."""

import logging
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify as ha_slugify


_LOGGER = logging.getLogger(__name__)

def sanitize_name(raw_name: str) -> str:
    """Sanitize mixer/device names for Home Assistant entity_id compliance.

    Uses Home Assistant's built-in slugify function to ensure compatibility
    with Home Assistant 2026.02+ entity ID requirements.

    Args:
        raw_name: The raw name to sanitize (e.g., "X32C-07-68-95")

    Returns:
        Sanitized name with only lowercase, digits, and underscores
        (e.g., "x32c_07_68_95")
    """
    return ha_slugify(raw_name, separator="_")


async def async_migrate_old_unique_ids(hass, config_entry, platform_domain):
    """
    Migrate hyphenated unique IDs to sanitized versions for 2026.02 compliance.
    Call this from each platform's async_setup_entry.
    """
    ent_reg = er.async_get(hass)

    # Get all entities for this config entry and platform (e.g., 'number')
    entries = er.async_entries_for_config_entry(ent_reg, config_entry.entry_id)

    for entry in entries:
        # Only process entities for the specific platform calling this (sensor, number, etc.)
        if entry.domain != platform_domain:
            continue

        # Create the compliant ID
        clean_unique_id = sanitize_name(entry.unique_id)

        if entry.unique_id != clean_unique_id:
            _LOGGER.info(
                "Migrating %s entity unique_id: %s -> %s",
                platform_domain, entry.unique_id, clean_unique_id
            )

            # Update the registry. This moves settings/history to the new ID.
            ent_reg.async_update_entity(
                entry.entity_id,
                new_unique_id=clean_unique_id
            )
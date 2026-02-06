"""Utility functions for Behringer Mixer integration."""

from homeassistant.util import slugify as ha_slugify


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

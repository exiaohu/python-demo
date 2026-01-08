from app.core.config import settings, Settings
from app.core.logger import logger

def reload_settings() -> None:
    """
    Reload settings from environment variables and .env file.
    Updates the global 'settings' object in-place.
    """
    try:
        new_settings = Settings()
        # Update the existing global settings object
        # We iterate over the fields to update them in-place
        for field in new_settings.model_fields.keys():
            new_value = getattr(new_settings, field)
            setattr(settings, field, new_value)
        
        logger.info("Settings reloaded successfully")
    except Exception as e:
        logger.error(f"Failed to reload settings: {e}")

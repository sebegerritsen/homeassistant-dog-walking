"""The Dog Walking Schedule integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, TIME_SLOTS, WEEKDAYS

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Service schemas
SERVICE_UPDATE_SCHEDULE_SCHEMA = vol.Schema({
    vol.Required("day"): vol.In(WEEKDAYS),
    vol.Required("time"): vol.In(TIME_SLOTS),
    vol.Required("walker"): cv.string,
})

SERVICE_GET_SCHEDULE_SCHEMA = vol.Schema({
    vol.Optional("day"): vol.In(WEEKDAYS),
})

SERVICE_REFRESH_SENSORS_SCHEMA = vol.Schema({})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Dog Walking Schedule component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dog Walking Schedule from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Initialize the schedule data
    hass.data[DOMAIN][entry.entry_id] = {
        "schedule": get_default_schedule(),
        "coordinator": None,
    }

    # Register services
    async def handle_update_schedule(call: ServiceCall) -> None:
        """Handle the update_schedule service call."""
        day = call.data["day"]
        time = call.data["time"]
        walker = call.data["walker"]
        
        # Update the schedule
        hass.data[DOMAIN][entry.entry_id]["schedule"][day][time] = walker
        
        _LOGGER.info(
            "Updated dog walking schedule: %s at %s is now assigned to %s",
            day, time, walker
        )
        
        # Trigger sensor updates
        await _refresh_all_sensors(hass)

    async def handle_get_schedule(call: ServiceCall) -> None:
        """Handle the get_schedule service call."""
        day = call.data.get("day")
        schedule = hass.data[DOMAIN][entry.entry_id]["schedule"]
        
        if day:
            result = {day: schedule[day]}
        else:
            result = schedule
            
        _LOGGER.info("Retrieved dog walking schedule: %s", result)
        
        # You could also fire an event with the schedule data
        hass.bus.async_fire(
            "dog_walking_schedule_retrieved",
            {"schedule": result}
        )

    async def handle_refresh_sensors(call: ServiceCall) -> None:
        """Handle the refresh_sensors service call."""
        _LOGGER.info("Manually refreshing dog walking sensors")
        await _refresh_all_sensors(hass)

    async def _refresh_all_sensors(hass: HomeAssistant) -> None:
        """Refresh all dog walking sensors."""
        entity_ids = [
            "sensor.dog_walking_current_walker",
            "sensor.dog_walking_next_walker", 
            "sensor.dog_walking_next_walk_time",
            "sensor.dog_walking_todays_schedule"
        ]
        
        for entity_id in entity_ids:
            try:
                await hass.helpers.entity_component.async_update_entity(entity_id)
            except Exception as e:
                _LOGGER.debug("Could not update entity %s: %s", entity_id, e)

    hass.services.async_register(
        DOMAIN,
        "update_schedule",
        handle_update_schedule,
        schema=SERVICE_UPDATE_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "get_schedule",
        handle_get_schedule,
        schema=SERVICE_GET_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "refresh_sensors",
        handle_refresh_sensors,
        schema=SERVICE_REFRESH_SENSORS_SCHEMA,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Remove services
        hass.services.async_remove(DOMAIN, "update_schedule")
        hass.services.async_remove(DOMAIN, "get_schedule")
        hass.services.async_remove(DOMAIN, "refresh_sensors")
        
    return unload_ok


def get_default_schedule() -> dict[str, dict[str, str]]:
    """Get the default dog walking schedule based on the spreadsheet."""
    return {
        "monday": {
            "8:00": "Hidde",
            "12:00": "Opa", 
            "16:00": "Noud",
            "22:00": "Sophie"
        },
        "tuesday": {
            "8:00": "Hugo",
            "12:00": "Sebe",
            "16:00": "Thijs", 
            "22:00": "Sophie"
        },
        "wednesday": {
            "8:00": "Hidde",
            "12:00": "Sebe/Sophie",
            "16:00": "Noud",
            "22:00": "Sophie"
        },
        "thursday": {
            "8:00": "Hugo",
            "12:00": "Sebe",
            "16:00": "Hidde",
            "22:00": "Sophie"
        },
        "friday": {
            "8:00": "Hidde",
            "12:00": "Sophie",
            "16:00": "Noud",
            "22:00": "Sophie"
        },
        "saturday": {
            "8:00": "Noud",
            "12:00": "Iemand",
            "16:00": "Iemand",
            "22:00": "Sophie"
        },
        "sunday": {
            "8:00": "Hugo",
            "12:00": "Iemand",
            "16:00": "Iemand",
            "22:00": "Sophie"
        }
    } 
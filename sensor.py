"""Sensor platform for Dog Walking Schedule."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    SENSOR_CURRENT_WALKER,
    SENSOR_NEXT_WALKER,
    SENSOR_NEXT_WALK_TIME,
    SENSOR_TODAYS_SCHEDULE,
    TIME_SLOTS,
    WEEKDAYS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Dog Walking Schedule sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    
    sensors = [
        DogWalkingCurrentWalkerSensor(data, config_entry),
        DogWalkingNextWalkerSensor(data, config_entry),
        DogWalkingNextWalkTimeSensor(data, config_entry),
        DogWalkingTodaysScheduleSensor(data, config_entry),
    ]
    
    async_add_entities(sensors, True)


class DogWalkingBaseSensor(SensorEntity):
    """Base class for Dog Walking sensors."""

    def __init__(self, data: dict[str, Any], config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._data = data
        self._config_entry = config_entry
        self._attr_should_poll = True
        self._attr_available = True

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Dog Walking Schedule",
            "manufacturer": "Custom",
            "model": "Dog Walking Scheduler",
            "sw_version": "1.0.0",
        }

    def _get_current_day(self) -> str:
        """Get current day of the week."""
        now = dt_util.now()
        return WEEKDAYS[now.weekday()]

    def _get_current_time_slot(self) -> str | None:
        """Get the current time slot or the next upcoming one."""
        now = dt_util.now()
        current_time = now.strftime("%H:%M")
        
        # Find the current or next time slot
        for time_slot in TIME_SLOTS:
            if current_time <= time_slot:
                return time_slot
        
        # If past all time slots, return None (will show next day's first slot)
        return None

    def _get_next_walk_info(self) -> tuple[str, str, datetime]:
        """Get information about the next walk."""
        now = dt_util.now()
        current_day = self._get_current_day()
        current_time = now.strftime("%H:%M")
        
        schedule = self._data["schedule"]
        
        # Check remaining slots today
        for time_slot in TIME_SLOTS:
            if current_time < time_slot:
                walker = schedule[current_day].get(time_slot, "Unknown")
                next_walk_time = now.replace(
                    hour=int(time_slot.split(":")[0]),
                    minute=int(time_slot.split(":")[1]),
                    second=0,
                    microsecond=0
                )
                return walker, time_slot, next_walk_time
        
        # No more walks today, check tomorrow
        tomorrow_idx = (WEEKDAYS.index(current_day) + 1) % 7
        tomorrow = WEEKDAYS[tomorrow_idx]
        first_slot = TIME_SLOTS[0]
        walker = schedule[tomorrow].get(first_slot, "Unknown")
        
        next_walk_time = (now + timedelta(days=1)).replace(
            hour=int(first_slot.split(":")[0]),
            minute=int(first_slot.split(":")[1]),
            second=0,
            microsecond=0
        )
        
        return walker, first_slot, next_walk_time


class DogWalkingCurrentWalkerSensor(DogWalkingBaseSensor):
    """Sensor for the current dog walker."""

    def __init__(self, data: dict[str, Any], config_entry: ConfigEntry) -> None:
        """Initialize the current walker sensor."""
        super().__init__(data, config_entry)
        self._attr_name = "Dog Walking Current Walker"
        self._attr_unique_id = f"{config_entry.entry_id}_{SENSOR_CURRENT_WALKER}"
        self._attr_icon = "mdi:dog"

    async def async_update(self) -> None:
        """Update the sensor."""
        try:
            current_day = self._get_current_day()
            current_time_slot = self._get_current_time_slot()
            
            schedule = self._data["schedule"]
            
            if current_time_slot:
                self._attr_native_value = schedule[current_day].get(current_time_slot, "Unknown")
            else:
                # Past all time slots for today, show tomorrow's first walker
                tomorrow_idx = (WEEKDAYS.index(current_day) + 1) % 7
                tomorrow = WEEKDAYS[tomorrow_idx]
                first_slot = TIME_SLOTS[0]
                self._attr_native_value = schedule[tomorrow].get(first_slot, "Unknown")
                current_time_slot = f"Tomorrow {first_slot}"

            self._attr_extra_state_attributes = {
                "day": current_day.title(),
                "time_slot": current_time_slot,
                "schedule": schedule[current_day],
                "current_time": dt_util.now().strftime("%H:%M"),
            }
            self._attr_available = True
            
        except Exception as e:
            _LOGGER.error("Error updating current walker sensor: %s", e)
            self._attr_available = False


class DogWalkingNextWalkerSensor(DogWalkingBaseSensor):
    """Sensor for the next dog walker."""

    def __init__(self, data: dict[str, Any], config_entry: ConfigEntry) -> None:
        """Initialize the next walker sensor."""
        super().__init__(data, config_entry)
        self._attr_name = "Dog Walking Next Walker"
        self._attr_unique_id = f"{config_entry.entry_id}_{SENSOR_NEXT_WALKER}"
        self._attr_icon = "mdi:dog-side"

    async def async_update(self) -> None:
        """Update the sensor."""
        try:
            walker, time_slot, next_walk_time = self._get_next_walk_info()
            
            self._attr_native_value = walker
            self._attr_extra_state_attributes = {
                "time_slot": time_slot,
                "next_walk_time": next_walk_time.isoformat(),
                "day": next_walk_time.strftime("%A").lower(),
                "current_time": dt_util.now().strftime("%H:%M"),
            }
            self._attr_available = True
            
        except Exception as e:
            _LOGGER.error("Error updating next walker sensor: %s", e)
            self._attr_available = False


class DogWalkingNextWalkTimeSensor(DogWalkingBaseSensor):
    """Sensor for the next walk time."""

    def __init__(self, data: dict[str, Any], config_entry: ConfigEntry) -> None:
        """Initialize the next walk time sensor."""
        super().__init__(data, config_entry)
        self._attr_name = "Dog Walking Next Walk Time"
        self._attr_unique_id = f"{config_entry.entry_id}_{SENSOR_NEXT_WALK_TIME}"
        self._attr_icon = "mdi:clock-outline"
        self._attr_device_class = "timestamp"

    async def async_update(self) -> None:
        """Update the sensor."""
        try:
            walker, time_slot, next_walk_time = self._get_next_walk_info()
            
            self._attr_native_value = next_walk_time
            self._attr_extra_state_attributes = {
                "walker": walker,
                "time_slot": time_slot,
                "day": next_walk_time.strftime("%A"),
                "current_time": dt_util.now().strftime("%H:%M"),
            }
            self._attr_available = True
            
        except Exception as e:
            _LOGGER.error("Error updating next walk time sensor: %s", e)
            self._attr_available = False


class DogWalkingTodaysScheduleSensor(DogWalkingBaseSensor):
    """Sensor for today's complete schedule."""

    def __init__(self, data: dict[str, Any], config_entry: ConfigEntry) -> None:
        """Initialize the today's schedule sensor."""
        super().__init__(data, config_entry)
        self._attr_name = "Dog Walking Today's Schedule"
        self._attr_unique_id = f"{config_entry.entry_id}_{SENSOR_TODAYS_SCHEDULE}"
        self._attr_icon = "mdi:calendar-today"

    async def async_update(self) -> None:
        """Update the sensor."""
        try:
            current_day = self._get_current_day()
            schedule = self._data["schedule"][current_day]
            
            # Create a formatted schedule string
            schedule_list = []
            for time_slot in TIME_SLOTS:
                walker = schedule.get(time_slot, "Unknown")
                schedule_list.append(f"{time_slot}: {walker}")
            
            self._attr_native_value = " | ".join(schedule_list)
            self._attr_extra_state_attributes = {
                "day": current_day.title(),
                "schedule": schedule,
                "time_slots": TIME_SLOTS,
                "current_time": dt_util.now().strftime("%H:%M"),
            }
            self._attr_available = True
            
        except Exception as e:
            _LOGGER.error("Error updating today's schedule sensor: %s", e)
            self._attr_available = False 
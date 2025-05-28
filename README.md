# Dog Walking Schedule - Home Assistant Custom Component

A custom Home Assistant integration for managing and tracking dog walking schedules.

## Features

- **Current Walker Sensor**: Shows who is currently responsible for walking the dog
- **Next Walker Sensor**: Shows who will walk the dog next
- **Next Walk Time Sensor**: Shows when the next walk is scheduled
- **Today's Schedule Sensor**: Shows the complete schedule for today
- **Schedule Management**: Update walking assignments through Home Assistant services
- **Automatic Schedule Tracking**: Based on time slots throughout the day

## Installation

1. Copy the `dog_walking` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration > Integrations
4. Click "Add Integration" and search for "Dog Walking Schedule"
5. Follow the setup wizard

## Default Schedule

The component comes with a pre-configured schedule based on your spreadsheet:

### Time Slots
- **8:00** - Morning walk
- **12:00** - Midday walk  
- **16:00** - Afternoon walk
- **22:00** - Evening walk

### Weekly Schedule
- **Monday**: Hidde (8:00), Opa (12:00), Noud (16:00), Sophie (22:00)
- **Tuesday**: Hugo (8:00), Sebe (12:00), Thijs (16:00), Sophie (22:00)
- **Wednesday**: Hidde (8:00), Sebe/Sophie (12:00), Noud (16:00), Sophie (22:00)
- **Thursday**: Hugo (8:00), Sebe (12:00), Hidde (16:00), Sophie (22:00)
- **Friday**: Hidde (8:00), Sophie (12:00), Noud (16:00), Sophie (22:00)
- **Saturday**: Noud (8:00), Iemand (12:00), Iemand (16:00), Sophie (22:00)
- **Sunday**: Hugo (8:00), Iemand (12:00), Iemand (16:00), Sophie (22:00)

## Sensors

After installation, you'll have access to these sensors:

### `sensor.dog_walking_current_walker`
- Shows who is currently responsible for walking the dog
- Updates based on current time and day
- Attributes include current day, time slot, and full day schedule

### `sensor.dog_walking_next_walker`
- Shows who will walk the dog next
- Includes time slot and day information
- Automatically rolls over to next day when needed

### `sensor.dog_walking_next_walk_time`
- Timestamp sensor showing when the next walk is scheduled
- Can be used for automations and notifications
- Device class: timestamp

### `sensor.dog_walking_todays_schedule`
- Complete schedule for the current day
- Formatted as: "8:00: Hidde | 12:00: Opa | 16:00: Noud | 22:00: Sophie"
- Attributes include detailed schedule breakdown

## Services

### `dog_walking.update_schedule`
Update the walking schedule for a specific day and time slot.

**Parameters:**
- `day`: Day of the week (monday, tuesday, etc.)
- `time`: Time slot (8:00, 12:00, 16:00, 22:00)
- `walker`: Name of the person walking the dog

**Example:**
```yaml
service: dog_walking.update_schedule
data:
  day: monday
  time: "8:00"
  walker: "New Walker"
```

### `dog_walking.get_schedule`
Get the complete or daily schedule.

**Parameters:**
- `day`: (Optional) Specific day to get schedule for

## Automation Examples

### Notification Before Walk Time
```yaml
automation:
  - alias: "Dog Walk Reminder"
    trigger:
      - platform: time_pattern
        minutes: "/30"  # Check every 30 minutes
    condition:
      - condition: template
        value_template: >
          {% set next_walk = states('sensor.dog_walking_next_walk_time') | as_datetime %}
          {% set now = now() %}
          {% set time_diff = (next_walk - now).total_seconds() / 60 %}
          {{ 0 <= time_diff <= 30 }}
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Dog Walk Reminder"
          message: >
            {{ states('sensor.dog_walking_next_walker') }} should walk the dog at 
            {{ states.sensor.dog_walking_next_walk_time.attributes.time_slot }}
```

### Dashboard Card Example
```yaml
type: entities
title: Dog Walking Schedule
entities:
  - sensor.dog_walking_current_walker
  - sensor.dog_walking_next_walker
  - sensor.dog_walking_next_walk_time
  - sensor.dog_walking_todays_schedule
```

## Customization

You can modify the default schedule by:

1. Using the `dog_walking.update_schedule` service
2. Editing the `get_default_schedule()` function in `__init__.py`
3. Adding new time slots by modifying the `TIME_SLOTS` constant in `const.py`

## Troubleshooting

- **Sensors not updating**: Check that the integration is properly installed and Home Assistant has been restarted
- **Wrong walker showing**: Verify the current time and day, and check if the schedule needs updating
- **Service not working**: Ensure you're using the correct day format (lowercase) and time format (HH:MM)

## Support

This is a custom component created for personal use. Feel free to modify and adapt it to your needs. 
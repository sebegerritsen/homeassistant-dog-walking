# Dog Walking Schedule - Installation Guide

## ✅ Fixed Issues

The integration has been updated to fix the "This integration cannot be added from the UI" error.

### Changes Made:
1. ✅ Added `"config_flow": true` to `manifest.json`
2. ✅ Created `translations/en.json` for UI localization
3. ✅ Verified all required files are present

## 🚀 Installation Steps

### 1. Copy Files
Ensure the entire `dog_walking` folder is in your Home Assistant `custom_components` directory:
```
/config/custom_components/dog_walking/
├── __init__.py
├── config_flow.py
├── const.py
├── manifest.json
├── sensor.py
├── services.yaml
├── strings.json
├── translations/
│   └── en.json
├── examples/
│   ├── automations.yaml
│   └── dashboard.yaml
└── README.md
```

### 2. Restart Home Assistant
**Important**: Do a full restart, not just a reload:
- Go to Settings → System → Restart
- Wait for Home Assistant to fully restart

### 3. Add Integration
1. Go to Settings → Devices & Services
2. Click "Add Integration" (+ button)
3. Search for "dog" or "Dog Walking Schedule"
4. Click on "Dog Walking Schedule"
5. Follow the setup wizard

## 🔧 Troubleshooting

### If the integration still doesn't appear:

1. **Check file permissions**:
   ```bash
   chmod -R 755 /config/custom_components/dog_walking/
   ```

2. **Check Home Assistant logs**:
   - Go to Settings → System → Logs
   - Look for any errors related to "dog_walking"

3. **Verify file structure**:
   - Make sure all files are in the correct locations
   - Check that `manifest.json` contains `"config_flow": true`

4. **Clear browser cache**:
   - Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)

5. **Check Home Assistant version**:
   - This integration requires Home Assistant 2023.1 or later

### If you get import errors:
- Make sure you're running this in Home Assistant, not standalone Python
- The integration uses Home Assistant's built-in libraries

## 📱 After Installation

Once installed, you'll have these sensors:
- `sensor.dog_walking_current_walker`
- `sensor.dog_walking_next_walker`
- `sensor.dog_walking_next_walk_time`
- `sensor.dog_walking_todays_schedule`

And these services:
- `dog_walking.update_schedule`
- `dog_walking.get_schedule`

## 🎯 Quick Test

After installation, go to Developer Tools → States and search for "dog_walking" to see if the sensors are created.

## 📞 Support

If you still have issues:
1. Check the Home Assistant logs for specific error messages
2. Verify all files are present and have correct permissions
3. Make sure you did a full restart, not just a reload 
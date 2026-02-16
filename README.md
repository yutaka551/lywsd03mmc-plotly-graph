# OctoPrint-LYWSD03MMC

OctoPrint plugin to add LYWSD03MMC temperature and humidity sensor data to PlotlyTempGraph.

## Description

This plugin integrates Xiaomi Mijia LYWSD03MMC Bluetooth temperature and humidity sensors with OctoPrint's PlotlyTempGraph plugin. It allows you to monitor environmental conditions around your 3D printer by displaying sensor data directly in the temperature graph.

## Features

- Read temperature and humidity from LYWSD03MMC Bluetooth sensors
- Display sensor data in OctoPrint's temperature graph (requires PlotlyTempGraph plugin)
- Configurable update interval
- Optional display of humidity and battery level
- Customizable graph labels

## Requirements

- OctoPrint
- [PlotlyTempGraph plugin](https://github.com/jneilliii/OctoPrint-PlotlyTempGraph)
- LYWSD03MMC Bluetooth temperature and humidity sensor
- Bluetooth support on your OctoPrint host (e.g., Raspberry Pi with built-in Bluetooth)
- Python 3.x

## Installation

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

```
https://github.com/yutaka551/lywsd03mmc-plotly-graph/archive/master.zip
```

**Note:** After installation, you may need to install system dependencies:

```bash
sudo apt-get install python3-pip libglib2.0-dev
```

## Setup and Configuration

### 1. Find Your Sensor's MAC Address

You can find your sensor's MAC address using one of these methods:

**Method 1: Using Xiaomi Home App**
- Open the Xiaomi Home app
- Go to your sensor's settings
- Look for the MAC address in the "About" section

**Method 2: Using hcitool on Linux**
```bash
sudo hcitool lescan
```
Look for devices named "LYWSD03MMC" and note the MAC address (e.g., `A4:C1:38:12:34:56`).

### 2. Configure the Plugin

1. Open OctoPrint settings
2. Navigate to the "LYWSD03MMC Sensor" section
3. Enter your sensor's MAC address
4. Configure the update interval (default: 60 seconds)
5. Choose which data to display:
   - Temperature (always displayed)
   - Humidity (optional)
   - Battery level (optional)
6. Customize graph labels if desired
7. Save settings

### 3. Verify the Plugin is Working

After configuration, restart OctoPrint. Check the logs (Settings → Logging) for messages like:
```
LYWSD03MMC Plugin started
Starting sensor monitoring for MAC: A4:C1:38:12:34:56
```

The sensor data should appear in your temperature graph within the configured update interval.

## Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| MAC Address | Bluetooth MAC address of your LYWSD03MMC sensor | (empty) |
| Update Interval | How often to poll the sensor (in seconds) | 60 |
| Display Humidity | Show humidity readings in the graph | Yes |
| Display Battery | Show battery level in the graph | No |
| Temperature Label | Label for temperature in the graph | LYWSD03MMC Temp |
| Humidity Label | Label for humidity in the graph | LYWSD03MMC Humidity |
| Battery Label | Label for battery level in the graph | LYWSD03MMC Battery |

## Troubleshooting

### Connection Issues

If the plugin cannot connect to your sensor:

1. **Check MAC address**: Ensure the MAC address is entered correctly
2. **Check Bluetooth range**: Make sure the sensor is within range of your OctoPrint host
3. **Check permissions**: The OctoPrint user may need Bluetooth permissions
4. **Check for other connections**: The sensor can only maintain one BLE connection at a time

### Permissions Issue

If you see permission errors in the logs, you may need to grant Bluetooth capabilities:

```bash
sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python3))
```

Or run OctoPrint with appropriate permissions (not recommended for production).

### No Data Appearing

1. Check OctoPrint logs for error messages
2. Verify PlotlyTempGraph plugin is installed and active
3. Ensure update interval has elapsed since plugin start
4. Try manually testing the sensor connection:
   ```bash
   pip install lywsd03mmc
   lywsd03mmc A4:C1:38:12:34:56
   ```

## How It Works

This plugin uses the `lywsd03mmc` Python library to communicate with the sensor via Bluetooth Low Energy (BLE). It runs a background thread that periodically polls the sensor and injects the data into OctoPrint's temperature reporting system using the `octoprint.comm.protocol.temperatures.received` hook, making it compatible with PlotlyTempGraph and other temperature-aware plugins.

## License

Licensed under the GNU Affero General Public License v3.0.

## Support

For issues, feature requests, or questions, please use the [GitHub issue tracker](https://github.com/yutaka551/lywsd03mmc-plotly-graph/issues).

# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import threading
import time


class PlotlyGraphLywsd03mmcPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.StartupPlugin
):
    def __init__(self):
        self._temperature = None
        self._humidity = None
        self._battery = None
        self._last_update = 0
        self._update_thread = None
        self._stop_thread = False
        self._client = None

    # SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            mac_address="",
            update_interval=60,  # seconds
            display_humidity=True,
            display_battery=False,
            temp_label="LYWSD03MMC Temp",
            humidity_label="LYWSD03MMC Humidity",
            battery_label="LYWSD03MMC Battery"
        )

    # StartupPlugin mixin

    def on_after_startup(self):
        self._logger.info("LYWSD03MMC Plugin started")
        mac_address = self._settings.get(["mac_address"])

        if mac_address:
            self._logger.info("Starting sensor monitoring for MAC: %s", mac_address)
            self._start_monitoring()
        else:
            self._logger.warning("No MAC address configured. Please configure the sensor MAC address in settings.")

    # AssetPlugin mixin

    def get_assets(self):
        return dict(
            js=[],
            css=[],
            less=[]
        )

    # TemplatePlugin mixin

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    # Sensor monitoring

    def _start_monitoring(self):
        """Start the sensor monitoring thread"""
        if self._update_thread is None or not self._update_thread.is_alive():
            self._stop_thread = False
            self._update_thread = threading.Thread(target=self._monitor_sensor)
            self._update_thread.daemon = True
            self._update_thread.start()

    def _stop_monitoring(self):
        """Stop the sensor monitoring thread"""
        self._stop_thread = True
        if self._update_thread:
            self._update_thread.join(timeout=5)

    def _monitor_sensor(self):
        """Monitor the sensor and update values periodically"""
        while not self._stop_thread:
            try:
                self._read_sensor()
            except Exception as e:
                self._logger.error("Error reading sensor: %s", e)

            # Sleep for the configured interval
            update_interval = self._settings.get_int(["update_interval"])
            time.sleep(update_interval)

    def _read_sensor(self):
        """Read data from the LYWSD03MMC sensor"""
        mac_address = self._settings.get(["mac_address"])

        if not mac_address:
            self._logger.warning("MAC address not configured")
            # Reset sensor data when no MAC address is configured
            self._temperature = None
            self._humidity = None
            self._battery = None
            return

        try:
            # Import here to avoid issues if the library isn't installed
            from lywsd03mmc import Lywsd03mmcClient

            # Create or reuse client
            if self._client is None:
                self._logger.info("Connecting to sensor at %s", mac_address)
                try:
                    self._client = Lywsd03mmcClient(mac_address)
                except Exception as e:
                    self._logger.error("Failed to connect to sensor: %s", e)
                    # Reset sensor data when connection fails
                    self._temperature = None
                    self._humidity = None
                    self._battery = None
                    return

            # Read sensor data
            try:
                data = self._client.data
                self._temperature = data.temperature
                self._humidity = data.humidity
                self._battery = data.battery
                self._last_update = time.time()

                self._logger.debug("Sensor data - Temp: %.1f°C, Humidity: %d%%, Battery: %d%%",
                                   self._temperature, self._humidity, self._battery)
            except Exception as e:
                self._logger.error("Failed to read sensor data: %s", e)
                # Reset client on data read error to force reconnection on next attempt
                self._client = None
                # Reset sensor data when read fails
                self._temperature = None
                self._humidity = None
                self._battery = None

        except ImportError:
            self._logger.error("lywsd03mmc library not installed. Please install it: pip install lywsd03mmc")
            # Reset sensor data when library is not available
            self._temperature = None
            self._humidity = None
            self._battery = None

    # Callback for temperature and humidity data
    def callback(self, comm, parsed_temps):
        """Inject sensor data into the temperature graph"""
        if self._temperature is not None:
            temp_label = self._settings.get(["temp_label"])
            parsed_temps.update({temp_label: (self._temperature, None)})

            if self._settings.get_boolean(["display_humidity"]) and self._humidity is not None:
                humidity_label = self._settings.get(["humidity_label"])
                parsed_temps.update({humidity_label: (self._humidity, None)})

            if self._settings.get_boolean(["display_battery"]) and self._battery is not None:
                battery_label = self._settings.get(["battery_label"])
                parsed_temps.update({battery_label: (self._battery, None)})

        return parsed_temps

    # Temperature hook

    def get_temperature_data(self, comm, parsed_temps):
        """Hook to inject sensor data into temperature graph"""
        if self._temperature is not None:
            # Add temperature as actual value (target set to 0)
            temp_label = self._settings.get(["temp_label"])
            parsed_temps[temp_label] = (self._temperature, 0)

            # Add humidity if enabled
            if self._settings.get_boolean(["display_humidity"]) and self._humidity is not None:
                humidity_label = self._settings.get(["humidity_label"])
                parsed_temps[humidity_label] = (self._humidity, 0)

            # Add battery if enabled
            if self._settings.get_boolean(["display_battery"]) and self._battery is not None:
                battery_label = self._settings.get(["battery_label"])
                parsed_temps[battery_label] = (self._battery, 0)

        return parsed_temps

    # Softwareupdate hook

    def get_update_information(self):
        return dict(
            plotlyGraphLywsd03mmc=dict(
                displayName="PlotlyGraph LYWSD03MMC Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="yutaka551",
                repo="lywsd03mmc-plotly-graph",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/yutaka551/lywsd03mmc-plotly-graph/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "PlotlyGraph LYWSD03MMC Sensor"
__plugin_pythoncompat__ = ">=3.7,<4"
__plugin_implementation__ = PlotlyGraphLywsd03mmcPlugin()
__plugin_version__ = "0.1.0"

__plugin_hooks__ = {
    "octoprint.comm.protocol.temperatures.received": (__plugin_implementation__.callback, 1),
    "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
}

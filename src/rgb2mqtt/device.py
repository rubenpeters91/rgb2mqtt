import json
from typing import Dict

from openrgb.orgb import Device
from openrgb.utils import RGBColor


class RGBDevice:
    def __init__(self, name: str, device: Device):
        """RGB device class

        This class holds state info and function to change the
        RGB device

        Parameters
        ----------
        name : str
            The name this device has in MQTT
        device : Device
            The OpenRGB device, used to change the color
        """
        self.name = name
        self.base_topic = f"homeassistant/light/{self.name}"
        self._device = device
        # Some devices start in different modes
        self._device.set_mode("direct")
        current_color = self._device.colors[0]
        self._state: Dict = {
            "state": "ON",
            "brightness": 255,
            "color": {
                "r": current_color.red,
                "g": current_color.green,
                "b": current_color.blue,
            },
        }
        self._config: Dict = {
            "~": self.base_topic,
            "name": self.name,
            "unique_id": f"{self.name}_rgb",
            "cmd_t": "~/set",
            "stat_t": "~/state",
            "schema": "json",
            "brightness": "true",
            "rgb": "true",
        }

    def get_subscribe_link(self) -> str:
        """Returns the subscribe link, used to receive messages"""
        return f"{self.base_topic}/set"

    def get_state_link(self) -> str:
        """Returns the state link, used to change the state"""
        return f"{self.base_topic}/state"

    def get_config_link(self) -> str:
        """Returns the config link, used to change the config"""
        return f"{self.base_topic}/config"

    def get_config(self) -> str:
        """Returns the config as a string"""
        return json.dumps(self._config)

    def get_state(self) -> str:
        """Returns the state as string"""
        return json.dumps(self._state)

    def update_state(self, new_state: Dict) -> None:
        """Update the state given a new state

        Parameters
        ----------
        new_state : Dict
            New state received from MQTT to merge with current state
        """
        self._state = {**self._state, **new_state}

    def set_colors(self) -> None:
        """Set the colors of the RGB device using the current state,
        note that since we can't set the brightness we multiply all
        RGB values by a brightness multiplier
        """
        brightness_multiplier = self._state["brightness"] / 255
        color = RGBColor(
            int(self._state["color"]["r"] * brightness_multiplier),
            int(self._state["color"]["g"] * brightness_multiplier),
            int(self._state["color"]["b"] * brightness_multiplier),
        )
        self._device.set_color(color)

    def turn_off(self):
        """Turn off the RGB device"""
        self._device.clear()

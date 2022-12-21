import json

from openrgb.orgb import Device
from openrgb.utils import RGBColor


class RGBDevice:
    def __init__(self, name: str, device: Device):
        self.name = name
        self.base_topic = f"homeassistant/light/{self.name}"
        self._device = device
        current_color = self._device.colors[0]
        self._state: dict = {
            "state": "ON",
            "brightness": 255,
            "color": {
                "r": current_color.red,
                "g": current_color.green,
                "b": current_color.blue,
            },
        }
        self._config: dict = {
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
        return f"{self.base_topic}/set"

    def get_state_link(self) -> str:
        return f"{self.base_topic}/state"

    def get_config_link(self) -> str:
        return f"{self.base_topic}/config"

    def get_config(self) -> str:
        return json.dumps(self._config)

    def get_state(self) -> str:
        return json.dumps(self._state)

    def update_state(self, new_state: dict) -> None:
        self._state = {**self._state, **new_state}

    def set_colors(self) -> None:
        brightness_multiplier = self._state["brightness"] / 255
        color = RGBColor(
            int(self._state["color"]["r"] * brightness_multiplier),
            int(self._state["color"]["g"] * brightness_multiplier),
            int(self._state["color"]["b"] * brightness_multiplier),
        )
        self._device.set_color(color)

    def turn_off(self):
        self._device.set_color(RGBColor(0, 0, 0))

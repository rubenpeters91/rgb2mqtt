from openrgb.utils import RGBColor

from rgb2mqtt.device import RGBDevice


class MockRGB:
    def __init__(self, red, green, blue) -> None:
        self.red = red
        self.green = green
        self.blue = blue


class MockDevice:
    def __init__(self, name: str):
        self.name = name
        self._color = None
        self.colors = [MockRGB(0, 0, 0), MockRGB(255, 255, 255)]

    def set_mode(self, mode):
        pass

    def set_color(self, color):
        self._color = color

    def get_color(self):
        return self._color

    def clear(self):
        self._color = None


def test_rgb_device():
    """Test the RGBDevice class using a mock device class"""

    mock_device = MockDevice("test")
    device = RGBDevice("test", mock_device)
    assert device.name == "test"
    assert device.base_topic == "homeassistant/light/test"
    assert device._device is mock_device
    assert device._state == {
        "state": "ON",
        "brightness": 255,
        "color": {"r": 0, "g": 0, "b": 0},
    }
    assert device._config == {
        "~": "homeassistant/light/test",
        "name": "test",
        "unique_id": "test_rgb",
        "cmd_t": "~/set",
        "stat_t": "~/state",
        "schema": "json",
        "brightness": "true",
        "rgb": "true",
    }
    assert device.get_subscribe_link() == "homeassistant/light/test/set"
    assert device.get_state_link() == "homeassistant/light/test/state"
    assert device.get_config_link() == "homeassistant/light/test/config"
    assert device.get_config() == (
        '{"~": "homeassistant/light/test", "name": "test", '
        '"unique_id": "test_rgb", "cmd_t": "~/set", "stat_t": "~/state", '
        '"schema": "json", "brightness": "true", "rgb": "true"}'
    )
    assert device.get_state() == (
        '{"state": "ON", "brightness": 255, "color": {"r": 0, "g": 0, "b": 0}}'
    )


def test_rgb_update_state():
    """Tests the rgb update state function using a mock RGBDevice"""

    mock_device = MockDevice("test")
    device = RGBDevice("test", mock_device)
    device.update_state({"state": "OFF"})
    assert device._state == {
        "state": "OFF",
        "brightness": 255,
        "color": {"r": 0, "g": 0, "b": 0},
    }
    device.update_state({"state": "ON"})
    assert device._state == {
        "state": "ON",
        "brightness": 255,
        "color": {"r": 0, "g": 0, "b": 0},
    }
    device.update_state({"brightness": 0})
    assert device._state == {
        "state": "ON",
        "brightness": 0,
        "color": {"r": 0, "g": 0, "b": 0},
    }
    device.update_state({"color": {"r": 255, "g": 0, "b": 0}})
    assert device._state == {
        "state": "ON",
        "brightness": 0,
        "color": {"r": 255, "g": 0, "b": 0},
    }


def test_rgb_set_color_and_turnoff():
    """Tests the rgb set color and turn off function using a mock RGBDevice"""

    mock_device = MockDevice("test")
    device = RGBDevice("test", mock_device)
    device.update_state({"color": {"r": 255, "g": 0, "b": 0}})
    device.set_colors()
    assert device._device.get_color() == RGBColor(255, 0, 0)
    device.turn_off()
    assert device._device.get_color() is None

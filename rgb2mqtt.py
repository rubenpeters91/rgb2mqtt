from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
import paho.mqtt.client as mqtt
import tomllib
import json
import logging

rgb_client = OpenRGBClient(name="mqtt")
device = rgb_client.get_devices_by_name("Gigabyte RTX3080 Gaming OC 10G")[0]
current_color = device.colors[0]
state_message = {
    "state": "ON",
    "brightness": 255,
    "color": {
        "r": current_color.red,
        "g": current_color.green,
        "b": current_color.blue,
    },
}


def get_real_color(state):
    """Apply brightness scaling to RGB"""
    brightness_multiplier = state["brightness"] / 255
    return RGBColor(
        int(state["color"]["r"] * brightness_multiplier),
        int(state["color"]["g"] * brightness_multiplier),
        int(state["color"]["b"] * brightness_multiplier),
    )


def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code " + str(rc))
    client.subscribe("homeassistant/light/test/set")


def on_message(client, userdata, msg):
    global state_message
    logging.info(msg.topic + " " + str(msg.payload))
    msg = json.loads(msg.payload)
    state_message = {**state_message, **msg}
    client.publish(
        "homeassistant/light/test/state",
        payload=json.dumps(state_message),
        qos=0,
        retain=False,
    )

    if msg["state"] == "OFF":
        logging.debug("turning off the light")
        device.set_color(RGBColor(0, 0, 0))
    else:
        logging.debug("Changing the color")
        device.set_color(get_real_color(state_message))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    with open("config.toml", mode="rb") as config_path:
        config = tomllib.load(config_path)

    config_message = {
        "~": "homeassistant/light/test",
        "name": "test",
        "unique_id": "test" + "_light",
        "cmd_t": "~/set",
        "stat_t": "~/state",
        "schema": "json",
        "brightness": "true",
        "rgb": "true",
    }

    client = mqtt.Client(client_id="test_rgb")
    client.on_connect = on_connect
    client.on_message = on_message

    client.username_pw_set(username=config["mqtt_user"], password=config["mqtt_pwd"])
    client.connect("192.168.178.27", 1883, 60)

    client.publish(
        "homeassistant/light/test/config",
        payload=json.dumps(config_message),
        qos=0,
        retain=False,
    )
    client.publish(
        "homeassistant/light/test/state",
        payload=json.dumps(state_message),
        qos=0,
        retain=False,
    )

    client.loop_forever()

import json
import logging
from functools import partial

import paho.mqtt.client as mqtt
import tomllib
from openrgb import OpenRGBClient

from device import RGBDevice


def on_connect(client, userdata, flags, rc, rgb_device):
    logging.info(f"Connected with result code {rc}")
    client.subscribe(rgb_device.get_subscribe_link())


def on_message(client, userdata, msg, rgb_device):
    logging.info(f"{msg.topic} {msg.payload}")
    msg = json.loads(msg.payload)
    rgb_device.update_state(msg)
    client.publish(
        rgb_device.get_state_link(),
        payload=rgb_device.get_state(),
        qos=0,
        retain=False,
    )

    if msg["state"] == "OFF":
        rgb_device.turn_off()
    else:
        rgb_device.set_colors()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with open("config.toml", mode="rb") as config_path:
        config = tomllib.load(config_path)

    rgb_client = OpenRGBClient(name=config["rgb_client_name"])
    device = rgb_client.get_devices_by_name("Gigabyte RTX3080 Gaming OC 10G")[0]
    name = "test"

    rgb_device = RGBDevice(name, device)

    client = mqtt.Client(client_id="test_rgb")
    client.on_connect = partial(on_connect, rgb_device=rgb_device)
    client.on_message = partial(on_message, rgb_device=rgb_device)

    client.username_pw_set(username=config["mqtt_user"], password=config["mqtt_pwd"])
    client.connect(config["mqtt_host"], config["mqtt_port"], 60)

    client.publish(
        rgb_device.get_config_link(),
        payload=rgb_device.get_config(),
        qos=0,
        retain=False,
    )
    client.publish(
        rgb_device.get_state_link(),
        payload=rgb_device.get_state(),
        qos=0,
        retain=False,
    )

    client.loop_forever()

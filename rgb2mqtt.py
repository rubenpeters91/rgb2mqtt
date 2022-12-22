import json
import logging
from functools import partial
import time

import paho.mqtt.client as mqtt
import tomllib
from openrgb import OpenRGBClient

from device import RGBDevice


def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected with result code {rc}")


def on_message(client, userdata, msg):
    logging.info(f"{msg.topic} {msg.payload}")


def on_message_sub(client, userdata, msg, rgb_device):
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
    logging.basicConfig(
        level=logging.INFO,
        filename="rgb2mqtt.log",
        filemode="w",
        format="%(asctime)s %(levelname)s: %(message)s",
    )

    # Wait for OpenRGB server to start
    time.sleep(10)

    with open("config.toml", mode="rb") as config_path:
        config = tomllib.load(config_path)

    client = mqtt.Client(client_id="test_rgb")
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username=config["mqtt_user"], password=config["mqtt_pwd"])
    client.connect(config["mqtt_host"], config["mqtt_port"], 60)

    rgb_client = OpenRGBClient(name=config["rgb_client_name"])
    for orgb_name, mqtt_names in config["device_map"].items():
        devices = rgb_client.get_devices_by_name(orgb_name)
        if len(devices) != len(mqtt_names):
            error_message = (
                f"The amount of OpenRGB devices with this name is {len(devices)} "
                f"while there are only {len(mqtt_names)} values in config!"
            )
            logging.error(error_message)
            raise Exception(error_message)

        for device, mqtt_name in zip(devices, mqtt_names):
            rgb_device = RGBDevice(mqtt_name, device)
            client.subscribe(rgb_device.get_subscribe_link())
            client.message_callback_add(
                rgb_device.get_subscribe_link(),
                partial(on_message_sub, rgb_device=rgb_device),
            )

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

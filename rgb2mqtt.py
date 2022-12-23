import json
import logging
from typing import Any, Dict

from paho.mqtt.client import Client, MQTTMessage
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

from utils import connect_to_openrgb, setup_devices
from device import RGBDevice

logger = logging.getLogger(__name__)


def on_connect(client: Client, userdata: Any, flags: Dict, rc: int) -> None:
    """Callback for connection with MQTT Client

    Parameters
    ----------
    client : Client
        The client you're trying to connect to
    userdata : Any
        Any userdata you might have send (None in our case)
    flags : Dict
        Any flags
    rc : int
        The return code. 0 means success
    """
    logger.info(f"Connected to MQTT client with result code {rc}")


def on_message(client: Client, userdata: Any, msg: MQTTMessage):
    """Callback for receiving a message from MQTT

    Parameters
    ----------
    client : Client
        The MQTT client
    userdata : Any
        Any userdata (in our case None)
    msg : MQTTMessage
        The message send from the MQTT client
    """
    logger.info(f"{msg.topic} {msg.payload}")


def on_message_sub(
    client: Client, userdata: Any, msg: MQTTMessage, rgb_device: RGBDevice
) -> None:
    """Callback for receiving a specific message from MQTT

    Parameters
    ----------
    client : Client
        The MQTT client
    userdata : Any
        Any userdata (in our case: None)
    msg : MQTTMessage
        The message send from the MQTT client
    rgb_device: RGBDevice
        The RGBDevice where this message is sent to
    """
    logger.info(f"{msg.topic} {msg.payload}")
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

    with open("config.toml", mode="rb") as config_path:
        config = tomllib.load(config_path)

    logger.info("Connecting to MQTT client...")
    mqtt_client = Client(client_id="test_rgb")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set(
        username=config["mqtt_user"], password=config["mqtt_pwd"]
    )
    mqtt_client.connect(config["mqtt_host"], config["mqtt_port"], 60)

    rgb_client = connect_to_openrgb(
        name=config["rgb_client_name"], retry=5, retry_wait=10
    )

    setup_devices(
        mqtt_client=mqtt_client,
        rgb_client=rgb_client,
        device_map=config["device_map"],
        on_message_sub=on_message_sub,
    )

    mqtt_client.loop_forever()

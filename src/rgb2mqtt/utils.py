import logging
import os
import platform
import time
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict

import paho.mqtt.client as mqtt
import tomli_w
from openrgb import OpenRGBClient

from rgb2mqtt.device import RGBDevice

logger = logging.getLogger(__name__)


def _config_logs_location() -> Path:
    if platform.system() == "Windows":
        config_folder = Path(os.getenv("APPDATA", "")) / "rgb2mqtt"
    else:
        config_folder = Path.home() / "rgb2mqtt"
    config_folder.mkdir(parents=True, exist_ok=True)
    return config_folder


def config_location() -> Path:
    return _config_logs_location() / "rgb2mqtt.toml"


def log_location() -> Path:
    return _config_logs_location() / "rgb2mqtt.log"


def write_config(config_path: Path, config_dict: Dict[Any, Any]) -> None:
    """Write config from dictionary to toml file"""
    with open(config_path, "wb") as f:
        tomli_w.dump(config_dict, f)

    print(f"Config written to {config_path.absolute()}")


def connect_to_openrgb(
    name: str, retry: int = 5, retry_wait: int = 10
) -> OpenRGBClient:
    """Connect to the OpenRGB Server

    Connection to the OpenRGB server may fail initially, since this
    script is often loaded before the OpenRGB server has started.
    Therefore we retry when the connection does not succeed

    Parameters
    ----------
    name : str
        Name of this client, just so openRGB can detect this client
    retry : int, optional
        How many times do we want to retry the connection, by default 5
    retry_wait : int, optional
       How many seconds do we want to wait after a failed connection, by default 10

    Returns
    -------
    OpenRGBClient
        The initialized RGB Client
    """
    logger.info("Connecting to OpenRGB server...")
    for i in range(retry):
        try:
            rgb_client = OpenRGBClient(name=name)
            if len(rgb_client.devices) > 0:
                logger.info("Connection to OpenRGB succeeded!")
                return rgb_client
        except TimeoutError:
            logger.error(
                f"Connecting to OpenRGB timed out. "
                f"This is {i + 1} out of {retry} retries."
            )
        else:
            logger.error(
                f"No devices found, will try to reconnect. "
                f"This is {i + 1} out of {retry} retries."
            )
        time.sleep(retry_wait)

    raise Exception("Could not connect to OpenRGB client!")


def setup_devices(
    mqtt_client: mqtt.Client,
    rgb_client: OpenRGBClient,
    device_map: Dict,
    on_message_sub: Callable,
) -> None:
    """Setup all RGB devices listed in config

    Uses the device_map section of the config to set up
    all the devices, by registering the specific callback
    to mqtt and sending an inital state

    Parameters
    ----------
    mqtt_client : mqtt.Client
        The MQTT client
    rgb_client : OpenRGBClient
        The OpenRGB client
    device_map : Dict
        The device map section from the config, containing
        the names from OpenRGB as keys and the names for MQTT as values
    on_message_sub : Callable
        The callback function to use when a message is send to this device

    Raises
    ------
    Exception
        If the configuration is not compatible with the devices found in OpenRGB
    """
    for orgb_name, mqtt_names in device_map.items():
        devices = rgb_client.get_devices_by_name(orgb_name)
        if len(devices) != len(mqtt_names):
            error_message = (
                f"The amount of OpenRGB devices with this name is {len(devices)} "
                f"while there are only {len(mqtt_names)} values in config!"
            )
            logger.error(error_message)
            raise Exception(error_message)

        for device, mqtt_name in zip(devices, mqtt_names):
            rgb_device = RGBDevice(mqtt_name, device)
            mqtt_client.subscribe(rgb_device.get_subscribe_link())
            mqtt_client.message_callback_add(
                rgb_device.get_subscribe_link(),
                partial(on_message_sub, rgb_device=rgb_device),
            )

            mqtt_client.publish(
                rgb_device.get_config_link(),
                payload=rgb_device.get_config(),
                qos=0,
                retain=False,
            )
            mqtt_client.publish(
                rgb_device.get_state_link(),
                payload=rgb_device.get_state(),
                qos=0,
                retain=False,
            )

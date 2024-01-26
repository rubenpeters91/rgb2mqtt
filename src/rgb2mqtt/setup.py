import getpass
import logging
import os
import platform
import sysconfig
from pathlib import Path
from typing import Any, Dict

from rgb2mqtt.utils import config_location, connect_to_openrgb, write_config

logger = logging.getLogger(__name__)


def setup_rgb2mqtt() -> None:
    """Script to create config file"""
    config_dict: Dict[Any, Any] = {}
    config_dict["mqtt_user"] = input("Input your MQTT username: ")
    config_dict["mqtt_pwd"] = getpass.getpass("Input your MQTT password: ")
    config_dict["mqtt_host"] = input("Input your MQTT host: ")
    config_dict["mqtt_port"] = int(
        input("Input your MQTT port (default: 1883): ") or "1883"
    )
    config_dict["rgb_client_name"] = (
        input("Input your OpenRGB SDK Client name (default: mqtt): ") or "mqtt"
    )
    config_dict["device_map"] = {}

    rgb_client = connect_to_openrgb(
        name=config_dict["rgb_client_name"], retry=5, retry_wait=10
    )
    print("")
    print(
        "We will now enter the devices in the config, "
        "Note that all names have to be unique!"
    )
    for rgb_device in rgb_client.devices:
        device_input = input(
            f"Insert your mqtt name for {rgb_device} "
            "(or leave empty to remove from config): "
        )
        if device_input != "":
            if rgb_device.name in config_dict["device_map"]:
                config_dict["device_map"][rgb_device.name] += [device_input]
            else:
                config_dict["device_map"][rgb_device.name] = [device_input]

    config_path = config_location()
    if config_path.exists():
        overwrite_answer = input(
            "Config already found, overwrite current config? [y/N] "
        )
        if overwrite_answer in ["y", "Y", "yes"]:
            write_config(config_path, config_dict)
    else:
        write_config(config_path, config_dict)


def copy_to_autostart() -> None:
    """Copies executable to autostart location

    This script requires admin privileges, so will need to be run from
    Powershell with elevated permissions
    """
    if platform.system() != "Windows":
        raise NotImplementedError()

    script_path = (
        Path(sysconfig.get_path("scripts", f"{os.name}_user")) / "rgb2mqtt-gui-run.exe"
    )
    if not script_path.exists():
        script_path = Path(sysconfig.get_path("scripts")) / "rgb2mqtt-gui-run.exe"
        if not script_path.exists():
            raise Exception(
                "Can't find installed run script, did you run 'pip install'?"
            )

    target_file = (
        Path(os.getenv("Appdata", ""))
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
        / "rgb2mqtt-gui-run.exe"
    )
    if target_file.exists():
        logger.error("Script already in autostart!")
    os.symlink(script_path, target_file)


if __name__ == "__main__":
    setup_rgb2mqtt()

# RGB2MQTT

![GitHub](https://img.shields.io/github/license/rubenpeters91/rgb2mqtt)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

This is a Python script that will act as a brige between an [OpenRGB](https://openrgb.org/) server and an MQTT broker (like Mosquitto).
Useful for if you want to control your PC RGB lights via [Home Assistant](https://www.home-assistant.io/) for example.

This script is inspired by the original script from [ghomasHudson](https://gist.github.com/ghomasHudson/7cc24aa187e8141003073e36e068a5a2) and the fork from [buttercheetah](https://gist.github.com/buttercheetah/6cf0c81a5a45404f00736f4ce52aaf97).
This script is licensed under the MIT license, so feel free to try or change it yourself!

## Installation

Use `pip install -r requirements.txt` to install the required packages.
If you are running an older Python version (<3.11) than you also need to install tomli: `pip install tomli`

## Configuration

Configuration is stored in a `config.toml` file, see the `config.toml.example` file.
Be aware that in the device map section, you need to list the name of the OpenRGB device exactly as key.
To figure out which devices are supported by OpenRGB, see the `notebooks/tryout_openrgb_sdk.ipynb` file.

## Usage

The run the script, use `python rgb2mqtt.py`.

If you want this script to autostart when your PC turns on (on Windows), then press `Windows key + r` and type in `shell:startup`.
This will open a folder that contains startup script. You can add a shortcut to the `rgb2mqtt.py` script here.

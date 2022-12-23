# RGB2MQTT

This is a Python script that will act as a brige between an [OpenRGB](https://openrgb.org/) server and an MQTT broker (like Mosquitto).
Useful for if you want to control your PC RGB lights via [Home Assistant](https://www.home-assistant.io/) for example.

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

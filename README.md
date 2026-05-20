# Noma IQ HACS integration

## About

This integration exposes devices from the Noma IQ app. For now, only the current devices have been tested:

- Garage Door Opener
- Garage Door Opener's Light

It also includes generic Home Assistant `switch` support for writable boolean Ayla properties, which is intended to cover Noma IQ smart plugs and similar on/off devices. Specific plug models may still need property-level validation.

## Installation

Installation is done like any other Home Assistant HACS integration.

### Requirements

In order to setup this integration you will need:

- A Home Assistant instance with [HACS](https://hacs.xyz/) installed.

### HACS Installation

Click the button below:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mnfjorge&repository=https%3A%2F%2Fgithub.com%2Fmnfjorge%2Fhacs-nomaiq&category=integration)

Or search for "Noma IQ" in the HACS store. If you don't see it there, you can [add this repository url as a HACS custom repository](https://hacs.xyz/docs/faq/custom_repositories).

## Home Assistant Integration

[![Open your Home Assistant instance and start setting up a new integration of a specific brand.](https://my.home-assistant.io/badges/brand.svg)](https://my.home-assistant.io/redirect/brand/?brand=+Noma+IQ)

After installation, setup the integration via the web UI like any other integration. When prompted, provide the following:

- Username: your username to log into the Noma IQ app
- Password: your password to log into the Noma IQ app

### Troubleshooting

If you are having issues connecting, make sure your credentials are correct using the Noma IQ in your mobile app. If you're still having trouble, you can open a new issue here: https://github.com/mnfjorge/hacs-nomaiq/issues/new

### Probe A Device Before Installing In Home Assistant

If you want to confirm that a Noma IQ device exposes usable switch properties before loading this custom component into Home Assistant, run:

```bash
python3 scripts/probe_nomaiq.py --username YOUR_EMAIL --device-name "outdoor"
```

Add `--json` if you want the raw matching property data. For the outdoor 2-outlet plug, the expected result is that the device shows one or more writable boolean properties that correspond to the controllable outlets.

## Contributions

Contributions are welcome!

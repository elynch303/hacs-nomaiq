#!/usr/bin/env python3
"""Probe Noma IQ devices and print writable boolean properties."""

from __future__ import annotations

import argparse
import asyncio
import json
from getpass import getpass
from typing import Any

import aiohttp
import ayla_iot_unofficial

CLIENT_ID = "ctc-noma-Bg-id"
CLIENT_SECRET = "ctc-noma-WNHWBmAGLoaMl8xq8lx9XxGmiTQ"
EXCLUDED_SWITCH_PROPERTIES = {"light_control"}


def is_switch_property(property_name: str, property_data: dict[str, Any]) -> bool:
    """Match the same switch-discovery rule used by the HA integration."""
    return (
        property_name not in EXCLUDED_SWITCH_PROPERTIES
        and property_data.get("base_type") == "boolean"
        and not property_data.get("read_only", True)
    )


async def main() -> int:
    """Run the probe."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password")
    parser.add_argument(
        "--device-name",
        help="Optional substring filter to narrow output to one device",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print matching switch-like properties as JSON",
    )
    args = parser.parse_args()

    password = args.password or getpass("Noma IQ password: ")

    async with aiohttp.ClientSession() as session:
        api = ayla_iot_unofficial.new_ayla_api(
            args.username, password, CLIENT_ID, CLIENT_SECRET, session
        )
        await api.async_sign_in()
        try:
            devices = await api.async_get_devices()
            results = []

            for device in devices:
                await device.async_update()

                if args.device_name and args.device_name.lower() not in device.name.lower():
                    continue

                switch_props = {}
                for property_name, property_data in device.properties_full.items():
                    if is_switch_property(property_name, property_data):
                        switch_props[property_name] = {
                            "value": device.get_property_value(property_name),
                            "display_name": property_data.get("display_name"),
                            "name": property_data.get("name"),
                            "base_type": property_data.get("base_type"),
                            "read_only": property_data.get("read_only"),
                        }

                results.append(
                    {
                        "name": device.name,
                        "dsn": device.serial_number,
                        "oem_model": device.oem_model_number,
                        "switch_properties": switch_props,
                        "all_properties": sorted(device.properties_full.keys()),
                    }
                )

            if args.json:
                print(json.dumps(results, indent=2, sort_keys=True))
            else:
                for record in results:
                    print(f"Device: {record['name']}")
                    print(f"  DSN: {record['dsn']}")
                    print(f"  OEM model: {record['oem_model']}")
                    print("  Switch-like properties:")
                    if record["switch_properties"]:
                        for prop, meta in sorted(record["switch_properties"].items()):
                            print(
                                f"    - {prop}: value={meta['value']!r} "
                                f"display_name={meta['display_name']!r}"
                            )
                    else:
                        print("    - none found")
                    print("  All properties:")
                    for prop in record["all_properties"]:
                        print(f"    - {prop}")
                    print()
        finally:
            await api.async_sign_out()

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

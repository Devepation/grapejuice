from typing import Optional

import requests

from grapejuice_common.util.cache_utils import cache


@cache()
def current_player_version() -> Optional[str]:
    print("Gaming")
    response = requests.get("https://s3.amazonaws.com/setup.roblox.com/version")

    try:
        response.raise_for_status()

    except requests.exceptions.HTTPError:
        return None

    return response.text.strip()


@cache()
def current_studio_version() -> Optional[str]:
    print("Gaming")
    response = requests.get("https://setup.rbxcdn.com/versionQTStudio")

    try:
        response.raise_for_status()

    except requests.exceptions.HTTPError:
        return None

    return response.text.strip()

#!/usr/bin/env python3
import base64
import os
import ssl
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


if len(sys.argv) != 2:
    raise SystemExit("Usage: wait_for_restconf.py <timeout-seconds>")

host = os.environ["DEV_ROUTER_IP"]
username = os.environ["TF_VAR_dev_username"]
password = os.environ["TF_VAR_dev_password"]
timeout = int(sys.argv[1])
deadline = time.monotonic() + timeout
context = ssl._create_unverified_context()
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
url = f"https://{host}/restconf/data/Cisco-IOS-XE-native:native/hostname"
last_error = "RESTCONF did not return HTTP 200"

while time.monotonic() < deadline:
    request = Request(
        url,
        headers={
            "Accept": "application/yang-data+json",
            "Authorization": f"Basic {credentials}",
        },
    )
    try:
        with urlopen(request, timeout=15, context=context) as response:
            if response.status == 200:
                print(f"Authenticated RESTCONF is ready on https://{host}:443")
                raise SystemExit(0)
            last_error = f"HTTP {response.status}"
    except HTTPError as error:
        last_error = f"HTTP {error.code}"
    except (URLError, TimeoutError, OSError) as error:
        last_error = str(error)
    time.sleep(10)

raise SystemExit(f"Timed out after {timeout}s waiting for authenticated RESTCONF on {host}:443 ({last_error})")

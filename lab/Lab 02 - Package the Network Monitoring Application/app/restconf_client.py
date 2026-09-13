from __future__ import annotations

import requests


class RestconfError(RuntimeError):
    pass


class RestconfClient:
    def __init__(self, settings):
        self.settings = settings

    def get(self, path: str) -> dict:
        url = f"https://{self.settings.router_host}:{self.settings.router_port}{path}"
        try:
            response = requests.get(
                url,
                headers={"Accept": "application/yang-data+json"},
                auth=(self.settings.username, self.settings.password),
                timeout=(5, 15),
                verify=False,
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            raise RestconfError(f"RESTCONF collection failed: {type(exc).__name__}") from exc

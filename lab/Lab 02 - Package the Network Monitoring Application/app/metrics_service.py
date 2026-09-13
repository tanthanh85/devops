from __future__ import annotations

import math
import time
from datetime import datetime, timezone


CPU_NAMES = ("five-seconds", "five_seconds", "cpu-utilization", "cpu_usage", "value")
USED_NAMES = ("used-memory", "used_memory", "memory-used", "memory_used", "used")
FREE_NAMES = ("free-memory", "free_memory", "memory-free", "memory_free", "free")
TOTAL_NAMES = ("total-memory", "total_memory", "memory-total", "memory_total", "total")


def _find_number(value, names):
    if isinstance(value, dict):
        for key, child in value.items():
            leaf = key.split(":")[-1]
            if leaf in names and isinstance(child, (int, float, str)):
                try:
                    return float(child)
                except ValueError:
                    pass
            found = _find_number(child, names)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_number(child, names)
            if found is not None:
                return found
    return None


def normalize(cpu_data: dict, memory_data: dict) -> dict:
    cpu = _find_number(cpu_data, CPU_NAMES)
    used = _find_number(memory_data, USED_NAMES)
    total = _find_number(memory_data, TOTAL_NAMES)
    free = _find_number(memory_data, FREE_NAMES)
    if used is None and total is not None and free is not None:
        used = total - free
    if total is None and used is not None and free is not None:
        total = used + free
    if cpu is None or used is None or not total:
        raise ValueError("The RESTCONF response does not contain the configured CPU and memory leaves")
    return {"cpu_percent": round(cpu, 2), "memory_percent": round(used / total * 100, 2)}


def mock_metrics() -> dict:
    wave = time.time() / 12
    return {
        "cpu_percent": round(28 + 12 * math.sin(wave), 2),
        "memory_percent": round(54 + 5 * math.cos(wave / 2), 2),
    }


def sample(settings, client) -> dict:
    values = mock_metrics() if settings.mock_mode else normalize(
        client.get(settings.cpu_path), client.get(settings.memory_path)
    )
    return {
        "router": settings.router_host,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **values,
    }

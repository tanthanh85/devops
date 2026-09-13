from __future__ import annotations

import requests

CPU_PATH = "/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"
MEMORY_PATH = "/restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics/memory-statistic"


def _find(value, names):
    if isinstance(value, dict):
        for key, child in value.items():
            if key.split(":")[-1] in names and isinstance(child, (int, float, str)):
                try: return float(child)
                except ValueError: pass
            found = _find(child, names)
            if found is not None: return found
    if isinstance(value, list):
        for child in value:
            found = _find(child, names)
            if found is not None: return found
    return None


def collect(router):
    base = f"https://{router.host}:{router.port}"
    kwargs = dict(headers={"Accept": "application/yang-data+json"}, auth=(router.username, router.password), timeout=(5, 15), verify=False)
    cpu_response = requests.get(base + CPU_PATH, **kwargs)
    memory_response = requests.get(base + MEMORY_PATH, **kwargs)
    cpu_response.raise_for_status(); memory_response.raise_for_status()
    cpu = _find(cpu_response.json(), {"five-seconds", "five_seconds", "cpu-utilization", "value"})
    used = _find(memory_response.json(), {"used-memory", "used_memory", "used"})
    total = _find(memory_response.json(), {"total-memory", "total_memory", "total"})
    free = _find(memory_response.json(), {"free-memory", "free_memory", "free"})
    if used is None and total is not None and free is not None: used = total - free
    if total is None and used is not None and free is not None: total = used + free
    if cpu is None or used is None or not total: raise ValueError("expected CPU or memory leaves not found")
    return {"cpu_percent": round(cpu, 2), "memory_percent": round(used / total * 100, 2)}

import os
from dataclasses import dataclass


def _boolean(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    router_host: str = os.getenv("ROUTER_HOST", "192.0.2.10")
    router_port: int = int(os.getenv("ROUTER_PORT", "443"))
    username: str = os.getenv("ROUTER_USERNAME", "")
    password: str = os.getenv("ROUTER_PASSWORD", "")
    verify_tls: bool = _boolean("RESTCONF_VERIFY", True)
    ca_bundle: str = os.getenv("RESTCONF_CA_BUNDLE", "")
    cpu_path: str = os.getenv("RESTCONF_CPU_PATH", "/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization")
    memory_path: str = os.getenv("RESTCONF_MEMORY_PATH", "/restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics/memory-statistic")
    mock_mode: bool = _boolean("MOCK_MODE", True)

    @property
    def verify(self):
        return self.ca_bundle or self.verify_tls

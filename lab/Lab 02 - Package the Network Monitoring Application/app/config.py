import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


load_dotenv()


def _boolean(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    router_host: str = field(default_factory=lambda: os.getenv("ROUTER_HOST", "").strip())
    router_port: int = field(default_factory=lambda: int(os.getenv("ROUTER_PORT", "443")))
    username: str = field(default_factory=lambda: os.getenv("ROUTER_USERNAME", ""))
    password: str = field(default_factory=lambda: os.getenv("ROUTER_PASSWORD", ""))
    verify_tls: bool = False
    cpu_path: str = field(default_factory=lambda: os.getenv("RESTCONF_CPU_PATH", "/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"))
    memory_path: str = field(default_factory=lambda: os.getenv("RESTCONF_MEMORY_PATH", "/restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics/memory-statistic"))
    mock_mode: bool = field(default_factory=lambda: _boolean("MOCK_MODE", False))

    def __post_init__(self):
        placeholder_hosts = {"192.0.2.10", "<assigned-management-address>"}
        if self.mock_mode and not self.router_host:
            object.__setattr__(self, "router_host", "demonstration-target")
        elif not self.mock_mode and self.router_host in placeholder_hosts | {""}:
            raise ValueError(
                "Set ROUTER_HOST to the assigned router address in .env; "
                "documentation and empty addresses are not valid targets"
            )

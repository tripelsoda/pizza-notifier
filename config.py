from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Config:
    url: str = "https://www.pizzint.watch/api/dashboard-data"
    tz_name: str = "America/New_York"
    poll_seconds: int = 60
    timeout_seconds: int = 20
    nocache: bool = True
    output_dir: str = "out"


def load_config() -> Config:
    def env_bool(name: str, default: bool) -> bool:
        v = os.getenv(name)
        if v is None:
            return default
        return v.strip().lower() in {"1", "true", "yes", "y", "on"}

    return Config(
        url=os.getenv("PIZZINT_URL", Config.url),
        tz_name=os.getenv("PIZZINT_TZ", Config.tz_name),
        poll_seconds=int(os.getenv("PIZZINT_POLL_SECONDS", str(Config.poll_seconds))),
        timeout_seconds=int(os.getenv("PIZZINT_TIMEOUT_SECONDS", str(Config.timeout_seconds))),
        nocache=env_bool("PIZZINT_NOCACHE", Config.nocache),
        output_dir=os.getenv("PIZZINT_OUTPUT_DIR", Config.output_dir),
    )

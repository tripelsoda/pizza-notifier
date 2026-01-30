from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass
class Client:
    url: str
    tz_name: str
    timeout_seconds: int

    def __post_init__(self) -> None:
        try:
            self.tz = ZoneInfo(self.tz_name)
        except ZoneInfoNotFoundError as e:
            raise RuntimeError(
                f"Timezone '{self.tz_name}' not found. On Windows install tzdata:\n"
                f"  pip install tzdata\n"
            ) from e

    def fetch_dashboard(self, nocache: bool = True) -> Dict[str, Any]:
        params = {"nocache": 1} if nocache else None
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        r = requests.get(self.url, params=params, headers=headers, timeout=self.timeout_seconds)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, dict):
            raise ValueError(f"Unexpected response type: {type(data)}")
        return data

    @staticmethod
    def parse_iso(dt: Optional[str]) -> Optional[datetime]:
        if not dt:
            return None
        try:
            if dt.endswith("Z"):
                dt = dt.replace("Z", "+00:00")
            return datetime.fromisoformat(dt)
        except ValueError:
            return None

    def fmt_dt(self, dt_str: Optional[str]) -> str:
        dt = self.parse_iso(dt_str)
        if not dt:
            return "-" if dt_str is None else str(dt_str)
        return dt.astimezone(self.tz).strftime("%Y-%m-%d %H:%M:%S %Z")

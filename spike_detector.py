from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def safe_list(v: Any) -> List[Any]:
    return v if isinstance(v, list) else []


def safe_dict(v: Any) -> Dict[str, Any]:
    return v if isinstance(v, dict) else {}


def is_spike_payload(payload: Dict[str, Any]) -> bool:
    if payload.get("has_active_spikes") is True:
        return True

    events = safe_list(payload.get("events"))
    if len(events) > 0:
        return True

    data = safe_list(payload.get("data"))
    for item in data:
        if isinstance(item, dict) and item.get("is_spike") is True:
            return True

    return False


def spike_signature(payload: Dict[str, Any]) -> Optional[str]:
    """
    Returns a stable signature for the current spike state.
    If it returns the same signature as last time, you can suppress printing.
    """
    if not is_spike_payload(payload):
        return None

    events = safe_list(payload.get("events"))
    if events:
        parts: List[str] = []
        for e in events:
            if not isinstance(e, dict):
                continue
            parts.append(f"{e.get('place_id')}|{e.get('recorded_at')}|{e.get('spike_magnitude')}")
        parts.sort()
        return "EVENTS:" + ";".join(parts)

    # Fallback: look at spiky places
    data = safe_list(payload.get("data"))
    parts2: List[str] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        if item.get("is_spike") is True:
            parts2.append(f"{item.get('place_id')}|{item.get('recorded_at')}|{item.get('spike_magnitude')}")
    parts2.sort()
    return "PLACES:" + ";".join(parts2)


def spike_summary_lines(payload: Dict[str, Any], fmt_dt_func) -> List[str]:
    """
    fmt_dt_func is typically: client.fmt_dt
    """
    lines: List[str] = []
    lines.append("SPIKE DETECTED")

    overall_index = payload.get("overall_index")
    defcon_level = payload.get("defcon_level")
    active_spikes = payload.get("active_spikes")
    ts = fmt_dt_func(payload.get("timestamp"))

    lines.append(f"timestamp: {ts}")
    lines.append(f"overall_index: {overall_index} | defcon_level: {defcon_level} | active_spikes: {active_spikes}")

    events = safe_list(payload.get("events"))
    if events:
        lines.append(f"events: {len(events)}")
        for e in events:
            if not isinstance(e, dict):
                continue
            lines.append(
                f"- {e.get('place_name')} | pop={e.get('current_popularity')} | "
                f"%={e.get('percentage_of_usual')} | mag={e.get('spike_magnitude')} | "
                f"at={fmt_dt_func(e.get('recorded_at'))} | minutes_ago={e.get('minutes_ago')}"
            )
    return lines

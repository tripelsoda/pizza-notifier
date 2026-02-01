from __future__ import annotations

from typing import Any, Dict, List, Optional


def safe_list(v: Any) -> List[Any]:
    return v if isinstance(v, list) else []


def safe_dict(v: Any) -> Dict[str, Any]:
    return v if isinstance(v, dict) else {}


def _pct_value(x: Any) -> Optional[int]:
    # percentage_of_usual can be int, float, or None
    if isinstance(x, (int, float)):
        return int(x)
    return None


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


def is_spike_payload_over_threshold(payload: Dict[str, Any], min_pct: int = 300) -> bool:
    """
    True only if there is a spike AND at least one spike has percentage_of_usual >= min_pct.
    Checks both `events` and `data`.
    """
    events = safe_list(payload.get("events"))
    for e in events:
        if not isinstance(e, dict):
            continue
        pct = _pct_value(e.get("percentage_of_usual"))
        if pct is not None and pct >= min_pct:
            return True

    data = safe_list(payload.get("data"))
    for item in data:
        if not isinstance(item, dict):
            continue
        if item.get("is_spike") is not True:
            continue
        pct = _pct_value(item.get("percentage_of_usual"))
        if pct is not None and pct >= min_pct:
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


def spike_signature_over_threshold(payload: Dict[str, Any], min_pct: int = 300) -> Optional[str]:
    """
    Same idea as spike_signature(), but ONLY when there is at least one spike with
    percentage_of_usual >= min_pct.

    Returns a signature based on all qualifying spikes (events first if present),
    so you still get de-duping when multiple spikes are active.
    """
    if not is_spike_payload_over_threshold(payload, min_pct=min_pct):
        return None

    events = safe_list(payload.get("events"))
    qualifying_events: List[str] = []
    for e in events:
        if not isinstance(e, dict):
            continue
        pct = _pct_value(e.get("percentage_of_usual"))
        if pct is None or pct < min_pct:
            continue
        qualifying_events.append(
            f"{e.get('place_id')}|{e.get('recorded_at')}|{e.get('spike_magnitude')}|{pct}"
        )

    if qualifying_events:
        qualifying_events.sort()
        return f"EVENTS>={min_pct}:" + ";".join(qualifying_events)

    # Fallback: qualifying spiky places in data
    data = safe_list(payload.get("data"))
    qualifying_places: List[str] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        if item.get("is_spike") is not True:
            continue
        pct = _pct_value(item.get("percentage_of_usual"))
        if pct is None or pct < min_pct:
            continue
        qualifying_places.append(
            f"{item.get('place_id')}|{item.get('recorded_at')}|{item.get('spike_magnitude')}|{pct}"
        )

    qualifying_places.sort()
    return f"PLACES>={min_pct}:" + ";".join(qualifying_places)


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

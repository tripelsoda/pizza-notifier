from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def safe_list(v: Any) -> List[Any]:
    return v if isinstance(v, list) else []


def fmt(v: Any) -> str:
    return "-" if v is None else str(v)


def normalize_int(v: Any) -> Optional[int]:
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    return None


def extract_spikes(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    spikes: List[Dict[str, Any]] = []

    events = safe_list(payload.get("events"))
    for e in events:
        if not isinstance(e, dict):
            continue
        spikes.append({
            "place_name": e.get("place_name"),
            "current_popularity": e.get("current_popularity"),
            "percentage_of_usual": e.get("percentage_of_usual"),
            "spike_magnitude": e.get("spike_magnitude"),
            "minutes_ago": e.get("minutes_ago"),
            "recorded_at": e.get("recorded_at"),
        })

    if spikes:
        return spikes

    data = safe_list(payload.get("data"))
    for item in data:
        if not isinstance(item, dict):
            continue
        if item.get("is_spike") is True:
            spikes.append({
                "place_name": item.get("name"),
                "current_popularity": item.get("current_popularity"),
                "percentage_of_usual": item.get("percentage_of_usual"),
                "spike_magnitude": item.get("spike_magnitude"),
                "minutes_ago": None,
                "recorded_at": item.get("recorded_at"),
            })

    return spikes


def pick_primary_spike(spikes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not spikes:
        return None

    def key(s: Dict[str, Any]) -> Tuple[int, int]:
        pct = normalize_int(s.get("percentage_of_usual")) or -1
        pop = normalize_int(s.get("current_popularity")) or -1
        return (pct, pop)

    return max(spikes, key=key)


def _box(lines: List[str]) -> str:
    width = max(len(line) for line in lines) if lines else 0
    top = "┌" + "─" * (width + 2) + "┐"
    mid = "\n".join("│ " + line.ljust(width) + " │" for line in lines)
    bot = "└" + "─" * (width + 2) + "┘"
    return f"{top}\n{mid}\n{bot}"

def pretty_spike_text(payload: dict, fmt_dt_func) -> str:
    spikes = extract_spikes(payload)
    primary = pick_primary_spike(spikes)

    ts = fmt_dt_func(payload.get("timestamp"))
    overall_index = fmt(payload.get("overall_index"))
    defcon = fmt(payload.get("defcon_level"))
    active_spikes = fmt(payload.get("active_spikes"))

    lines = [
        "PizzINT Spike Alert",
        f"Time: {ts}",
        f"DEFCON {defcon} | Index {overall_index} | Spikes {active_spikes}",
    ]

    if primary:
        name = fmt(primary.get("place_name"))
        pop = fmt(primary.get("current_popularity"))
        pct = primary.get("percentage_of_usual")
        pct_s = f"{pct}%" if pct is not None else "-"
        mag = fmt(primary.get("spike_magnitude"))
        mins = primary.get("minutes_ago")
        mins_s = f"{mins}m ago" if isinstance(mins, int) else ""
        lines += [
            "",
            f"Top: {name}",
            f"pop {pop} | {pct_s} | {mag} | {mins_s}".strip(),
        ]

    if spikes:
        lines.append("")
        lines.append("Active spikes:")
        for s in spikes[:5]:
            n = fmt(s.get("place_name"))
            p = fmt(s.get("current_popularity"))
            pct2 = s.get("percentage_of_usual")
            pct2s = f"{pct2}%" if pct2 is not None else "-"
            m = fmt(s.get("spike_magnitude"))
            mi = s.get("minutes_ago")
            mis = f"{mi}m" if isinstance(mi, int) else ""
            lines.append(f"- {n} | pop {p} | {pct2s} | {m} | {mis}".strip())

    return "\n".join(lines)

def pretty_spike_text_telegram_html(payload: dict, fmt_dt_func) -> str:
    spikes = extract_spikes(payload)
    primary = pick_primary_spike(spikes)

    ts = fmt_dt_func(payload.get("timestamp"))
    overall_index = fmt(payload.get("overall_index"))
    defcon = fmt(payload.get("defcon_level"))
    active_spikes = fmt(payload.get("active_spikes"))

    lines = []
    lines.append("🍕 <b>PizzINT Spike Alert</b>")
    lines.append(f"🕒 <b>Time:</b> {ts}")
    lines.append(f"🛡️ <b>DEFCON</b> {defcon}   •   📈 <b>Index</b> {overall_index}   •   ⚠️ <b>Spikes</b> {active_spikes}")

    if primary:
        name = fmt(primary.get("place_name"))
        pop = fmt(primary.get("current_popularity"))
        pct = primary.get("percentage_of_usual")
        pct_s = f"<b>{pct}%</b>" if pct is not None else "-"
        mag = fmt(primary.get("spike_magnitude"))
        mins = primary.get("minutes_ago")
        mins_s = f"{mins}m ago" if isinstance(mins, int) else ""

        lines.append("")
        lines.append("🔥 <b>Top spike</b>")
        lines.append(f"🏷️ {name}")
        lines.append(f"👥 pop {pop}   •   {pct_s}   •   🚨 {mag}   •   ⏱️ {mins_s}".strip())

    if spikes:
        lines.append("")
        lines.append("📍 <b>Active spikes</b>")
        for s in spikes[:8]:
            n = fmt(s.get("place_name"))
            p = fmt(s.get("current_popularity"))
            pct2 = s.get("percentage_of_usual")
            pct2s = f"<b>{pct2}%</b>" if pct2 is not None else "-"
            m = fmt(s.get("spike_magnitude"))
            mi = s.get("minutes_ago")
            mis = f"{mi}m" if isinstance(mi, int) else ""
            lines.append(f"• {n} — pop {p} — {pct2s} — {m} — {mis}".strip())

    lines.append("")
    lines.append("🔗 <b></b> <a href='https://t.me/+ozxRG_0RksRiZWY0'></a>")

    return "\n".join(lines)


def pretty_spike_card(payload: Dict[str, Any], fmt_dt_func) -> str:
    ts = fmt_dt_func(payload.get("timestamp"))
    overall_index = fmt(payload.get("overall_index"))
    defcon = fmt(payload.get("defcon_level"))
    active_spikes = fmt(payload.get("active_spikes"))

    spikes = extract_spikes(payload)
    primary = pick_primary_spike(spikes)

    if primary:
        name = fmt(primary.get("place_name"))
        pop = fmt(primary.get("current_popularity"))
        pct = primary.get("percentage_of_usual")
        pct_s = f"{pct}%" if pct is not None else "-"
        mag = fmt(primary.get("spike_magnitude"))
        mins = primary.get("minutes_ago")
        mins_s = f"{mins}m ago" if isinstance(mins, int) else ""
    else:
        name = "No spike"
        pop = "-"
        pct_s = "-"
        mag = "-"
        mins_s = ""

    lines = [
        "🍕  PizzINT Spike Alert",
        f"Time: {ts}",
        f"DEFCON {defcon}   Index {overall_index}   Spikes {active_spikes}",
        "",
        f"Top spike: {name}",
        f"pop {pop}   {pct_s}   {mag}   {mins_s}".strip(),
    ]

    # show up to 3 spikes
    if spikes:
        lines.append("")
        lines.append("Active:")
        for s in sorted(
            spikes,
            key=lambda x: (normalize_int(x.get("percentage_of_usual")) or -1, normalize_int(x.get("current_popularity")) or -1),
            reverse=True
        )[:3]:
            n = fmt(s.get("place_name"))
            p = fmt(s.get("current_popularity"))
            pct2 = s.get("percentage_of_usual")
            pct2s = f"{pct2}%" if pct2 is not None else "-"
            m = fmt(s.get("spike_magnitude"))
            mi = s.get("minutes_ago")
            mis = f"{mi}m" if isinstance(mi, int) else ""
            lines.append(f"• {n} | pop {p} | {pct2s} | {m} | {mis}".strip())


    return _box(lines)

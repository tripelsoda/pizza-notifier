from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch


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


def safe_filename(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", s)


def clamp_text(s: str, max_len: int) -> str:
    s = s or ""
    return s if len(s) <= max_len else s[: max_len - 1] + "…"


def hex_to_rgba(hex_color: str, alpha: float):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b, alpha)


def apply_glow_to_patch(patch, glow_hex: str, strength: float = 1.0):
    """
    Real glow using multiple strokes behind the patch.
    """
    c1 = hex_to_rgba(glow_hex, 0.22 * strength)
    c2 = hex_to_rgba(glow_hex, 0.14 * strength)
    c3 = hex_to_rgba(glow_hex, 0.08 * strength)

    patch.set_path_effects([
        pe.Stroke(linewidth=22 * strength, foreground=c3),
        pe.Stroke(linewidth=14 * strength, foreground=c2),
        pe.Stroke(linewidth=8 * strength, foreground=c1),
        pe.Normal(),
    ])


def apply_glow_to_text(text_obj, glow_hex: str, strength: float = 1.0):
    c1 = hex_to_rgba(glow_hex, 0.25 * strength)
    c2 = hex_to_rgba(glow_hex, 0.16 * strength)
    c3 = hex_to_rgba(glow_hex, 0.09 * strength)
    text_obj.set_path_effects([
        pe.Stroke(linewidth=10 * strength, foreground=c3),
        pe.Stroke(linewidth=6 * strength, foreground=c2),
        pe.Stroke(linewidth=3 * strength, foreground=c1),
        pe.Normal(),
    ])


def apply_glow_to_line(line_obj, glow_hex: str, strength: float = 1.0):
    c1 = hex_to_rgba(glow_hex, 0.28 * strength)
    c2 = hex_to_rgba(glow_hex, 0.18 * strength)
    c3 = hex_to_rgba(glow_hex, 0.10 * strength)
    line_obj.set_path_effects([
        pe.Stroke(linewidth=9 * strength, foreground=c3),
        pe.Stroke(linewidth=6 * strength, foreground=c2),
        pe.Stroke(linewidth=3.5 * strength, foreground=c1),
        pe.Normal(),
    ])


def draw_round_rect(ax, x, y, w, h, radius, face, edge=None, lw=1.0, alpha=1.0) -> FancyBboxPatch:
    rect = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        linewidth=lw,
        edgecolor=edge if edge else face,
        facecolor=face,
        alpha=alpha,
        transform=ax.transAxes,
    )
    ax.add_patch(rect)
    return rect


def draw_trend_icon(ax, x, y, w, h, color, glow_hex: Optional[str] = None):
    xs = [x + w * 0.18, x + w * 0.42, x + w * 0.62, x + w * 0.82]
    ys = [y + h * 0.35, y + h * 0.30, y + h * 0.55, y + h * 0.70]
    line = ax.plot(xs, ys, color=color, linewidth=2.6, transform=ax.transAxes, solid_capstyle="round")[0]
    if glow_hex:
        apply_glow_to_line(line, glow_hex, strength=1.2)

    arrow = ax.plot(
        [xs[-1] - w * 0.06, xs[-1], xs[-1] - w * 0.02],
        [ys[-1] - h * 0.06, ys[-1], ys[-1] - h * 0.10],
        color=color,
        linewidth=2.6,
        transform=ax.transAxes,
        solid_capstyle="round",
    )[0]
    if glow_hex:
        apply_glow_to_line(arrow, glow_hex, strength=1.2)


def draw_spike_badge(ax, x, y, text, fill, border, icon_fill, icon_border, text_color, icon_color):
    badge_w = 0.33
    badge_h = 0.09

    outer = draw_round_rect(ax, x, y, badge_w, badge_h, radius=14, face=fill, edge=border, lw=1.8)
    apply_glow_to_patch(outer, border, strength=1.1)

    icon_w = badge_h * 0.82
    icon_h = badge_h * 0.82
    icon_x = x + 0.015
    icon_y = y + (badge_h - icon_h) / 2

    icon = draw_round_rect(ax, icon_x, icon_y, icon_w, icon_h, radius=11, face=icon_fill, edge=icon_border, lw=1.2)
    apply_glow_to_patch(icon, border, strength=0.8)

    draw_trend_icon(ax, icon_x, icon_y, icon_w, icon_h, icon_color, glow_hex=border)

    t = ax.text(
        icon_x + icon_w + 0.018,
        y + badge_h / 2,
        text,
        color=text_color,
        fontsize=20,
        fontweight="bold",
        transform=ax.transAxes,
        va="center",
        ha="left",
    )
    apply_glow_to_text(t, border, strength=1.1)


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


def render_simple_spike_card(
    payload: Dict[str, Any],
    fmt_dt_func,
    tz_name: str,
    output_dir: str,
) -> str:
    os.makedirs(output_dir, exist_ok=True)

    spikes = extract_spikes(payload)
    primary = pick_primary_spike(spikes)

    BG = "#0b1220"
    CARD = "#0f1b2e"
    BORDER = "#1d2b44"
    TEXT = "#e6edf6"
    MUTED = "#9fb0c3"

    RED = "#ef4444"
    RED_DARK = "#2a0f16"
    GREEN = "#22c55e"
    AMBER = "#f59e0b"

    fig = plt.figure(figsize=(12.5, 7.0), dpi=220)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.axis("off")

    # Main card with strong glow
    card = draw_round_rect(ax, 0.04, 0.06, 0.92, 0.88, radius=18, face=CARD, edge=BORDER, lw=1.8)
    apply_glow_to_patch(card, "#60a5fa", strength=1.25)

    # Header
    title = ax.text(0.075, 0.90, "PizzINT", color=TEXT, fontsize=30, fontweight="bold", transform=ax.transAxes, va="center")
    apply_glow_to_text(title, "#93c5fd", strength=1.1)

    ax.text(0.075, 0.855, "Spike monitor", color=MUTED, fontsize=15, transform=ax.transAxes)

    ts = fmt_dt_func(payload.get("timestamp"))
    ax.text(0.72, 0.90, "Last update", color=MUTED, fontsize=12, transform=ax.transAxes)
    ax.text(0.72, 0.865, ts, color=TEXT, fontsize=15, transform=ax.transAxes)

    # Small badges row
    def badge(x, y, text, face, edge, glow_hex):
        b = draw_round_rect(ax, x, y, 0.18, 0.065, radius=12, face=face, edge=edge, lw=1.4)
        apply_glow_to_patch(b, glow_hex, strength=0.9)
        ax.text(x + 0.016, y + 0.020, text, color=TEXT, fontsize=15, fontweight="bold", transform=ax.transAxes)

    overall_index = payload.get("overall_index")
    defcon = payload.get("defcon_level")
    active_spikes = payload.get("active_spikes")

    defcon_glow = AMBER if isinstance(defcon, int) and defcon <= 3 else GREEN
    badge(0.075, 0.79, f"DEFCON {fmt(defcon)}", face="#0c2a1a", edge=defcon_glow, glow_hex=defcon_glow)
    badge(0.275, 0.79, f"Index {fmt(overall_index)}", face="#13243d", edge=BORDER, glow_hex="#60a5fa")
    badge(0.475, 0.79, f"Spikes {fmt(active_spikes)}", face="#13243d", edge=BORDER, glow_hex="#60a5fa")

    # Primary spike badge
    if primary:
        pct = primary.get("percentage_of_usual")
        pct_txt = f"{pct}%" if pct is not None else "SPIKE"
        draw_spike_badge(
            ax=ax,
            x=0.075,
            y=0.685,
            text=f"{pct_txt} SPIKE",
            fill=RED_DARK,
            border=RED,
            icon_fill="#1f0b10",
            icon_border=RED,
            text_color=RED,
            icon_color=RED,
        )
    else:
        draw_spike_badge(
            ax=ax,
            x=0.075,
            y=0.685,
            text="NO SPIKE",
            fill="#0c2a1a",
            border=GREEN,
            icon_fill="#081d12",
            icon_border=GREEN,
            text_color=GREEN,
            icon_color=GREEN,
        )

    # Section title
    ax.text(0.075, 0.61, "Active spikes", color=MUTED, fontsize=15, fontweight="bold", transform=ax.transAxes)

    # List area with glow
    box = draw_round_rect(ax, 0.075, 0.18, 0.85, 0.40, radius=14, face="#0c1627", edge=BORDER, lw=1.3)
    apply_glow_to_patch(box, "#334155", strength=1.0)

    if not spikes:
        ax.text(0.095, 0.52, "Nothing to show.", color=TEXT, fontsize=18, transform=ax.transAxes)
    else:
        def sk(s):
            pct = normalize_int(s.get("percentage_of_usual")) or -1
            pop = normalize_int(s.get("current_popularity")) or -1
            return (pct, pop)

        spikes_sorted = sorted(spikes, key=sk, reverse=True)[:6]

        y = 0.54
        step = 0.070
        for s in spikes_sorted:
            name = clamp_text(fmt(s.get("place_name")), 46)
            pop = fmt(s.get("current_popularity"))
            pct = s.get("percentage_of_usual")
            pct_s = f"{pct}%" if pct is not None else "-"
            mag = fmt(s.get("spike_magnitude"))
            when = s.get("minutes_ago")
            when_s = f"{when}m ago" if isinstance(when, int) else ""

            right = f"pop {pop}   {pct_s}   {mag}   {when_s}".strip()

            ax.text(0.095, y, "•", color=RED, fontsize=20, transform=ax.transAxes, va="center")
            ax.text(0.112, y, name, color=TEXT, fontsize=16, transform=ax.transAxes, va="center")
            ax.text(0.92, y, right, color=MUTED, fontsize=15, transform=ax.transAxes, va="center", ha="right")
            y -= step

    out_name = safe_filename(f"pizzint_card_{ts}.png")
    path = os.path.join(output_dir, out_name)
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path

import os
import time

from config import load_config
from client import Client
from spike_detector import spike_signature_over_threshold
from telegram_notifier import load_telegram_config, send_message, send_photo
from renderer import render_simple_spike_card
from pretty_print import pretty_spike_text_telegram_html

LAST_SIG_FILE = "last_sig.txt"


def read_last_sig(path: str = LAST_SIG_FILE) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            s = f.read().strip()
            return s or None
    except FileNotFoundError:
        return None


def write_last_sig(sig: str, path: str = LAST_SIG_FILE) -> None:
    # write atomically so it never ends up half-written
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(sig)
    os.replace(tmp, path)


def main():
    cfg = load_config()
    tg = load_telegram_config()
    client = Client(url=cfg.url, tz_name=cfg.tz_name, timeout_seconds=cfg.timeout_seconds)

    last_sig = read_last_sig()

    # Run 5 checks, one per minute (GitHub cron runs every 5 minutes)
    for i in range(5):
        try:
            payload = client.fetch_dashboard(nocache=cfg.nocache)
            sig = spike_signature(payload)

            if sig is not None and sig != last_sig:
                last_sig = sig
                write_last_sig(sig)

                # Send message (HTML)
                text = pretty_spike_text_telegram_html(payload, client.fmt_dt)
                send_message(tg, text, parse_mode="HTML")

                # Render + send image
                img_path = render_simple_spike_card(
                    payload=payload,
                    fmt_dt_func=client.fmt_dt,
                    tz_name=cfg.tz_name,
                    output_dir=cfg.output_dir,
                )
                send_photo(tg, img_path, caption="🍕 PizzINT spike card")

        except Exception as e:
            print(f"error: {e}")

        if i < 4:
            time.sleep(60)


if __name__ == "__main__":
    main()

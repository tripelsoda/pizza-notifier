from __future__ import annotations
from telegram_notifier import load_telegram_config, send_message, send_photo


import time

from config import load_config
from client import Client
from spike_detector import spike_signature, spike_summary_lines
from renderer import render_simple_spike_card
from pretty_print import pretty_spike_text
from pretty_print import pretty_spike_text_telegram_html




def main() -> None:
    tg = load_telegram_config()
    cfg = load_config()
    client = Client(url=cfg.url, tz_name=cfg.tz_name, timeout_seconds=cfg.timeout_seconds)

    last_sig: str | None = None

    while True:
        try:
            payload = client.fetch_dashboard(nocache=cfg.nocache)
            sig = spike_signature(payload)

            # Only print when a NEW spike signature appears
            if sig is not None and sig != last_sig:
                last_sig = sig
                print(pretty_spike_text(payload, client.fmt_dt))

                text = pretty_spike_text_telegram_html(payload, client.fmt_dt)
                send_message(tg, text, parse_mode="HTML")

                # Print spike summary
                for line in spike_summary_lines(payload, client.fmt_dt):
                    print(line)

                # Save image
                img_path = render_simple_spike_card(
                    payload=payload,
                    fmt_dt_func=client.fmt_dt,
                    tz_name=cfg.tz_name,
                    output_dir=cfg.output_dir,
                )
                print(f"saved_image: {img_path}")



        except Exception as e:
            # If you truly want zero prints except spikes, delete the next line.
            print(f"error: {e}")

        time.sleep(cfg.poll_seconds)


if __name__ == "__main__":
    main()

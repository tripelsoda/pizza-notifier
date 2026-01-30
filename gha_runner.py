import time

from config import load_config
from client import Client
from spike_detector import spike_signature
from telegram_notifier import load_telegram_config, send_message
from pretty_print import pretty_spike_text  # change if your function name differs


def main():
    cfg = load_config()
    tg = load_telegram_config()
    client = Client(url=cfg.url, tz_name=cfg.tz_name, timeout_seconds=cfg.timeout_seconds)

    last_sig = None

    # Run 5 checks, one per minute (since GitHub cron is every 5 minutes)
    for i in range(5):
        payload = client.fetch_dashboard(nocache=cfg.nocache)
        sig = spike_signature(payload)

        if sig is not None and sig != last_sig:
            last_sig = sig
            text = pretty_spike_text(payload, client.fmt_dt)
            send_message(tg, text)

        if i < 4:
            time.sleep(60)


if __name__ == "__main__":
    main()

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass(frozen=True)
class TelegramConfig:
    token: str
    chat_id: str


def load_telegram_config() -> TelegramConfig:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    if not token or not chat_id:
        raise RuntimeError(
            "Missing Telegram config. Set environment variables:\n"
            "TELEGRAM_BOT_TOKEN\n"
            "TELEGRAM_CHAT_ID\n"
        )

    return TelegramConfig(token=token, chat_id=chat_id)


def send_message(cfg, text: str, timeout: int = 20, parse_mode: str | None = None) -> None:
    url = f"https://api.telegram.org/bot{cfg.token}/sendMessage"
    data = {
        "chat_id": cfg.chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    if parse_mode:
        data["parse_mode"] = parse_mode

    r = requests.post(url, data=data, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(f"Telegram error {r.status_code}: {r.text}")




def send_photo(cfg: TelegramConfig, photo_path: str, caption: Optional[str] = None, timeout: int = 30) -> None:
    url = f"https://api.telegram.org/bot{cfg.token}/sendPhoto"
    with open(photo_path, "rb") as f:
        files = {"photo": f}
        data = {"chat_id": cfg.chat_id}
        if caption:
            data["caption"] = caption
        r = requests.post(url, data=data, files=files, timeout=timeout)
    r.raise_for_status()

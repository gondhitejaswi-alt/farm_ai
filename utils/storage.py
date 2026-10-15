"""
Farm AI - Persistent local storage (additive module)
====================================================
Keeps the farmer's history, chat questions and settings on disk so nothing is
lost when the browser is refreshed or the app is restarted.

Files live in  data/user_data/  as plain JSON (easy to back up / inspect).
No personal data beyond what the farmer typed is stored, and nothing is sent
anywhere. Writes are atomic so a crash can never corrupt the history file.
"""

import os, json, tempfile, threading, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_DIR = os.path.join(ROOT, "data", "user_data")
HISTORY_FILE = os.path.join(USER_DIR, "history.json")
CHAT_FILE = os.path.join(USER_DIR, "chat_history.json")
SETTINGS_FILE = os.path.join(USER_DIR, "settings.json")

MAX_HISTORY = 500
MAX_CHAT = 200
_lock = threading.Lock()

DEFAULT_SETTINGS = {
    "lang": "te",
    "large_text": False,
    "high_contrast": False,
    "developer_mode": False,
    "district": None,
    "crop": None,
}


def _read(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write(path, data):
    os.makedirs(USER_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=USER_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception:
        try:
            os.remove(tmp)
        except Exception:
            pass


# ── History of farm advice runs ───────────────────────────────
def load_history() -> list:
    h = _read(HISTORY_FILE, [])
    return h if isinstance(h, list) else []


def add_history(entry: dict) -> bool:
    """Append an entry unless an identical run (same inputs) was just saved.
    Returns True if a new row was written."""
    entry = dict(entry)
    entry.setdefault("time", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    sig = json.dumps({k: v for k, v in entry.items() if k != "time"}, sort_keys=True, default=str)
    with _lock:
        h = load_history()
        if h and h[-1].get("_sig") == sig:
            return False
        entry["_sig"] = sig
        h.append(entry)
        _write(HISTORY_FILE, h[-MAX_HISTORY:])
    return True


def clear_history():
    with _lock:
        _write(HISTORY_FILE, [])


# ── Chat questions ─────────────────────────────────────────────
def load_chat() -> list:
    c = _read(CHAT_FILE, [])
    return c if isinstance(c, list) else []


def save_chat(chat: list):
    with _lock:
        _write(CHAT_FILE, chat[-MAX_CHAT:])


# ── Settings ───────────────────────────────────────────────────
def load_settings() -> dict:
    s = dict(DEFAULT_SETTINGS)
    saved = _read(SETTINGS_FILE, {})
    if isinstance(saved, dict):
        s.update({k: v for k, v in saved.items() if k in DEFAULT_SETTINGS})
    return s


def save_settings(settings: dict):
    with _lock:
        _write(SETTINGS_FILE, {k: settings.get(k) for k in DEFAULT_SETTINGS})

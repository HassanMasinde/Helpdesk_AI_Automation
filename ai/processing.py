"""Small metadata-only ledger for tickets already handled by the agent."""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path


LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "processed_tickets.json"
_LOCK = threading.Lock()


def _now():
    return datetime.now(timezone.utc).isoformat()


def _load():
    if not LEDGER_PATH.exists():
        return {}
    try:
        data = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data):
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = LEDGER_PATH.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    temporary.replace(LEDGER_PATH)


def get(ticket_id):
    with _LOCK:
        return _load().get(str(ticket_id))


def has_been_handled(ticket_id):
    return get(ticket_id) is not None


def mark_handled(ticket_id, created_on="", status="processed"):
    with _LOCK:
        data = _load()
        data[str(ticket_id)] = {
            "created_on": created_on or data.get(str(ticket_id), {}).get("created_on", ""),
            "status": status,
            "updated_at": _now(),
        }
        _save(data)

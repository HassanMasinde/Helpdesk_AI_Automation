"""
dashboard_server.py

A small LOCAL web dashboard for the Helpdesk AI agent.

It serves a browser page at http://127.0.0.1:8790 and lets you:
  - "Check Now"   -> run ONE ticket cycle
  - "Start"       -> run the continuous monitoring loop
  - "Stop"        -> stop after the current ticket finishes

It uses only Python's built-in http.server, so there are NO new dependencies.
It binds to 127.0.0.1 only, so it is not reachable from other machines.
"""

import asyncio
import json
import os
import queue
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import run_agent
from ai.analyzer import TICKET_TYPE_LABELS
from ai.processing import mark_handled

ROOT = Path(__file__).resolve().parent
DASHBOARD_DIR = ROOT / "dashboard"
HOST = "127.0.0.1"
PORT = int(os.getenv("PORT", "8790"))
MAX_LOG_LINES = 300

STATUS_TEXT = {
    "starting": "Agent starting...",
    "launching": "Launching browser...",
    "logging_in": "Logging into Loyon...",
    "checking": "Checking tickets...",
    "processing": "Processing tickets...",
    "sleeping": "Sleeping until next check.",
    "idle": "No open tickets to process.",
    "stopped": "Agent stopped.",
}


class Hub:
    """Shared, thread-safe state between the agent thread and the web server."""

    def __init__(self):
        self.lock = threading.Lock()
        self.subscribers = []
        self.state = {
            "running": False,
            "mode": None,          # "check" or "monitor"
            "status": "idle",
            "current_ticket": None,
            "resolution": None,
            "counts": {"found": 0, "saved": 0, "skipped": 0, "failed": 0},
            "last_error": None,
            "last_updated": _now(),
            "background": False,   # run Loyon headlessly (background) or visibly
        }
        self.log = []
        self.tickets = {}
        self.search_tickets = []

    # ---- state helpers -----------------------------------------------------
    def _touch(self):
        self.state["last_updated"] = _now()

    def reset_run(self, mode):
        with self.lock:
            self.state["running"] = True
            self.state["mode"] = mode
            self.state["status"] = "starting"
            self.state["current_ticket"] = None
            self.state["resolution"] = None
            self.state["counts"] = {"found": 0, "saved": 0, "skipped": 0, "failed": 0}
            self.state["last_error"] = None
            self.tickets = {}
            self._touch()
        self.publish()

    def finish_run(self):
        with self.lock:
            self.state["running"] = False
            self.state["mode"] = None
            self.state["status"] = "idle"
            self.state["current_ticket"] = None
            self._touch()
        self.publish()

    def add_log(self, message):
        with self.lock:
            self._append_log(message)
            self._touch()
        self.publish()

    def _append_log(self, message):
        # Caller must already hold self.lock.
        self.log.append({"ts": _now(), "message": message})
        if len(self.log) > MAX_LOG_LINES:
            self.log = self.log[-MAX_LOG_LINES:]

    def _upsert_ticket(self, ticket_id, **fields):
        # Caller must already hold self.lock.
        if ticket_id is None:
            return
        key = str(ticket_id)
        record = self.tickets.get(key)
        if record is None:
            record = {
                "id": key,
                "subject": "",
                "description": "",
                "type": "",
                "status": "found",
                "reason": "",
                "resolution": "",
                "source": "",
                "created_on": "",
                "updated_at": _now(),
            }
            self.tickets[key] = record
        for name, value in fields.items():
            if value is not None:
                record[name] = value
        record["updated_at"] = _now()

    def apply_resolution_edit(self, ticket_id, text, source="manual"):
        with self.lock:
            self._upsert_ticket(
                ticket_id,
                resolution=text or "",
                source=source if text else "",
                status="saved",
                reason="",
            )
            for ticket in self.search_tickets:
                if str(ticket.get("id")) == str(ticket_id):
                    ticket["resolution"] = text or ""
                    ticket["updated_at"] = _now()
            self._append_log(
                f"{'Updated' if text else 'Cleared'} resolution for #{ticket_id}."
            )
            self._touch()
        self.publish()

    def set_search_tickets(self, tickets):
        with self.lock:
            self.search_tickets = [dict(ticket) for ticket in tickets]
            self._touch()
        self.publish()

    # ---- event handling from the agent ------------------------------------
    def handle(self, kind, data):
        with self.lock:
            if kind == "status":
                new_state = data.get("state", "idle")
                if new_state != self.state["status"]:
                    self.state["status"] = new_state
                    self._append_log(STATUS_TEXT.get(new_state, new_state))
            elif kind == "stats":
                if "found" in data:
                    self.state["counts"]["found"] = data["found"]
                    self._append_log(f"Found {data['found']} eligible ticket(s).")
            elif kind == "found_tickets":
                for item in data.get("tickets", []):
                    self._upsert_ticket(
                        item.get("id"),
                        created_on=item.get("created_on", ""),
                        status="found",
                    )
            elif kind == "ticket":
                event = data.get("event")
                ticket_id = data.get("ticket_id")
                if event == "processing":
                    ticket_type = data.get("ticket_type")
                    label = TICKET_TYPE_LABELS.get(ticket_type, ticket_type or "Unknown")
                    self.state["current_ticket"] = {
                        "id": ticket_id,
                        "subject": data.get("subject"),
                        "type": label,
                    }
                    self._upsert_ticket(
                        ticket_id,
                        subject=data.get("subject", ""),
                        description=data.get("subject", ""),
                        type=label,
                        status="processing",
                        reason="",
                    )
                    self._append_log(
                        f"Processing #{ticket_id} [{label}]: {data.get('subject', '')}"
                    )
                elif event == "saved":
                    self.state["counts"]["saved"] += 1
                    source = data.get("source") or "unknown"
                    resolution = data.get("resolution") or (self.state.get("resolution") or {}).get("text", "")
                    self._upsert_ticket(
                        ticket_id,
                        status="saved",
                        source=source,
                        resolution=resolution,
                        reason="",
                    )
                    self._append_log(f"Saved resolution for #{ticket_id} ({source}).")
                elif event == "skipped":
                    self.state["counts"]["skipped"] += 1
                    reason = data.get("reason") or "Already has a resolution."
                    current = self.tickets.get(str(ticket_id), {})
                    resolution = data.get("resolution")
                    if resolution is None or resolution == "":
                        resolution = current.get("resolution", "")
                    self._upsert_ticket(
                        ticket_id,
                        status="skipped",
                        reason=reason,
                        subject=data.get("subject", ""),
                        description=data.get("subject", ""),
                        resolution=resolution,
                        created_on=data.get("created_on") or current.get("created_on", ""),
                        type=data.get("ticket_type_label") or current.get("type", ""),
                        ticket_type=data.get("ticket_type") or current.get("ticket_type", ""),
                        ticket_type_label=data.get("ticket_type_label") or current.get("ticket_type_label", ""),
                    )
                    self._append_log(f"Skipped #{ticket_id}: {reason}")
                elif event == "failed":
                    self.state["counts"]["failed"] += 1
                    reason = data.get("reason") or "Unknown error."
                    self._upsert_ticket(
                        ticket_id,
                        status="failed",
                        reason=reason,
                        subject=data.get("subject", ""),
                    )
                    self._append_log(f"Failed #{ticket_id}: {reason}")
            elif kind == "resolution":
                self.state["resolution"] = {
                    "text": data.get("text"),
                    "source": data.get("source"),
                }
            elif kind == "error":
                self.state["last_error"] = data.get("message")
                self._append_log(f"Error: {data.get('message')}")
            elif kind == "log":
                message = data.get("message")
                if message:
                    self._append_log(message)
            self._touch()
        self.publish()

    # ---- subscribers (Server-Sent Events) ---------------------------------
    def subscribe(self):
        q = queue.Queue()
        with self.lock:
            self.subscribers.append(q)
        return q

    def unsubscribe(self, q):
        with self.lock:
            if q in self.subscribers:
                self.subscribers.remove(q)

    def publish(self):
        snapshot = self.snapshot()
        with self.lock:
            subscribers = list(self.subscribers)
        for q in subscribers:
            q.put(snapshot)

    def snapshot(self):
        with self.lock:
            return {
                "state": dict(self.state),
                "log": list(self.log[-60:]),
                "tickets": [dict(t) for t in self.tickets.values()],
                "search_tickets": [dict(t) for t in self.search_tickets],
            }


def _now():
    return datetime.now().strftime("%H:%M:%S")


class DashboardReporter:
    """Adapter: turns run_agent's emit() calls into dashboard state updates."""

    def __init__(self, hub):
        self.hub = hub

    def emit(self, kind, **data):
        self.hub.handle(kind, data)


hub = Hub()
run_agent.set_reporter(DashboardReporter(hub))
_agent_thread = None
_thread_lock = threading.Lock()


def _run_agent_thread(continuous, mode):
    try:
        asyncio.run(run_agent.agent_main(continuous=continuous))
    except Exception as error:  # noqa: BLE001 - surface any startup error to the UI
        hub.handle("error", {"message": str(error)})
        hub.add_log(f"Agent error: {error}")
    finally:
        hub.finish_run()


def start_agent(continuous, mode):
    global _agent_thread
    with _thread_lock:
        if hub.state["running"]:
            return False, "Agent is already running."
        hub.reset_run(mode)
        _agent_thread = threading.Thread(
            target=_run_agent_thread,
            args=(continuous, mode),
            daemon=True,
        )
        _agent_thread.start()
        return True, "Started."


def stop_agent():
    if not hub.state["running"]:
        return False, "Agent is not running."
    run_agent.request_stop()
    hub.add_log("Stop requested - finishing the current ticket...")
    return True, "Stopping."


def set_background(value):
    """Toggle whether Loyon opens in the background. Applies to the next operation."""
    value = bool(value)
    run_agent.set_headless(value)
    with hub.lock:
        hub.state["background"] = value
        hub._append_log(
            f"Loyon will run {'in the background' if value else 'visibly'} on the next operation."
        )
        hub._touch()
    hub.publish()
    return True, "Loyon will run in the background." if value else "Loyon will run visibly."


def update_ticket_resolution(ticket_id, text, created_on=None):
    if hub.state["running"]:
        return False, "Stop the agent before editing tickets."
    with _manual_lock:
        try:
            asyncio.run(run_agent.set_ticket_resolution(ticket_id, text, created_on))
        except Exception as error:  # noqa: BLE001 - report failure to the UI
            return False, f"Update failed: {error}"
    hub.apply_resolution_edit(ticket_id, text)
    mark_handled(ticket_id, created_on, status="deleted" if not text else "processed")
    return True, "Resolution updated." if text else "Resolution cleared."


def redo_ticket_resolution(ticket_id, created_on=None):
    if hub.state["running"]:
        return False, "Stop the agent before editing tickets.", ""
    with _manual_lock:
        try:
            ok, resolution = asyncio.run(run_agent.redo_ticket_resolution(ticket_id, created_on))
        except Exception as error:  # noqa: BLE001 - report failure to the UI
            return False, f"Redo failed: {error}", ""
    if ok:
        hub.apply_resolution_edit(ticket_id, resolution, source="redo")
        mark_handled(ticket_id, created_on, status="redo")
        return True, "Resolution regenerated.", resolution
    return False, resolution, ""


_manual_lock = threading.Lock()


def search_tickets(filters):
    if hub.state["running"]:
        return False, "Stop the agent before searching tickets.", []
    if not _manual_lock.acquire(blocking=False):
        return False, "Another Loyon browser operation is already running.", []
    try:
        tickets = asyncio.run(run_agent.fetch_tickets(filters.get("date_from"), filters.get("date_to")))
        query = (filters.get("query") or "").strip().lower()
        status = (filters.get("status") or "").lower()
        ticket_type = filters.get("ticket_type") or ""
        if query:
            tickets = [ticket for ticket in tickets if query in " ".join(str(ticket.get(field, "")) for field in ("id", "subject", "description", "resolution")).lower()]
        if status:
            tickets = [ticket for ticket in tickets if status in ticket.get("status", "").lower()]
        if ticket_type:
            tickets = [ticket for ticket in tickets if ticket.get("ticket_type") == ticket_type]
        hub.set_search_tickets(tickets)
        hub.add_log(f"Loaded {len(tickets)} ticket(s) for the selected date range.")
        return True, f"Found {len(tickets)} matching ticket(s).", tickets
    except Exception as error:  # noqa: BLE001 - report the UI-visible failure
        hub.add_log(f"Monthly ticket load failed: {error}")
        return False, f"Search failed: {error}", []
    finally:
        _manual_lock.release()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # keep the console quiet; the dashboard log is the source of truth

    # ---- helpers ----------------------------------------------------------
    def _json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def _serve_file(self, rel_path):
        if rel_path in ("", "/"):
            rel_path = "index.html"
        target = (DASHBOARD_DIR / rel_path.lstrip("/")).resolve()
        if DASHBOARD_DIR.resolve() not in target.parents and target != DASHBOARD_DIR.resolve():
            self.send_error(404)
            return
        if not target.is_file():
            self.send_error(404)
            return

        content_types = {
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
        }
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_types.get(target.suffix, "application/octet-stream"))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ---- routes -----------------------------------------------------------
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/status":
            self._json(hub.snapshot())
        elif path == "/api/tickets":
            self._json({"tickets": hub.snapshot()["tickets"]})
        elif path == "/api/search-tickets":
            self._json({"tickets": hub.snapshot()["search_tickets"]})
        elif path == "/api/events":
            self._stream_events()
        elif path.startswith("/api/"):
            self._json({"error": "Not found"}, 404)
        else:
            self._serve_file(path)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/check":
            ok, message = start_agent(continuous=False, mode="check")
            self._json({"ok": ok, "message": message}, 200 if ok else 409)
        elif path == "/api/start":
            ok, message = start_agent(continuous=True, mode="monitor")
            self._json({"ok": ok, "message": message}, 200 if ok else 409)
        elif path == "/api/stop":
            ok, message = stop_agent()
            self._json({"ok": ok, "message": message}, 200 if ok else 409)
        elif path == "/api/background":
            payload = self._read_body()
            ok, message = set_background(payload.get("background", False))
            self._json({"ok": ok, "message": message}, 200 if ok else 409)
        elif path == "/api/search-tickets":
            payload = self._read_body()
            ok, message, tickets = search_tickets(payload)
            self._json({"ok": ok, "message": message, "tickets": tickets}, 200 if ok else 409)
        elif path.startswith("/api/tickets/") and path.endswith("/resolution"):
            ticket_id = path[len("/api/tickets/"): -len("/resolution")]
            payload = self._read_body()
            text = payload.get("text", "")
            ok, message = update_ticket_resolution(ticket_id, text, payload.get("created_on"))
            self._json({"ok": ok, "message": message}, 200 if ok else 409)
        elif path.startswith("/api/tickets/") and path.endswith("/redo"):
            ticket_id = path[len("/api/tickets/"): -len("/redo")]
            payload = self._read_body()
            ok, message, resolution = redo_ticket_resolution(ticket_id, payload.get("created_on"))
            self._json({"ok": ok, "message": message, "resolution": resolution}, 200 if ok else 409)
        else:
            self._json({"error": "Not found"}, 404)

    def _stream_events(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        q = hub.subscribe()
        try:
            self.wfile.write(f"data: {json.dumps(hub.snapshot())}\n\n".encode("utf-8"))
            self.wfile.flush()
            while True:
                try:
                    snapshot = q.get(timeout=15)
                    self.wfile.write(f"data: {json.dumps(snapshot)}\n\n".encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, OSError):
            pass
        finally:
            hub.unsubscribe(q)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Helpdesk AI dashboard running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the dashboard.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

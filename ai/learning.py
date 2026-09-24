import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LEARNED_PATH = DATA_DIR / "learned_knowledge.json"

DEFAULT_THRESHOLD = 0.5
NEAR_DUPLICATE_THRESHOLD = 0.6

STOPWORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "any", "can",
    "had", "her", "was", "one", "our", "out", "has", "his", "how", "its",
    "now", "she", "than", "that", "this", "what", "when", "who", "will",
    "with", "your", "have", "from", "they", "been", "into", "them", "then",
    "there", "when", "where", "which", "would", "could", "should", "about",
    "also", "very", "just", "does", "doing", "being", "having", "only",
    "some", "such", "these", "those", "cannot", "please", "help", "support",
    "issue", "problem", "error", "ticket", "doesnt", "dont", "isnt", "cant",
}


def _normalize(text):
    return re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())


def _keywords(text):
    words = _normalize(text).split()
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]


def _score(query_words, entry):
    entry_words = set(entry.get("keywords", []))
    if not query_words or not entry_words:
        return 0.0
    query_set = set(query_words)
    intersection = len(query_set & entry_words)
    if intersection == 0:
        return 0.0
    return 2 * intersection / (len(query_set) + len(entry_words))


def load_learned():
    if not LEARNED_PATH.exists():
        return []
    try:
        data = json.loads(LEARNED_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_learned(entries):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LEARNED_PATH.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def find_learned_match(problem, threshold=DEFAULT_THRESHOLD, verified=None):
    query_words = _keywords(problem)
    if not query_words:
        return None, 0.0

    best_entry = None
    best_score = 0.0
    for entry in load_learned():
        if verified is not None and bool(entry.get("verified", False)) != bool(verified):
            continue
        score = _score(query_words, entry)
        if score > best_score:
            best_entry, best_score = entry, score

    if best_score >= threshold:
        return best_entry, best_score
    return None, best_score


def add_learned(problem, resolution, ticket_id, kind="solution", verified=False):
    entries = load_learned()
    query_words = _keywords(problem)
    ticket_id = str(ticket_id)

    for entry in entries:
        if entry.get("source_ticket") == ticket_id:
            return entry

    for entry in entries:
        if entry.get("kind") == kind and _score(query_words, entry) >= NEAR_DUPLICATE_THRESHOLD:
            return entry

    entry = {
        "id": uuid.uuid4().hex[:12],
        "keywords": query_words,
        "problem_summary": problem,
        "resolution": resolution,
        "source_ticket": ticket_id,
        "kind": kind,
        "verified": bool(verified),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    entries.append(entry)
    save_learned(entries)
    return entry


def mark_verified(ticket_id):
    entries = load_learned()
    changed = False
    for entry in entries:
        if entry.get("source_ticket") == str(ticket_id):
            entry["verified"] = True
            changed = True
    if changed:
        save_learned(entries)
    return changed

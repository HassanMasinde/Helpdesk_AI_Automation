"""
ai/analyzer.py

WHAT THIS FILE IS
-----------------
Pipeline STEP 1. It reads a support ticket and decides two things:
  1. its `category` (what kind of problem it is), and
  2. its `priority` (how urgent it is).

WHO IMPORTS THIS (and when it runs)
-----------------------------------
- `ai/__init__.py` imports `analyze_ticket` and calls it first inside `solve_ticket`.
- `main.py` (the browser flow) imports it too.

This module is deliberately "dumb but predictable": it only uses simple keyword
matching, so the result is easy to explain and never calls the network.
"""

# The five official ticket types used by Hanmak support.
TICKET_TYPE_LABELS = {
    "how_to": "How-To / Informational",
    "incident": "Incident",
    "service_request": "Service Request",
    "problem": "Problem",
    "change_request": "Change Request / RFC",
}

# Keyword hints for each ticket type (lowercase).
_HOW_TO = (
    "how do i", "how to", "how can i", "where can i", "where do i",
    "steps to", "guide", "tutorial", "set up", "setup", "configure",
    "export", "procedure", "instructions",
)
_CHANGE_REQUEST = (
    "rfc", "change request", "upgrad", "deploy", "deployment", "migrat",
    "rollout", "go live", "new server", "server upgrade", "configuration change",
    "patch the server", "new integration",
)
_PROBLEM = (
    "repeated", "recurring", "keeps happening", "keeps crashing", "every night",
    "every sunday", "multiple users", "multiple staff", "several staff",
    "widespread", "root cause", "intermittent", "again and again",
    "for the third time", "many users",
)
_SERVICE_REQUEST = (
    "create a new user", "create account", "new account", "new user", "add user",
    "grant access", "access rights", "permissions", "install software",
    "install ms office", "additional monitor", "second monitor", "new laptop",
    "new hardware", "provision", "new license",
)
_INCIDENT = (
    "crash", "freezing", "freezes", "not working", "not printing", "jammed",
    "down", "outage", "error", "failed", "failure", "cannot", "can't", "cant",
    "unable", "broken", "slow", "timeout", "timed out", "dropped",
    "disconnected", "stuck", "hanging", "not loading", "won't", "wont",
    "failing", "stops working", "problem", "issue",
)
# Strong incident words that should beat a "how do I..." phrasing.
_INCIDENT_STRONG = (
    "crash", "freezing", "not working", "down", "outage", "error",
    "broken", "jammed", "timeout", "cannot", "unable", "failed", "failure",
)


def classify_ticket_type(text):
    """
    Return one of the five ticket types based on simple keyword matching.

    Types: how_to, incident, service_request, problem, change_request.
    Order matters: a "how do I..." question wins unless it is clearly about
    something broken.
    """
    text = (text or "").lower()

    if any(word in text for word in _HOW_TO) and not any(
        word in text for word in _INCIDENT_STRONG
    ):
        return "how_to"
    if any(word in text for word in _CHANGE_REQUEST):
        return "change_request"
    if any(word in text for word in _PROBLEM):
        return "problem"
    if any(word in text for word in _SERVICE_REQUEST):
        return "service_request"
    if any(word in text for word in _INCIDENT):
        return "incident"
    return "how_to"



async def analyze_ticket(ticket):
    """
    Classify one ticket and return a small summary dictionary.

    Parameters
    ----------
    ticket : dict or object
        The ticket to analyze. A `dict` is expected, but any object that has
        `subject`, `description`, and `id` attributes is also accepted.

    Returns
    -------
    dict
        {
            "ticket_id": "...",
            "category": "account_access" or "general_support",
            "priority": "medium" or "normal",
            "summary": "...",
        }
    """

    # The same ticket may arrive as a dictionary OR as an object.
    # `isinstance(ticket, dict)` asks: "is this a dict?" (returns True/False).
    if isinstance(ticket, dict):
        # dict access: ticket.get("key", default) returns the value for "key",
        # or the default ("") if that key is missing (avoids a crash).
        subject = ticket.get("subject", "")
        description = ticket.get("description", "")
        ticket_id = ticket.get("id", "Unknown")
    else:
        # Object access: getattr(obj, "name", default) reads the attribute
        # "name" from the object, or the default if it doesn't exist.
        subject = getattr(ticket, "subject", "")
        description = getattr(ticket, "description", "")
        ticket_id = getattr(ticket, "id", "Unknown")

    # Combine subject + description into one lowercase string.
    # An f-string (f"...") lets us drop variables straight into the text.
    # .lower() makes matching case-insensitive ("Login" and "login" both match).
    text = f"{subject} {description}".lower()

    # Decide the category by looking for known keywords.
    # `any(...)` returns True if at least one item in the loop is True.
    # `kw in text` checks whether a keyword string appears inside `text`.
    if any(kw in text for kw in ("password", "log in", "login", "locked out")):
        category = "account_access"   # it looks like a login/password problem
        priority = "medium"           # login issues block the user, so medium
    else:
        category = "general_support"  # anything else falls back to general
        priority = "normal"

    # Decide the ticket type (how_to / incident / service_request / problem /
    # change_request) using the same combined text.
    ticket_type = classify_ticket_type(text)

    # Return the result as a dictionary so the next pipeline step can use it.
    return {
        "ticket_id": ticket_id,
        "category": category,
        "ticket_type": ticket_type,
        "priority": priority,
        "summary": subject,  # we reuse the subject line as the short summary
    }

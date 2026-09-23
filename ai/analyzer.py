async def analyze_ticket(ticket):
    if isinstance(ticket, dict):
        subject = ticket.get("subject", "")
        description = ticket.get("description", "")
        ticket_id = ticket.get("id", "Unknown")
    else:
        subject = getattr(ticket, "subject", "")
        description = getattr(ticket, "description", "")
        ticket_id = getattr(ticket, "id", "Unknown")

    text = f"{subject} {description}".lower()

    if any(kw in text for kw in ("password", "log in", "login", "locked out")):
        category = "account_access"
        priority = "medium"
    else:
        category = "general_support"
        priority = "normal"

    return {
        "ticket_id": ticket_id,
        "category": category,
        "priority": priority,
        "summary": subject,
    }

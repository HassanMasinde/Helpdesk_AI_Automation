def analyze_ticket(ticket):
    text = f"{ticket.subject} {ticket.description}".lower()

    if "password" in text or "log in" in text or "login" in text:
        category = "account_access"
        priority = "medium"
    else:
        category = "general_support"
        priority = "normal"

    return {
        "ticket_id": ticket.id,
        "category": category,
        "priority": priority,
        "summary": ticket.subject,
    }

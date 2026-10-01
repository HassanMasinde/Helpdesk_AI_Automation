import os
import logging
from playwright.async_api import Page

# Grab the raw env URL once
_RAW_URL = str(os.getenv("HELPDESK_URL", "https://loyonerp.hanmak.co.ke/HelpDesk/Tickets")).strip()

# Strip any trailing /HelpDesk/Tickets so we have a clean base
if "/HelpDesk" in _RAW_URL:
    BASE_URL = _RAW_URL.split("/HelpDesk")[0]
else:
    BASE_URL = _RAW_URL

# Always the correct absolute tickets URL
TICKETS_URL = f"{BASE_URL.rstrip('/')}/HelpDesk/Tickets"


async def navigate_to_tickets_queue(page: Page):
    """
    Navigates cleanly to the Loyon ERP helpdesk ticket grid.
    1. Tries clicking the on-screen 'Tickets' link (preserves session).
    2. Falls back to the correct absolute URL (no duplication).
    """
    logging.info("Navigating to active tickets queue...")
    print("🧭 Navigating to Support Tickets Queue...")

    try:
        ticket_link = page.get_by_role("link", name="Tickets")
        if await ticket_link.count() > 0:
            await ticket_link.first.click(timeout=8000)
            print("👆 Clicked 'Tickets' link on dashboard.")
        else:
            raise Exception("No 'Tickets' link found on dashboard")

    except Exception as e:
        print(f"⚠️ Sidebar locator failed ({e}). Routing to absolute URL...")
        print(f"   📌 Target: {TICKETS_URL}")
        await page.goto(TICKETS_URL, wait_until="domcontentloaded")

    await page.wait_for_load_state("networkidle")
    print("📋 Tickets queue page loaded successfully.")
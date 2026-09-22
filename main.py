import asyncio
import logging
import os
from playwright.async_api import async_playwright

# Imports from your project structure
from config import LOG_DIR, LOG_FILE, MOCK_MODE
from browser.login import login
from browser.tickets import get_tickets
from ai.knowledge import find_relevant_kb
from ai.analyzer import analyze_ticket
from ai.resolver import resolve_ticket

# Setup logging function
def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

async def main():
    print("🤖 Starting your Helpdesk AI Agent...")
    setup_logging()
    logging.info("Agent started.")

    async with async_playwright() as p:
        # Launch Chrome browser
        browser = await p.chromium.launch(
            headless=False,
            channel="chrome"
        )
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 1. Login to the helpdesk system
            print("🔑 Logging in...")
            await login(page)

            # 2. Fetch active helpdesk tickets
            print("📥 Fetching tickets...")
            tickets = await get_tickets(page)

            # 3. Process each ticket using AI
            for ticket in tickets:
                # Typecheck conversion to stop the dictionary attribute crash
                if isinstance(ticket, dict):
                    ticket_id = ticket.get('id', 'Unknown')
                    ticket_subj = ticket.get('subject', 'No Subject')
                else:
                    ticket_id = "Unknown"
                    ticket_subj = str(ticket)
                    # Convert raw string into a structured dictionary for the AI modules
                    ticket = {
                        "id": ticket_id, 
                        "subject": ticket_subj, 
                        "description": ticket_subj
                    }

                print(f"📄 Processing Ticket ID: {ticket_id}")
                
                # Analyze the problem
                analysis = await analyze_ticket(ticket)
                
                # Find matching knowledge base documentation
                kb_docs = await find_relevant_kb(analysis)
                
                # Generate a resolution or reply using Gemini 3.6 Flash
                resolution = await resolve_ticket(ticket, analysis, kb_docs)
                
                print(f"✅ Resolution generated: {resolution[:75]}...")
                
                # ⏱️ COOLDOWN PAUSE: Prevents Gemini Free Tier 503 errors during rapid loops
                print("⏳ Pausing for 5 seconds to respect free-tier API rate limits...")
                await asyncio.sleep(5)

        except Exception as e:
            logging.error(f"An error occurred during execution: {e}")
            print(f"❌ Error: {e}")

        finally:
            print("Shutting down browser...")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

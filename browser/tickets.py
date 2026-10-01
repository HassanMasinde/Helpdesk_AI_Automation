import logging


async def get_tickets(page):
    """
    Fetches active tickets from the Loyon ERP helpdesk ticket grid.

    The ticket list is rendered as a DataTables grid at the bottom of
    the /HelpDesk/Tickets page, below the create-ticket form.

    Columns (from left to right):
      No | Customer | Created On | Summary | Type | Assigned To | Priority | Status | Created By
    """
    logging.info("Scraping ticket matrix from DOM...")
    print("📥 Fetching tickets from Loyon queue...")

    # Give the DataTables grid time to render
    await page.wait_for_timeout(3000)

    # ---------- Diagnostic: what's on the page? ----------
    stats = await page.evaluate("""
        () => ({
            tables: document.querySelectorAll("table").length,
            rows: document.querySelectorAll("table tbody tr").length,
            empty_msg: document.querySelector("table tbody td.dataTables_empty") ? "yes" : "no",
        })
    """)
    print(f"   📊 Page scan: {stats}")

    tickets = []

    # ---------- Scrape the ticket table ----------
    try:
        # Wait briefly for the grid to appear
        await page.wait_for_selector("table tbody", timeout=8000)

        # Check if the table is empty
        empty_row = await page.query_selector("td.dataTables_empty")
        if empty_row:
            print("   ℹ️ Ticket grid is empty — 'No data available in table'.")
            print("   ℹ️ That means there are currently no open tickets.")
            return []

        # Otherwise, scrape all rows
        rows = await page.query_selector_all("table tbody tr")
        print(f"   ✅ Found {len(rows)} ticket row(s) in grid.")

        for row in rows:
            cells = await row.query_selector_all("td")
            if len(cells) < 5:
                continue

            # Extract each column by index
            # 0=No, 1=Customer, 2=Created On, 3=Summary, 4=Type, 5=Assigned To, 6=Priority, 7=Status, 8=Created By
            row_text = [ (await c.inner_text()).strip() for c in cells ]

            tickets.append({
                "id": row_text[0] if len(row_text) > 0 else "N/A",
                "customer": row_text[1] if len(row_text) > 1 else "",
                "created_on": row_text[2] if len(row_text) > 2 else "",
                "subject": row_text[3] if len(row_text) > 3 else "",
                "description": row_text[3] if len(row_text) > 3 else "",   # Summary doubles as description
                "type": row_text[4] if len(row_text) > 4 else "",
                "assigned_to": row_text[5] if len(row_text) > 5 else "",
                "priority": row_text[6] if len(row_text) > 6 else "",
                "status": row_text[7] if len(row_text) > 7 else "",
                "created_by": row_text[8] if len(row_text) > 8 else "",
            })

    except Exception as e:
        print(f"   ⚠️ Scraping failed: {e}")
        logging.warning(f"Ticket scraping failed: {e}")

    if tickets:
        print(f"📄 Retrieved {len(tickets)} tickets from live queue.")
    else:
        print("   ℹ️ No tickets to process at this time.")

    return tickets
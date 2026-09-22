import os
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

async def login(page):
    url = os.getenv("HELPDESK_URL", "https://support.hanmak.co.ke/")
    username = os.getenv("HELPDESK_USERNAME")
    password = os.getenv("HELPDESK_PASSWORD")

    logging.info(f"Navigating to login workspace: {url}")
    await page.goto(url)
    
    # Give the page animations a brief moment to settle down
    await page.wait_for_load_state("domcontentloaded")

    # 1. Fill the Facility Access Code box by matching its nearby screen label
    print("🔑 Inputting facility access keys...")
    # This searches the screen for any entry field near the text 'Code' or 'Access'
    await page.locator("input[id*='Code'], input[name*='Code'], input[placeholder*='Code']").first.fill("demo")

    # 2. Select the core target system from the Application menu dropdown
    print("📋 Selecting application variant...")
    # Selects the Medicentre option out of the standard selection container dropdown
    await page.select_option("select", label="MedicentreV3 iHMIS")

    # 3. Supply your profile dashboard login keys using explicit text matching
    print(f"👤 Filling credential mapping details for user: {username}")
    await page.locator("input[name*='User'], input[placeholder*='Username']").first.fill(username)
    await page.locator("input[name*='Pass'], input[placeholder*='Password']").first.fill(password)

    # 4. Trigger the authentication click workflow processing run
    print("🚀 Clicking login button...")
    await page.click("button[type='submit'], input[type='submit'], button:has-text('Login')")
    
    # Give the session dashboard deep buffer time to change state addresses
    await page.wait_for_load_state("networkidle")
    print("🔓 Workspace unlocked successfully! Logged into active session dashboard.")

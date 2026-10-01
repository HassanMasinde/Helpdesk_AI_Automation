import os
import logging
from dotenv import load_dotenv

load_dotenv(override=True)


async def login(page):
    """
    Logs into the Loyon ERP Helpdesk portal.

    Smart flow:
      - If already logged in (session cookie present) -> skip
      - If Client Code prompt is visible -> handle it
      - Otherwise, go straight to username/password
    """
    raw_url = str(os.getenv("HELPDESK_URL", "")).strip()
    username = os.getenv("HELPDESK_USERNAME", "").strip()
    password = os.getenv("HELPDESK_PASSWORD", "").strip()
    client_code = os.getenv("HELPDESK_CLIENT_CODE", "hanmak").strip()

    if not raw_url:
        raise ValueError("HELPDESK_URL not set in .env")

    if "/HelpDesk" in raw_url:
        base_login_url = raw_url.split("/HelpDesk")[0]
    else:
        base_login_url = raw_url

    print(f"🌍 Navigating to: {base_login_url}")
    logging.info(f"Navigating to Loyon portal: {base_login_url}")

    await page.goto(base_login_url, wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)

    # ---------- Check for existing session ----------
    current_url = page.url
    if "/HelpDesk" in current_url or "/Home" in current_url:
        print("🔓 Already logged in — session cookie detected.")
        return

    # ---------- Check if username field is ALREADY visible ----------
    # (means Client Code was already passed in this session)
    user_field = page.locator("#userName, input[name='Username']").first
    user_visible = await user_field.is_visible()

    if user_visible:
        print("🔑 Client Code gate already passed — going straight to credentials.")
    else:
        print("🔑 Client Code gate detected — need to enter code.")

        # ---------- STEP 1: Enter Client Code via JavaScript ----------
        print(f"   📝 Injecting Client Code '{client_code}' via JS events...")

        injected = await page.evaluate(f"""
            () => {{
                // The real Client Code input is #hospCode (visible after interaction)
                const real = document.getElementById('hospCode');
                const hidden = document.getElementById('HospitalCode');
                const val = "{client_code}";

                if (real) {{
                    real.value = val;
                    real.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    real.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
                if (hidden) {{
                    hidden.value = val;
                    hidden.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
                return {{ real: !!real, hidden: !!hidden }};
            }}
        """)
        print(f"   ✅ Injected into fields: {injected}")

        await page.wait_for_timeout(500)

        # ---------- Click Proceed ----------
        print("🔎 Clicking Proceed button...")
        clicked = await page.evaluate("""
            () => {
                // Try role-based button first, then any button with 'Proceed'
                const btns = [...document.querySelectorAll('button, input[type=button], input[type=submit]')];
                const proceed = btns.find(b =>
                    (b.innerText || b.value || '').toLowerCase().includes('proceed')
                );
                if (proceed) { proceed.click(); return true; }
                return false;
            }
        """)

        if not clicked:
            raise Exception("No 'Proceed' button found.")

        print("🚀 Clicked Proceed. Waiting for credentials form...")
        await page.wait_for_timeout(3000)

    # ---------- STEP 2: Fill Username + Password ----------
    print(f"👤 Filling credentials for {username}...")

    await user_field.wait_for(state="visible", timeout=15000)
    await user_field.click(force=True)
    await user_field.fill("")
    await user_field.type(username, delay=60)
    print("   ✅ Username filled.")

    pass_field = page.locator("#userPassword, input[name='Password']").first
    await pass_field.click(force=True)
    await pass_field.fill("")
    await pass_field.type(password, delay=60)
    print("   ✅ Password filled.")

    # ---------- STEP 3: Submit ----------
    print("🚀 Clicking Login button...")
    await page.evaluate("""
        () => {
            const btn = document.getElementById('btnLogin')
                     || document.querySelector("button[type='submit']");
            if (btn) btn.click();
        }
    """)

    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)

    current_url = page.url
    print(f"   Current URL after login: {current_url}")

    if "/Security/Login" in current_url or "ReturnUrl" in current_url:
        print("   ⚠️ Login failed — still on login page.")
    else:
        print("   ✅ Login succeeded.")
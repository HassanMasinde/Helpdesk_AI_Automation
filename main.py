import asyncio
from playwright.async_api import async_playwright

async def main():
    print("🤖 Starting your Helpdesk AI Agent...")
    
    async with async_playwright() as p:
        # This line uses your built-in Chrome to bypass the download block!
        browser = await p.chromium.launch(
            headless=False, 
            channel="chrome"
        )
        
        page = await browser.new_page()
        
        # Test line to make sure it opens a window successfully
        await page.goto("https://google.com")
        print("✅ Browser successfully opened Google using your local Chrome!")
        
        # Keeps the browser open for 10 seconds so you can see it work
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

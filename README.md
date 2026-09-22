# Helpdesk AI Automation Agent 🤖

An automated asynchronous workflow agent engineered to optimize healthcare and corporate IT support workflows for **MedicentreV3 iHMIS** and **Loyon ERP** platforms. 

The system leverages **Playwright** browser automation to dynamically interact with live web portal infrastructure, bypass initial access portals, authenticate client-success users, and scrape open tracking tickets automatically.

---

## 🛠️ System Architecture (Core Components)

The repository focuses entirely on the entry orchestration and visual runtime environment:

### 1. `main.py` (The Central Orchestrator)
* **Asynchronous Loop Management:** Built completely on top of Python's `asyncio` engine to safely process long-running automated tasks without freezing systemic operations.
* **Playwright Context Control:** Spawns a structured Chromium browser instance using a dedicated execution block (`async with async_playwright()`).
* **Robust Typecheck Guardrails:** Features data validation loops that catch incoming dictionary structures or raw text arrays dynamically, converting unstructured queue logs into clean JSON data schemas.
* **Rate-Limit Preservation:** Enforces systemic cooldown delays (`asyncio.sleep`) to respect downstream service throttling and avoid workflow interruption.

### 2. `browser/` Infrastructure (Automated Actions)
* **`login.py`:** Automates interactions with the complex multi-step login form. It dynamically populates the initial facility access code prompt, selects target enterprise software systems (e.g., *MedicentreV3 iHMIS*), applies encrypted profile credentials, and waits until network states settle (`networkidle`) before changing workspaces.
* **`tickets.py`:** Directly fetches active support tracking numbers, subjects, and issue data fields out of the live web table elements.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your workstation.

### 2. Installation & Setup
Clone the repository and install the standard browser automation dependencies inside a virtual environment (`venv`):

```bash
# Clone the repository
git clone https://github.com
cd Helpdesk_AI_Automation

# Install Playwright web automation tools
pip install playwright

# Download and install required browser binaries (Chromium)
playwright install chromium
```

### 3. Execution Options (Headless vs. Headed Mode)
By default, the script launches a visible browser on your laptop (`headless=False`) so you can supervise mouse movements and credential entry steps in real-time.

To run the agent completely hidden in your machine's background memory to save RAM, adjust your launch setup inside `main.py`:

```python
# Edit this flag inside your main.py file:
browser = await p.chromium.launch(
    headless=True,       # Hides the browser window completely
    channel="chrome"     # Forces it to utilize your desktop Chrome binary
)
```

To kick off the processing queue pipeline, run:
```bash
python main.py
```

---

## 🔒 Security Compliance Note
This repository adheres to strict data privacy and application security standards. Private authentication keys, administrative helpdesk credentials, and target server addresses are completely isolated out of the codebase files. They are managed strictly via local environment variables (`.env`) which are permanently omitted from public version tracking.


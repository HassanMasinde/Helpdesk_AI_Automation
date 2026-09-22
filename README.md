# Helpdesk AI Automation — `Simba` Branch Workload

This branch (`Simba`) contains the automated browser integration and knowledge base workload for the **Hanmak Support Portal / MedicentreV3 iHMIS** helpdesk agent.

---

## 🛠️ Key Features on this Branch

* **Automated Login Engine (`browser/login.py`)**: 
  * Direct DOM event manipulation to handle form dynamic re-renders.
  * Reliable populating of Client Access Code, Branch, Username, and Password fields without focus loss or input wipes.
* **Environment Configuration**:
  * Safe environment variable loading via `python-dotenv`.
  * Multi-account handling using `PORTAL_USERNAME` to prevent conflicts with Windows system environment variables.
* **Knowledge & Workload Module (`knowledge/`)**:
  * Structured knowledge base and workspace workload configuration for processing helpdesk requests.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ installed along with Playwright and browsers:

```bash
pip install -r requirements.txt
playwright install chromium

import os
from dotenv import load_dotenv

# This command actually reads your .env file into Python
load_dotenv()

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the missing variables
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "agent.log")
MOCK_MODE = True  # Set to False when you want to use real AI instead of mock data

# Helpdesk Login Credentials (Change these to your actual login details)
# Pull safely from the hidden .env file
HELPDESK_URL = os.getenv("HELPDESK_URL")
HELPDESK_USERNAME = os.getenv("HELPDESK_USERNAME")
HELPDESK_PASSWORD = os.getenv("HELPDESK_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

BROWSER_CHANNEL = "chrome"
HEADLESS = False
BROWSER_HOLD_SECONDS = 10
START_URL = HELPDESK_URL  # Maps the start page to the secure URL you already set up

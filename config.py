import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the missing variables
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "agent.log")
MOCK_MODE = True  # Set to False when you want to use real AI instead of mock data

# Helpdesk Login Credentials (Change these to your actual login details)
HELPDESK_URL = "https://support.hanmak.co.ke/"
HELPDESK_USERNAME = "Nicanel"
HELPDESK_PASSWORD = "Nicanelobita@123!"
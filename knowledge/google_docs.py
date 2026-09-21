import logging

def get_knowledge_base():
    """
    Mock function to simulate fetching knowledge base articles from Google Docs.
    """
    logging.info("Fetching knowledge base from Google Docs...")
    print("📋 Syncing with Google Docs Knowledge Base...")
    
    # Return placeholder documentation data
    return [
        {"category": "Password Reset", "steps": "Go to settings, click reset password, follow email instructions."},
        {"category": "VPN Connection", "steps": "Ensure internet is active, open Cisco AnyConnect, click Connect."}
    ]

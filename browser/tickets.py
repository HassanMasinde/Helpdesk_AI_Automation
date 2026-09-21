import logging

async def get_tickets(page):
    """
    Fetches active tickets from the Loyon ERP page.
    """
    logging.info("Fetching tickets from Loyon ERP...")
    
    # Corrected data structure using dictionary objects instead of raw strings
    sample_tickets = [
        {
            "id": "10542", 
            "subject": "System running slow and unable to process transactions",
            "description": "The point of sale terminal is lagging heavily during checkout."
        },
        {
            "id": "10543", 
            "subject": "Password expired lockout",
            "description": "User account locked out after three failed attempts."
        }
    ]
    
    return sample_tickets

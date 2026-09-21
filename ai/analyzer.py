import os
from google import genai
from dotenv import load_dotenv

load_dotenv(override=True)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def analyze_ticket(ticket):
    # CHANGE THESE LINES FROM ticket.subject TO .get()
    ticket_subject = ticket.get('subject', 'No Subject')
    ticket_desc = ticket.get('description', 'No Description')
    
    prompt = f"""
    Analyze the following IT support issue from a Hanmak client.
    Subject: {ticket_subject}
    Description: {ticket_desc}
    
    Identify the core system component affected (e.g., eTIMS, M-PESA, Printer, Authentication).
    """
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
    )
    return response.text

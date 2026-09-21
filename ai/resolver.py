import os
from google import genai
from dotenv import load_dotenv

load_dotenv(override=True)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Update this definition line to take exactly the 3 arguments main.py sends!
async def resolve_ticket(ticket, analysis, kb_docs):
    
    # Safely extract values out of the ticket dictionary
    ticket_subject = ticket.get('subject', 'No Subject')
    ticket_desc = ticket.get('description', 'No Description')

    prompt = f"""
    You are an IT Support Agent at Hanmak Technologies.
    
    Client Ticket Details:
    - Subject: {ticket_subject}
    - Details: {ticket_desc}
    
    AI Assessment Matrix:
    {analysis}
    
    Troubleshooting Guidelines (Knowledge Base):
    {kb_docs}
    
    Draft a polite, professional, semi-automated response to the client.
    """
    
    # Run the live production-ready Gemini 3.6 Flash engine
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
    )
    return response.text

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Initialize Gemini client using API key from .env
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

def generate_response(ticket_subject: str, ticket_body: str, kb_context: str = "") -> str:
    """Generates a Customer Success response for a Helpdesk ticket using Gemini."""
    if not client:
        return "Human Escalation Required: GEMINI_API_KEY is not configured."

    system_instruction = (
        "You are Rukia, a polite and professional Customer Success Specialist. "
        "Provide clear, step-by-step guidance to help resolve the user's issue."
    )

    prompt = f"""
    Ticket Subject: {ticket_subject}
    Ticket Description: {ticket_body}
    Knowledge Base Context: {kb_context}
    
    Please draft a clear, helpful response to the client.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"system_instruction": system_instruction}
    )

    return response.text
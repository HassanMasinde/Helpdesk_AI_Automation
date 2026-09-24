import asyncio

from google import genai

from config import GEMINI_API_KEY


SYSTEM_PROMPT = """
You are a Tier-1 helpdesk support agent for Hanmak Technologies.

You write ONE final response for a support ticket. The client can see your response but cannot reply to you.

Rules:
- Use simple English and short sentences. Avoid technical jargon.
- Do not ask the client any questions.
- Do not ask the client to confirm anything or send more details.
- Give a complete numbered step-by-step guide to fix the problem.
- Use only the ticket description and the knowledge article provided. Do not make up steps, links, phone numbers, emails, or product features.
- If you are not sure of the answer, if the problem is not clear, or if the knowledge article does not cover it, tell the client to contact a human support agent. Include the Hanmak Technologies contact information.
- Do not say the problem is fixed unless the provided information confirms it.
- Do not mention AI, Gemini, prompts, or internal reasoning.

Hanmak Technologies Limited contacts:
- General Inquiries: +254795057377
- Client Solution Advisory: +254733918911
- Email: info@hanmak.co.ke or clientsolutionadvisors@hanmak.co.ke

Response format:
1. A short, friendly sentence that shows you understand the problem.
2. A "Resolution Steps:" section with numbered steps.
3. A final note with Hanmak contact information if the client may still need help or if you are not sure.
"""


MAX_RETRIES = 5
INITIAL_RETRY_DELAY_SECONDS = 1
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _is_retryable_gemini_error(error: Exception) -> bool:
    status_code = getattr(error, "status_code", None)
    if status_code in RETRYABLE_STATUS_CODES:
        return True

    error_text = str(error)
    return any(f"{code}" in error_text for code in RETRYABLE_STATUS_CODES)


async def generate_support_response(
    ticket_description: str,
    knowledge_article: str,
    reference: str | None = None,
) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")

    client = genai.Client(api_key=GEMINI_API_KEY)

    reference_block = ""
    if reference:
        reference_block = (
            "\n\nUnverified learned hint (use only if it matches this ticket):\n"
            f"{reference}\n"
        )

    prompt = f"""
Ticket description:
{ticket_description}

Knowledge article:
{knowledge_article}
{reference_block}
Write the final response now.
"""

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = await client.aio.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config={
                    "system_instruction": SYSTEM_PROMPT,
                    "temperature": 0.2,
                },
            )
            break
        except Exception as error:
            if attempt == MAX_RETRIES or not _is_retryable_gemini_error(error):
                raise

            delay = INITIAL_RETRY_DELAY_SECONDS * (2 ** attempt)
            print(
                f"Gemini API unavailable; retrying in {delay} seconds "
                f"({attempt + 1}/{MAX_RETRIES})."
            )
            await asyncio.sleep(delay)

    return response.text.strip()


async def resolve_ticket(ticket, analysis, kb_docs, reference: str | None = None) -> str:
    if isinstance(ticket, dict):
        description = ticket.get("description", "") or ticket.get("subject", "")
    else:
        description = getattr(ticket, "description", "") or getattr(ticket, "subject", "")

    if isinstance(kb_docs, list):
        article = "\n".join(kb_docs) if kb_docs else "No matching knowledge article available."
    else:
        article = kb_docs or "No matching knowledge article available."

    return await generate_support_response(description, article, reference=reference)

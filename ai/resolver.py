import asyncio

from google import genai

from config import GEMINI_API_KEY


SYSTEM_PROMPT = """
You are a professional Tier-1 helpdesk support agent for MedicentreV3, a hospital system supported by Hanmak Technologies.

Your job is to draft clear, polite, and accurate support replies to hospital staff.

Rules:
- Use only the ticket description and knowledge article provided.
- Do not invent product features, URLs, credentials, policies, or troubleshooting steps.
- If the knowledge article does not directly address the ticket, say that the issue needs further review and recommend escalation.
- Do not provide generic troubleshooting steps unless they are explicitly included in the knowledge article.
- Do not say the issue has been fixed unless the provided information confirms that.
- Keep the response professional, concise, and suitable for sending directly to the user.
- Do not mention AI, Gemini, prompts, or internal reasoning.
- Do not include private internal notes.
"""


MOCK_CASES = [
    {
        "name": "Login invalid credentials",
        "ticket_description": """
A hospital receptionist reports that they cannot log into MedicentreV3.
They say their username is accepted, but after entering the password they get
an 'Invalid credentials' message.
""",
        "knowledge_article": """
For MedicentreV3 login issues, first confirm the user's registered email address
and username. Ask whether they recently changed their password. If needed, guide
the user to reset their password using the MedicentreV3 password reset workflow.
If the user is locked out after repeated failed attempts, escalate the ticket to Tier-2.
""",
    },
    {
        "name": "Unsupported outpatient billing crash",
        "ticket_description": """
The outpatient billing module is crashing when I try to cancel a receipt.
This started this morning after I posted a payment to the wrong patient account.
I need to reverse it before end-of-day billing reconciliation.
""",
        "knowledge_article": """
No matching MedicentreV3 knowledge article is available for outpatient billing
receipt cancellation crashes.
""",
    },
    {
        "name": "Printer mapping issue",
        "ticket_description": """
The pharmacy team can print reports from MedicentreV3, but prescription labels
are going to the ward printer instead of the pharmacy label printer.
""",
        "knowledge_article": """
For printer routing issues, collect the user's department, workstation name,
expected printer name, and the printer where the document actually printed.
Do not change printer mappings from Tier-1. Escalate to Tier-2 after collecting
those details.
""",
    },
]


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
) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
Ticket description:
{ticket_description}

Knowledge article:
{knowledge_article}

Draft the support response now.
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


async def main() -> None:
    for case in MOCK_CASES:
        print(f"\n--- {case['name']} ---")
        reply = await generate_support_response(
            case["ticket_description"],
            case["knowledge_article"],
        )
        print(reply)


if __name__ == "__main__":
    asyncio.run(main())

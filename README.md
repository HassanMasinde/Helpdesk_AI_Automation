# Hanmak Support AI Agent

Autonomous Tier-1 helpdesk agent for the MedicentreV3 hospital system at Hanmak Technologies.

The project is being built in Python with `asyncio`. The current focus is the AI resolver module, which drafts professional support replies from ticket descriptions and knowledge base articles.

## Team Roles

- Browser Lead: owns Playwright navigation, ticket extraction, and reply submission through the MedicentreV3 support portal.
- Knowledge Lead: owns Google Docs scraping and extraction of troubleshooting articles.
- AI & Logic Lead: owns Gemini API integration, prompt design, ticket-to-knowledge reasoning, and response drafting.

## Directory Structure

```text
browser/      Playwright browser automation and ticket scraping
knowledge/    Google Docs knowledge extraction
ai/           AI analysis, knowledge matching, and Gemini response drafting
config.py     Central configuration and environment loading
.env          Local secrets and credentials, ignored by git
logs/         Runtime logs, ignored by git
```

## Current AI Resolver Status

The initial AI resolver has been implemented in `ai/resolver.py`.

It currently supports:

- Fully asynchronous Gemini API calls using the official `google-genai` SDK.
- Secure API key loading from `.env` through `config.py`.
- A strict system prompt for professional MedicentreV3 Tier-1 helpdesk replies.
- Mock ticket and knowledge article test cases while Browser and Knowledge modules are still in development.
- Exponential backoff retry handling for temporary Gemini API failures.
- Prompt stress tests to confirm the model does not invent troubleshooting steps when the knowledge base is insufficient.

## Environment Variables

Create a local `.env` file in the project root. This file is ignored by git.

Required for the AI resolver:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Existing browser/helpdesk settings are also loaded from `.env`:

```env
HELPDESK_URL=your_helpdesk_url_here
HELPDESK_USERNAME=your_username_here
HELPDESK_PASSWORD=your_password_here
```

`config.py` loads these values with `python-dotenv` and exposes:

- `HELPDESK_URL`
- `HELPDESK_USERNAME`
- `HELPDESK_PASSWORD`
- `GEMINI_API_KEY`

## Dependencies

The project dependencies are listed in `requirements.txt`.

Current dependencies:

```txt
playwright
python-dotenv
openai
requests
google-genai
```

Install them with:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Gemini Resolver

The main async function is:

```python
async def generate_support_response(
    ticket_description: str,
    knowledge_article: str,
) -> str:
```

It accepts:

- `ticket_description`: the user's helpdesk ticket text.
- `knowledge_article`: the relevant troubleshooting article or knowledge base content.

It returns:

- A concise, professional support reply suitable for a Tier-1 MedicentreV3 helpdesk response.

The resolver currently uses:

```python
model="gemini-3.6-flash"
```

This model was selected because the Gemini API reported that `gemini-2.5-flash` is no longer available to new users.

## System Prompt Rules

The resolver's system prompt instructs Gemini to act as a professional MedicentreV3 Tier-1 support agent.

Important guardrails:

- Use only the ticket description and knowledge article provided.
- Do not invent product features, URLs, credentials, policies, or troubleshooting steps.
- If the knowledge article does not directly address the ticket, say the issue needs further review and recommend escalation.
- Do not provide generic troubleshooting steps unless they are explicitly included in the knowledge article.
- Do not say the issue has been fixed unless the provided information confirms that.
- Keep the reply professional, concise, and suitable for sending directly to hospital staff.
- Do not mention AI, Gemini, prompts, or internal reasoning.
- Do not include private internal notes.

## Retry Handling

The Gemini call includes an async exponential backoff retry loop so temporary server spikes do not immediately crash the background agent.

Retry settings:

```python
MAX_RETRIES = 5
INITIAL_RETRY_DELAY_SECONDS = 1
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
```

Backoff schedule:

```text
1 second
2 seconds
4 seconds
8 seconds
16 seconds
```

The resolver retries transient API pressure/server errors such as `503 UNAVAILABLE` and `429 TOO MANY REQUESTS`.

It does not retry non-transient failures such as missing API keys, invalid credentials, invalid model names, or other configuration errors.

## Mock Stress Tests

Because the Browser and Knowledge modules are still in development, `ai/resolver.py` currently includes mock cases.

Current mock cases:

- Login invalid credentials with a matching login KB article.
- Unsupported outpatient billing receipt cancellation crash with no matching KB steps.
- Printer mapping issue with a constrained printer-routing KB article.

The unsupported billing crash case is intentionally designed to test hallucination resistance:

```text
The outpatient billing module is crashing when I try to cancel a receipt.
```

The expected behavior is that Gemini should not invent fake troubleshooting steps such as clearing cache, checking database tables, restarting services, changing permissions, or using unsupported receipt-reversal workflows.

Instead, it should acknowledge the issue and recommend escalation because the provided knowledge article says no matching article is available.

## Running The AI Resolver

Run the resolver directly with:

```powershell
.\.venv\Scripts\python.exe -m ai.resolver
```

Expected behavior:

- Loads `GEMINI_API_KEY` from `.env`.
- Runs each mock case through Gemini asynchronously.
- Prints each drafted response to the terminal.
- Retries transient Gemini API failures with exponential backoff.
- Raises a clear error if `GEMINI_API_KEY` is missing.

## Validation Commands Used

Dependency installation:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Syntax validation:

```powershell
.\.venv\Scripts\python.exe -m py_compile config.py ai\resolver.py
```

Resolver runtime validation:

```powershell
.\.venv\Scripts\python.exe -m ai.resolver
```

## Known SDK Warning

The Gemini SDK may print this warning:

```text
Direct use of automatic function calling (AFC) in AsyncModels.generate_content is not recommended...
```

The current resolver does not use tools or automatic function calling, and the async generation call works successfully. If needed later, the resolver can be migrated to the newer async chat or Interactions API style recommended by the SDK.

## Next Integration Step

Once Browser and Knowledge modules are ready, replace the mock cases in `ai/resolver.py` with live inputs:

- Ticket descriptions from `browser/`.
- Matched knowledge articles from `knowledge/` or `ai/knowledge.py`.
- Drafted responses returned by `generate_support_response()` for browser submission.

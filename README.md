# Hanmak Support AI Agent — AI Component

The AI brain that turns a helpdesk ticket into a ready-to-save resolution.

Given a ticket's problem description, the AI:

1. **Analyzes** it to work out its category and priority.
2. **Matches** it to the most relevant knowledge article.
3. **Drafts** a clean, professional resolution using Google Gemini.

It is written in Python with `asyncio` and Google's `google-genai` SDK, using the model **`gemini-3.6-flash`** at temperature `0.2`.

## The Problem

When staff raise support tickets, a human agent has to read each one, recall the right fix, and write a reply. That is slow, repetitive, and inconsistent.

## The Solution

The AI automates the routine part of support. For every ticket it produces a complete, polite, ready-to-save answer in seconds.

## How It Works

The pipeline is three steps, each in its own module:

1. `ai/analyzer.py` — reads the ticket and classifies it.
2. `ai/knowledge.py` — selects the matching support instructions.
3. `ai/resolver.py` — asks Gemini to write the final resolution.

A fourth module, `ai/learning.py`, remembers resolved tickets so the agent learns as it works (see [Learning](#learning)).

```python
analysis = await analyze_ticket(ticket)        # step 1
kb_docs   = await find_relevant_kb(analysis)   # step 2
resolution = await resolve_ticket(ticket, analysis, kb_docs)  # step 3
```

There is also a one-call helper that runs the whole pipeline:

```python
resolution = await solve_ticket(ticket)
```

## Functions

### `ai/analyzer.py`

- `analyze_ticket(ticket)` — async. Accepts a ticket as a `dict` (or object) with `subject` and `description`, and returns a classification:

```python
{
    "ticket_id": "...",
    "category": "account_access",   # or "general_support"
    "priority": "medium",           # or "normal"
    "summary": "...",
}
```

It currently recognizes login/password issues as `account_access`; everything else falls back to `general_support`.

### `ai/knowledge.py`

- `find_article(category)` — looks up a support article for a category.
- `find_relevant_kb(analysis)` — async. Takes the analyzer output and returns a list of knowledge articles for the category.

It also keeps a small set of local fallback articles (account access, network, printer, billing).

### `ai/resolver.py`

- `generate_support_response(ticket_description, knowledge_article, reference=None)` — async. Calls Gemini and returns the drafted response. `reference` is an optional unverified learned hint passed in as background context.
- `resolve_ticket(ticket, analysis, kb_docs, reference=None)` — async. Combines the ticket description and knowledge, then delegates to `generate_support_response`.

### `ai/learning.py`

- `find_learned_match(problem, verified=None)` — returns the best learned entry for a problem using pure keyword-overlap scoring, or `None` when below the threshold.
- `add_learned(problem, resolution, ticket_id, kind="solution", verified=False)` — records a learned entry after a ticket is resolved.
- `mark_verified(ticket_id)` — promotes an entry to verified so it can be auto-applied in future runs.
- `load_learned()` / `save_learned()` — read/write the local JSON store.

### `ai/__init__.py`

- `solve_ticket(ticket)` — async. Runs the full pipeline in one call and returns the resolution string.

## The Rules It Follows

The Gemini call is constrained by a strict system prompt. The AI must:

- Use **simple English** and short sentences — no jargon.
- Write **one final response** — it must **never ask the client questions** (the client cannot reply to the ticket).
- Give a **numbered step-by-step** resolution guide.
- Use **only** the ticket description and the knowledge article provided — never invent steps, links, phone numbers, emails, or product features.
- If it is unsure, the problem is unclear, or the knowledge does not cover it, **escalate to a human agent** and include Hanmak contact details.
- Never claim an issue is fixed unless the provided information confirms it.
- Never mention AI, Gemini, prompts, or internal reasoning.

### Guardrails

- Uses only the ticket and knowledge article provided.
- Never invents product features, URLs, credentials, or troubleshooting steps.
- Recommends escalation when the knowledge does not address the ticket.

### Fault Tolerance

The Gemini call retries on transient errors with exponential backoff:

- `MAX_RETRIES = 5`
- Retries on status codes `429, 500, 502, 503, 504`
- Starts at `1` second and doubles each attempt.

## Model & Configuration

- Model: `gemini-3.6-flash`
- Temperature: `0.2`
- API key is read from the `GEMINI_API_KEY` environment variable (`.env`).

## Knowledge Source

Live knowledge comes from the shared Hanmak support knowledge base (a public Google Sheet) through the knowledge module. `ai/knowledge.py` also carries a small set of local fallback articles.

## Learning

The agent learns as it resolves tickets. Every resolution is recorded in `ai/learning.py` against the problem's keywords, so a similar future ticket can be handled without another Gemini call.

### Resolution Precedence

For each ticket, the agent applies the first rule that matches, in order:

1. **Curated knowledge base** — a Google Sheet match is passed to Gemini for a fresh response.
2. **Verified learned entry** — a previously human-approved answer, reused directly.
3. **Unverified learned entry** — an escalation rule is reused directly; a solution entry is passed to Gemini as a background hint (never auto-posted).
4. **Gemini** — a fresh generated response.
5. **Escalation fallback** — a standard Hanmak escalation message with contact details.

Human-vetted knowledge always wins, unverified AI output is only used as context, and everything degrades gracefully to a human escalation.

### Learning Store

Learned entries live in a local JSON store (`data/learned_knowledge.json`), not in git. Each entry records:

- `keywords` — the problem keywords used for matching.
- `resolution` — the answer that was saved.
- `kind` — `"solution"` or `"escalation"`.
- `verified` — `true` once a human approves it for auto-apply.
- `source_ticket` — the ticket the answer came from.

## How It Runs

Integration contract — the browser automation hands the AI a ticket and receives the resolution back:

```python
resolution = await solve_ticket(ticket)
```

## How It Plugs Into The Full Flow

```text
login -> fetch ticket -> AI drafts resolution -> save
```

The browser automation logs in and pulls a ticket, passes the problem to the AI, and writes the AI's resolution back into the ticket.

## Project Structure

```text
ai/
  analyzer.py    ticket classification
  knowledge.py   knowledge article matching
  resolver.py    Gemini response drafting
  learning.py    learned-resolution store
```

## Getting Started

Requires Python 3.10+ and Google Chrome. Commands below are for Windows PowerShell.

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Add your Gemini API key — create a `.env` file in the project root:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. Try it — generate a resolution for one ticket:

   ```python
   import asyncio
   from ai import solve_ticket

   ticket = {"id": "1", "subject": "Login issue", "description": "Cannot log in."}
   print(asyncio.run(solve_ticket(ticket)))
   ```

The browser automation uses the same `solve_ticket` (or `generate_support_response`) to draft resolutions for live tickets.

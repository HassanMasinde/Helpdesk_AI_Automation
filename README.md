# Hanmak Support AI Agent

An autonomous AI responder for the MedicentreV3 Tier-1 helpdesk at Hanmak Technologies.

## The Problem

MedicentreV3 is a hospital system used daily by clinical and administrative staff. When something goes wrong, staff raise support tickets and wait for a human agent to reply.

That process had real costs:

- **Slow responses** — staff waited on a human to read and answer each ticket.
- **Repetitive work** — many tickets were recurring issues (login problems, printer routing, and similar) that followed the same resolution steps.
- **Inconsistent replies** — quality and tone varied from one agent to another.

Tier-1 support was spending its time on routine tickets instead of the complex cases that actually need a human.

## The Solution

The Support AI Agent automates the routine part of Tier-1 support. When a ticket arrives, the AI:

1. **Analyzes** the ticket to determine its category and priority.
2. **Matches** it to the most relevant knowledge article.
3. **Drafts** a professional, accurate support reply using Google Gemini.

The result is a polished, ready-to-send reply — produced in seconds, every time.

## Value Automation Brings to Hanmak

- **Faster responses** — tickets are answered in seconds instead of hours.
- **24/7 availability** — the agent never sleeps, so staff get replies at any hour.
- **Consistent quality** — every reply follows the same professional standard.
- **Freed-up staff** — Tier-1 agents focus on complex cases, not routine tickets.
- **Scalable support** — higher ticket volume no longer requires hiring more agents.

## How It Works

The AI component is built with Python's `asyncio` and Google Gemini:

- **`ai/analyzer.py`** — classifies each ticket into a category and assigns a priority.
- **`ai/knowledge.py`** — matches the ticket to the most relevant knowledge article.
- **`ai/resolver.py`** — drafts the professional reply through the Gemini API.

Development followed a mock-first approach: the AI was tested against realistic sample tickets before any live integration.

### Guardrails

The reply generator is constrained by a strict system prompt so it:

- Uses only the ticket and knowledge article provided.
- Never invents product features, URLs, credentials, or troubleshooting steps.
- Recommends escalation when the knowledge article does not address the ticket.
- Never claims an issue is fixed unless the provided information confirms it.
- Keeps replies professional, concise, and free of any mention of AI or internal reasoning.

The Gemini call also includes retry handling with exponential backoff for transient API errors, so temporary server pressure does not crash the agent.

## Project Structure

```text
ai/
  analyzer.py    ticket classification
  knowledge.py   knowledge article matching
  resolver.py    Gemini response drafting
config.py        configuration and environment loading
```

## Getting Started

1. Install dependencies:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root with your Gemini API key:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. Run the AI resolver:

   ```powershell
   .\.venv\Scripts\python.exe -m ai.resolver
   ```

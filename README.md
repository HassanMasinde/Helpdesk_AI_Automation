# Hanmak Support AI Agent

The AI component is built with Python's `asyncio` and Google Gemini:

- **`ai/analyzer.py`** — classifies each ticket into a category and assigns a priority.
- **`ai/knowledge.py`** — matches the ticket to the most relevant knowledge article.
- **`ai/resolver.py`** — drafts the professional reply through the Gemini API.

Development followed a mock-first approach: the AI was tested against realistic sample tickets before any live integration....For the live integration, we will need real time infomation from \browser and \knowledge

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

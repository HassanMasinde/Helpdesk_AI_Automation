"""
ai/__init__.py

WHAT THIS FILE IS
-----------------
This file turns the folder `ai/` into a Python "package" (an importable group of
modules). It is the front door of the AI component.

WHY IT MATTERS
--------------
Other code imports from the package like this:

    from ai import solve_ticket

`solve_ticket` below is the one-call entry point that runs the whole AI pipeline:
classify the ticket -> find knowledge -> ask Gemini for a resolution.

WHO IMPORTS THIS
----------------
- `main.py` (the browser flow) imports the three step functions directly.
- Any developer who only needs the full pipeline imports `solve_ticket`.
"""

# --- Imports: bring the step functions in from the other files in this package ---
# The leading dot (.) means "look inside the current package (the ai/ folder)".
# These lines only make the names available; they do NOT run the functions yet.
from .analyzer import analyze_ticket                    # step 1: classify the ticket
from .knowledge import find_article, find_relevant_kb   # step 2: pick knowledge articles
from .resolver import resolve_ticket                    # step 3: write the answer with Gemini


# `__all__` lists the public names of this package.
# It tells Python (and tools like editors) what `from ai import *` should expose.
# It is a convention that documents the intended public API, not a hard lock.
__all__ = ["analyze_ticket", "find_article", "find_relevant_kb", "resolve_ticket", "solve_ticket"]


async def solve_ticket(ticket) -> str:
    """
    Run the full AI pipeline for one ticket and return the resolution text.

    Parameters
    ----------
    ticket : dict
        A ticket with at least `subject` and `description`.

    Returns
    -------
    str
        The final resolution text produced by Gemini.

    Notes
    -----
    - `async` makes this a "coroutine function": it can pause while waiting for
      slow work (like a network call) without freezing the rest of the program.
    - `-> str` is a type hint meaning "this function returns a string".
    """
    # Step 1: read the ticket and decide its category (e.g. "account_access").
    # `await` pauses here until the async function finishes, then gives us its result.
    analysis = await analyze_ticket(ticket)

    # Step 2: use that category to fetch the matching knowledge articles.
    kb_docs = await find_relevant_kb(analysis)

    # Step 3: pass the ticket plus the articles to the resolver, which asks Gemini
    # to draft the final response. We return whatever it gives back.
    return await resolve_ticket(ticket, analysis, kb_docs)

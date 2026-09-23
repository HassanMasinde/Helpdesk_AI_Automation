from .analyzer import analyze_ticket
from .knowledge import find_article, find_relevant_kb
from .resolver import resolve_ticket


__all__ = ["analyze_ticket", "find_article", "find_relevant_kb", "resolve_ticket", "solve_ticket"]


async def solve_ticket(ticket) -> str:
    analysis = await analyze_ticket(ticket)
    kb_docs = await find_relevant_kb(analysis)
    return await resolve_ticket(ticket, analysis, kb_docs)

"""Custom tools for the knowledge assistant agent."""

try:
    from rag.retriever import search_knowledge
except ModuleNotFoundError:
    from src.rag.retriever import search_knowledge


def search_company_knowledge(query: str) -> dict:
    """Search the company knowledge base for relevant information.

    Use this tool when the user asks about company policies, procedures,
    or any internal knowledge. Always search before answering policy questions.

    Args:
        query: The search query describing what information to find.

    Returns:
        A dictionary with search results containing relevant text chunks and sources.
    """
    results = search_knowledge(query)

    if not results:
        return {"status": "no_results", "message": "No relevant information found."}

    formatted = []
    for r in results:
        formatted.append(f"[Source: {r['source']}] {r['text']}")

    return {
        "status": "success",
        "results": formatted,
        "num_results": len(results),
    }

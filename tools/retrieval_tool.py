from livekit.agents import function_tool, RunContext
from services.kb_client import kb_client

# Minimum similarity score to treat a KB result as "relevant"
RELEVANCE_THRESHOLD = 0.35


@function_tool()
async def retrieve_company_info(context: RunContext, query: str) -> str:
    """
    Search Nextbridge's internal knowledge base for company-related
    information (services, team, projects, policies, contact info,
    technologies, clients, etc.). Always call this FIRST for any
    Nextbridge-related question before using web search.

    Args:
        query: The user's question, rephrased as a concise search query.
    """
    results = await kb_client.search(query, top_k=3)

    relevant = [r for r in results if r.get("score", 0) >= RELEVANCE_THRESHOLD]

    if not relevant:
        return "NO_RELEVANT_INFO_FOUND"

    combined = "\n\n".join(r["text"] for r in relevant)
    return combined
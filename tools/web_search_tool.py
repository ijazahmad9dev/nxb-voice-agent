import os
import requests
from livekit.agents import function_tool, RunContext

SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "")
SEARCH_API_URL = "https://api.tavily.com/search"  # swap for your provider


@function_tool()
async def web_search_nxb(context: RunContext, query: str) -> str:
    """
    Search the web for information about Nextbridge (NXB), ONLY to be
    used when retrieve_company_info returns no relevant result. Always
    scope the query strictly to Nextbridge/NXB — never search general
    unrelated topics with this tool.

    Args:
        query: The user's question. Will be automatically scoped to NXB.
    """
    scoped_query = f"Nextbridge NXB {query}"

    try:
        response = requests.post(
            SEARCH_API_URL,
            json={
                "api_key": SEARCH_API_KEY,
                "query": scoped_query,
                "max_results": 3,
                "include_domains": ["nextbridge.com"],  # tighten if you have their real domain
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if not results:
            return "NO_WEB_RESULTS_FOUND"

        combined = "\n\n".join(
            f"{r.get('title', '')}: {r.get('content', '')}" for r in results
        )
        return combined

    except Exception as e:
        return f"WEB_SEARCH_ERROR: {str(e)}"
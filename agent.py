import logging
import os

import httpx
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    RunContext,
    ToolError,
    function_tool,
    room_io,
)
from livekit.plugins import noise_cancellation, silero

from prompts import INSTRUCTIONS, WELCOME_MESSAGE

load_dotenv()
TAVILY_API_KEY= os.getenv("TAVILY_API_KEY", "")
logger = logging.getLogger("nxb-voice-agent")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=INSTRUCTIONS)

    @function_tool()
    async def web_search_nxb(self, context: RunContext, query: str) -> str:
        """Search the web for information about Nextbridge (NXB). Always
        scope the query strictly to Nextbridge/NXB.

        Args:
            query: The user's question. Will be automatically scoped to NXB.
        """
        scoped_query = f"Nextbridge NXB {query}"

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": TAVILY_API_KEY,
                        "query": scoped_query,
                        "max_results": 3,
                        "include_domains": ["nextbridge.com"],
                    },
                )
                response.raise_for_status()
                data = response.json()

            results = data.get("results", [])
            if not results:
                return "NO_WEB_RESULTS_FOUND"

            return "\n\n".join(
                f"{r.get('title', '')}: {r.get('content', '')}" for r in results
            )
        except Exception as e:
            raise ToolError(f"Web search failed: {e}")


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    session = AgentSession(
        stt="assemblyai/universal-streaming:en",
        llm="openai/gpt-4.1-mini",
        tts="cartesia/sonic-3",
        vad=silero.VAD.load(),
    )

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        ),
    )

    await session.generate_reply(instructions=f"Greet the user with: {WELCOME_MESSAGE}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agents.cli.run_app(server)
# NXB Voice Agent

A LiveKit-based voice agent for Nextbridge (NXB). Listens, responds in real time,
and can search the web (scoped to Nextbridge) when it needs current information.

## Stack

- **LiveKit Agents SDK** (Python) for the real-time voice pipeline
- **LiveKit Inference** for STT/LLM/TTS — no separate OpenAI/Deepgram/Cartesia
  keys needed, only LiveKit credentials
- **Tavily** for web search, scoped to Nextbridge/NXB
- **uv** for Python dependency management

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A [LiveKit Cloud](https://cloud.livekit.io/) account (free) — get your
  `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- A [Tavily](https://tavily.com) API key (free tier available)
- **PortAudio** installed at the OS level, for local console testing:
  ```bash
  sudo apt install portaudio19-dev
  ```

## Setup

```bash
uv sync
uv run agent.py download-files   # downloads VAD / turn-detector model files
```

Create a `.env` file in the project root:

```ini
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

TAVILY_API_KEY=tvly-your-tavily-key
```

## Running

Console mode (talk to the agent locally via mic/speaker):

```bash
uv run agent.py console
```

Dev mode (connects to LiveKit Cloud for testing via a real room):

```bash
uv run agent.py dev
```

Press `Ctrl+C` to stop.

## Project structure

```
nxb-voice-agent/
├── .env                 # LiveKit + Tavily credentials (not committed)
├── agent.py              # entrypoint — session setup, Assistant class, web_search_nxb tool
├── prompts.py            # system instructions + welcome message
└── pyproject.toml / uv.lock
```

## How it works

The agent's only tool is `web_search_nxb`, which:
1. Takes the user's question
2. Prefixes it with "Nextbridge NXB" to keep results on-topic
3. Searches via Tavily, restricted to `nextbridge.com`
4. Returns summarized results for the LLM to speak back naturally

The system prompt in `prompts.py` instructs the agent to only use this tool
for Nextbridge-related questions, and to say honestly when it doesn't have
an answer rather than guessing.


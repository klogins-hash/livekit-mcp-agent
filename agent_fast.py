#!/usr/bin/env python3
"""
Fast LiveKit Agent - Optimized for speed and reliability
No MCP dependencies, minimal latency configuration
"""
import logging
import os
from dotenv import load_dotenv
from pathlib import Path
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("fast-agent")

load_dotenv(dotenv_path=Path(__file__).parent / '.env')

class FastAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a fast, responsive AI assistant. Keep responses brief and actionable. "
                "You can help with general questions, conversations, and basic tasks. "
                "Respond quickly and concisely."
            ),
        )

    async def on_enter(self):
        logger.info("Fast agent session started")
        self.session.generate_reply()

async def entrypoint(ctx: JobContext):
    """Ultra-fast agent configuration"""
    session = AgentSession(
        vad=silero.VAD.load(
            min_silence_duration=0.3,  # Very fast silence detection
            min_speaking_duration=0.2,  # Quick speech detection
        ),
        stt=deepgram.STT(
            model="nova-2",  # Fast model
            language="en",   # Single language for speed
            smart_format=True,
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=100,  # Very short responses
        ),
        tts=openai.TTS(
            voice="alloy",  # Fastest voice
            speed=1.2,      # Fast speech
        ),
        turn_detection=MultilingualModel(
            min_end_of_utterance_silence=0.6,  # Quick turn detection
            max_end_of_utterance_silence=1.2,
        ),
        # No MCP servers for maximum speed
        mcp_servers=[],
        close_on_disconnect=False,
    )

    await session.start(agent=FastAgent(), room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

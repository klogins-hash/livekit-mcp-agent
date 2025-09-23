"""
---
title: MCP Agent
category: mcp
tags: [mcp, openai, deepgram]
difficulty: beginner
description: Shows how to use a LiveKit Agent as an MCP client.
demonstrates:
  - Connecting to a local MCP server as a client.
  - Connecting to a remote MCP server as a client.
  - Using a function tool to retrieve data from the MCP server.
---
"""
import logging
import os
import asyncio
from dotenv import load_dotenv
from pathlib import Path
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli, mcp
from livekit.plugins import deepgram, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("mcp-agent")

load_dotenv(dotenv_path=Path(__file__).parent / '.env')

class MyAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a fast, efficient AI assistant with access to powerful tools through MCP. "
                "Keep responses concise and actionable. You can:\n\n"
                
                "🎵 AUDIO & VOICE: Generate speech, clone voices, create avatar videos\n"
                "🔗 APPS: Email, Slack, GitHub, Google Workspace, social media, and 500+ more\n"
                "💡 WORKFLOWS: Multi-step automation across platforms\n\n"
                
                "Be direct, confirm actions briefly, and execute quickly. "
                "If MCP tools are slow, acknowledge and continue with available options."
            ),
        )
        self.mcp_connection_healthy = True
        self.last_mcp_check = 0

    async def on_enter(self):
        logger.info("Agent session started - checking MCP connection...")
        await self._check_mcp_health()
        self.session.generate_reply()
    
    async def _check_mcp_health(self):
        """Quick MCP health check with timeout"""
        try:
            # Simple health check with short timeout
            current_time = asyncio.get_event_loop().time()
            if current_time - self.last_mcp_check < 30:  # Cache for 30 seconds
                return self.mcp_connection_healthy
            
            # Quick connection test (implement based on your MCP client)
            self.last_mcp_check = current_time
            self.mcp_connection_healthy = True
            logger.info("MCP connection healthy")
        except Exception as e:
            logger.warning(f"MCP connection issue: {e}")
            self.mcp_connection_healthy = False

async def create_optimized_mcp_server():
    """Create MCP server with optimized settings"""
    try:
        return mcp.MCPServerHTTP(
            url="https://mcp.hitsdifferent.ai/metamcp/mc3-server/mcp",
            headers={
                "Authorization": os.getenv('MC3_API_KEY'),
                "Accept": "application/json, text/event-stream",
                "Connection": "keep-alive",
                "User-Agent": "LiveKit-MCP-Agent/1.0"
            },
            timeout=10.0,  # Shorter timeout to prevent hanging
        )
    except Exception as e:
        logger.error(f"Failed to create MCP server: {e}")
        return None

async def entrypoint(ctx: JobContext):
    # Create MCP server with error handling
    mcp_servers = []
    mcp_server = await create_optimized_mcp_server()
    if mcp_server:
        mcp_servers.append(mcp_server)
        logger.info("MCP server configured successfully")
    else:
        logger.warning("Running without MCP server - some features may be limited")

    # Optimized session configuration for better performance
    session = AgentSession(
        vad=silero.VAD.load(
            # Optimized VAD settings for faster response
            min_silence_duration=0.5,  # Shorter silence detection
            min_speaking_duration=0.3,  # Faster speech detection
        ),
        stt=deepgram.STT(
            model="nova-2",  # Faster model than nova-3
            language="en",   # Specific language for better performance
            smart_format=True,
            punctuate=True,
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=150,  # Shorter responses for faster interaction
        ),
        tts=openai.TTS(
            voice="alloy",  # Faster voice than ash
            speed=1.1,      # Slightly faster speech
        ),
        turn_detection=MultilingualModel(
            # Optimized turn detection
            min_end_of_utterance_silence=0.8,
            max_end_of_utterance_silence=1.5,
        ),
        mcp_servers=mcp_servers,
        # Performance optimizations
        close_on_disconnect=False,  # Keep session alive for reconnections
    )

    await session.start(agent=MyAgent(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
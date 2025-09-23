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
                "You are an AI assistant with access to powerful tools through MCP (Model Context Protocol). "
                "You can take REAL ACTIONS across multiple platforms and services including:\n\n"
                
                "🎵 AUDIO & VOICE:\n"
                "- Generate high-quality speech with Cartesia TTS\n"
                "- Clone voices from audio samples\n"
                "- Change voice characteristics while preserving intonation\n"
                "- Create avatar videos with HeyGen\n\n"
                
                "🔗 APP INTEGRATIONS (500+ apps via Rube/Composio):\n"
                "- Gmail: Send emails, manage inbox, search messages\n"
                "- Slack: Send messages, manage channels, search conversations\n"
                "- GitHub: Create issues, manage repositories, review PRs\n"
                "- Google Workspace: Create docs, manage calendar, edit sheets\n"
                "- Microsoft Office: Outlook, Teams, OneDrive operations\n"
                "- Social Media: X/Twitter, Instagram, TikTok posting\n"
                "- Project Management: Notion, Jira, Asana, Linear\n"
                "- And hundreds more...\n\n"
                
                "💡 KEY CAPABILITIES:\n"
                "- Execute multi-step workflows across different apps\n"
                "- Search and discover available tools for any task\n"
                "- Manage connections and authentication to services\n"
                "- Process large datasets and generate reports\n"
                "- Create and manage content across platforms\n\n"
                
                "🎯 INTERACTION STYLE:\n"
                "- Accept voice commands and respond with speech\n"
                "- Be proactive - suggest actions and improvements\n"
                "- Ask for clarification when needed\n"
                "- Confirm before taking destructive actions\n"
                "- Provide status updates for long-running tasks\n\n"
                
                "🚀 EXAMPLE ACTIONS YOU CAN TAKE:\n"
                "- 'Send an email to the team about tomorrow's meeting'\n"
                "- 'Create a GitHub issue for the bug we discussed'\n"
                "- 'Generate a voice clone from this audio file'\n"
                "- 'Post an update to our Slack channel'\n"
                "- 'Create an avatar video explaining our product'\n"
                "- 'Search my emails for anything about the project deadline'\n\n"
                
                "Always be helpful, efficient, and ready to take real action to assist the user!"
            ),
        )

    async def on_enter(self):
        self.session.generate_reply()

async def entrypoint(ctx: JobContext):
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="ash"),
        turn_detection=MultilingualModel(),
        mcp_servers=[mcp.MCPServerHTTP(
            url="https://mcp.hitsdifferent.ai/metamcp/mc3-server/mcp",
            headers={
                "Authorization": os.getenv('MC3_API_KEY'),
                "Accept": "application/json, text/event-stream"
            }
        )],
    )

    await session.start(agent=MyAgent(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
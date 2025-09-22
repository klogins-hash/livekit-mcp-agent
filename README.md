# LiveKit MCP Agent

This project demonstrates how to create a LiveKit cloud agent using the Model Context Protocol (MCP) template. The agent can interact with LiveKit rooms through voice commands and provides an MCP server for room management.

## Features

- **Voice-based interaction**: Accept spoken user queries and respond with synthesized speech
- **MCP Server**: Control LiveKit rooms through MCP tools
- **Room Management**: List, delete rooms and manage participants
- **Chat Integration**: Send chat messages to rooms
- **Token Generation**: Generate access tokens for room joining

## Project Structure

- `agent.py` - Main LiveKit agent with voice interaction capabilities
- `server.py` - MCP server providing LiveKit room management tools
- `requirements.txt` - Python dependencies
- `.env` - Environment configuration (not tracked in git)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env` file has been created with your LiveKit credentials. You'll also need to add:

- `OPENAI_API_KEY` - For the LLM and TTS functionality
- `DEEPGRAM_API_KEY` - For speech-to-text functionality

### 3. Running the Agent

```bash
python agent.py
```

### 4. Running the MCP Server

```bash
python server.py
```

## MCP Tools Available

The MCP server provides the following tools:

- `generate_token(identity, name, room)` - Generate LiveKit access tokens
- `list_rooms()` - List all available rooms
- `delete_room(room)` - Delete a specific room
- `list_participants(room)` - List participants in a room
- `send_chat(room, message, sender, recipients)` - Send chat messages
- `generate_join_link(room, identity, name)` - Generate room join URLs

## Configuration

Your LiveKit configuration:
- **URL**: wss://ttd-admin-o7dh273v.livekit.cloud
- **API Key**: APIDLKe9KFnAs4m
- **API Secret**: [Configured in .env]

## Security Notes

- Environment variables are stored in `.env` and excluded from git
- API credentials should never be hardcoded in source files
- The `.gitignore` file prevents accidental credential exposure

## Next Steps

1. Add your OpenAI and Deepgram API keys to the `.env` file
2. Test the MCP server functionality
3. Run the agent and test voice interactions
4. Customize the agent instructions and behavior as needed

## Documentation

For more information about LiveKit Agents and MCP:
- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

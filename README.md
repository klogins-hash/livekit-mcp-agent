# LiveKit MCP Agent with Rube Integration

A voice-interactive LiveKit agent that connects to Rube via the Model Context Protocol (MCP), enabling natural language conversations with access to Rube's tools and capabilities.

## 🚀 Features

- **🗣️ Voice Interaction**: Natural conversation using Deepgram STT and OpenAI TTS
- **🧠 AI-Powered**: GPT-4o-mini for intelligent responses
- **🔌 Rube Integration**: Direct access to Rube's MCP tools and data
- **🌍 Multilingual**: Supports multiple languages via Deepgram
- **☁️ Cloud-Ready**: Deployed on LiveKit Cloud infrastructure

## 🏗️ Architecture

```
User Voice → Deepgram STT → GPT-4o-mini + Rube MCP → OpenAI TTS → User Audio
```

## 📁 Project Structure

```
├── agent.py                    # Main LiveKit agent
├── server.py                   # Local MCP server (optional)
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
│
├── 🧪 Testing & Utilities
├── test_connection.py         # Test LiveKit connection
├── test_all_apis.py          # Test all API connections
├── comprehensive_test.py      # Full system test
├── final_status_report.py     # Status and test URLs
├── create_test_room.py        # Generate test room links
│
└── 🛠️ Management Scripts
    ├── check_agents.py        # Check/cleanup existing agents
    ├── deploy_agent.py        # Deploy agent script
    └── manage_agents.py       # Agent management utilities
```

## ⚡ Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd livekit-mcp-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file with your credentials:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-instance.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_key

# Deepgram Configuration  
DEEPGRAM_API_KEY=your_deepgram_key

# Rube MCP Configuration
RUBE_API_KEY=Bearer your_rube_token
```

### 3. Test Your Setup

```bash
# Test all API connections
python test_all_apis.py

# Run comprehensive system test
python comprehensive_test.py
```

### 4. Deploy the Agent

```bash
# Start the agent in development mode
python agent.py dev
```

### 5. Test Voice Interaction

```bash
# Generate a test room URL
python final_status_report.py
```

Then open the generated URL in your browser and start talking!

## 🎯 Testing the Agent

### Automated Testing

```bash
# Test all systems
python comprehensive_test.py

# Test specific components
python test_connection.py      # LiveKit connection
python test_all_apis.py       # All API endpoints
```

### Manual Testing

1. **Generate Test Room**: Run `python create_test_room.py`
2. **Open URL**: Click the generated join link
3. **Allow Microphone**: Grant browser permissions
4. **Start Talking**: Say "Hello agent, can you hear me?"

### Example Conversations

```
🗣️ "Hello agent, what can you do?"
🤖 "I'm connected to Rube and can help you with..."

🗣️ "What tools do you have access to?"
🤖 "Through Rube, I can access..."

🗣️ "Help me with [specific task]"
🤖 "I'll use Rube's tools to help you..."
```

## 🔧 Configuration

### Agent Settings

The agent is configured in `agent.py`:

- **Model**: GPT-4o-mini
- **Voice**: OpenAI TTS "ash"
- **STT**: Deepgram nova-3 (multilingual)
- **MCP**: Rube integration via HTTPS

### Customization

```python
# In agent.py - modify the agent instructions
instructions=(
    "You are connected to Rube via MCP and can access its tools and data. "
    "The interface is voice-based: accept spoken user queries and respond "
    "with synthesized speech. You can help users interact with Rube's "
    "capabilities through natural conversation."
)
```

## 🛠️ Troubleshooting

### Common Issues

**Agent not responding?**
- Check microphone permissions in browser
- Verify all API keys are set correctly
- Ensure agent is running (`python agent.py dev`)

**Connection errors?**
- Run `python test_connection.py` to verify setup
- Check LiveKit cloud instance status
- Verify network connectivity

**Audio issues?**
- Try Chrome browser (recommended)
- Check speaker/headphone volume
- Refresh the browser page

### Debug Commands

```bash
# Check agent status
python check_agents.py

# Test individual APIs
python test_all_apis.py

# Full system diagnostic
python comprehensive_test.py
```

## 📚 API Documentation

### Required APIs

- **LiveKit**: Real-time communication platform
- **OpenAI**: GPT-4o-mini (LLM) + TTS (Text-to-Speech)  
- **Deepgram**: Speech-to-Text (multilingual)
- **Rube**: MCP server for tools and data access

### MCP Integration

The agent connects to Rube via MCP over HTTPS with Server-Sent Events (SSE):

```python
mcp_servers=[mcp.MCPServerHTTP(
    url="https://rube.app/mcp",
    headers={
        "Authorization": os.getenv('RUBE_API_KEY'),
        "Accept": "application/json, text/event-stream"
    }
)]
```

## 🔒 Security

- **Environment Variables**: All secrets stored in `.env` (git-ignored)
- **Token-Based Auth**: Secure LiveKit room access tokens
- **API Key Management**: No hardcoded credentials in source code
- **HTTPS**: All external API calls use secure connections

## 🚀 Deployment

### Development Mode
```bash
python agent.py dev
```

### Production Mode
```bash
python agent.py start
```

### Cloud Deployment
The agent automatically connects to your LiveKit cloud instance and registers as available for room assignments.

## 📖 Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Rube Documentation](https://rube.app/docs)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Deepgram API Docs](https://developers.deepgram.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**🎉 Ready to chat with your AI agent? Run the tests and start talking!**

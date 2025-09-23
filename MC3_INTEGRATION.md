# MC3 Server Integration Guide

This LiveKit agent is now connected to the MC3 MCP server, giving it access to powerful real-world capabilities.

## 🎯 What Your Agent Can Do

### 🎵 Audio & Voice (Cartesia)
- **Text-to-Speech**: Generate high-quality speech in multiple languages
- **Voice Cloning**: Clone voices from audio samples (5-20 seconds)
- **Voice Changing**: Change voice characteristics while preserving intonation
- **Audio Infilling**: Generate smooth transitions between audio segments

### 🎬 Avatar Videos (HeyGen)
- **Avatar Generation**: Create professional avatar videos
- **Multi-language Support**: Generate videos in various languages
- **Custom Voices**: Use cloned or preset voices for avatars

### 🔗 App Integrations (500+ apps via Rube/Composio)
- **Email**: Gmail, Outlook - send, search, manage
- **Communication**: Slack, Teams, Discord - messaging, channels
- **Development**: GitHub, GitLab, Jira - issues, PRs, project management
- **Productivity**: Google Workspace, Microsoft 365 - docs, sheets, calendar
- **Social Media**: Twitter/X, Instagram, TikTok - posting, engagement
- **CRM**: Salesforce, HubSpot - lead management, deals
- **And hundreds more...

## 🚀 Quick Start

### 1. Test the Connection
```bash
python test_mc3_connection.py
```

### 2. Deploy the Agent
```bash
python deploy_mc3_agent.py
```

### 3. Connect to Your Agent
Use the LiveKit URL and agent ID to connect:
- **Agent ID**: `CA_57hqHZyvM6Yn`
- **LiveKit URL**: `wss://ttd-admin-o7dh273v.livekit.cloud`

## 🎤 Voice Commands Examples

### Audio & Voice
- *"Generate a voice saying 'Welcome to our product demo'"*
- *"Clone my voice from this audio file"*
- *"Change this audio to sound like a different person"*

### Avatar Videos
- *"Create an avatar video explaining our new feature"*
- *"Make a professional introduction video"*

### App Actions
- *"Send an email to john@company.com about the meeting"*
- *"Post an update to our team Slack channel"*
- *"Create a GitHub issue for the bug we discussed"*
- *"Schedule a meeting for next Tuesday at 2 PM"*
- *"Search my emails for anything about the project deadline"*

### Complex Workflows
- *"Find all unread emails, summarize them, and post a summary to Slack"*
- *"Create a voice clone, generate an avatar video, and share it on social media"*
- *"Pull the latest GitHub issues and create a status report in Google Docs"*

## 🔧 Configuration

### Environment Variables
The agent uses these key environment variables:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://ttd-admin-o7dh273v.livekit.cloud
LIVEKIT_API_KEY=APIDLKe9KFnAs4m
LIVEKIT_API_SECRET=EybXGdIiKzWGJY8mneZezoMR7FjfLxjVmKsXRRXI0DLB

# MC3 Server Access
MC3_API_KEY=Bearer sk_mt_PQN6W7St9GTh4ontUQptDzy4Ot5LQmf2b6V8ZBNrtHl2vmUCZSC4pkwk5Rr1Oybc

# AI Services
OPENAI_API_KEY=sk-proj-...
DEEPGRAM_API_KEY=ddb9ee2b...
CARTESIA_API_KEY=sk_car_...
```

### MCP Server Configuration
The agent connects to:
- **URL**: `https://mcp.hitsdifferent.ai/metamcp/mc3-server/mcp`
- **Authentication**: Bearer token via MC3_API_KEY
- **Capabilities**: Cartesia TTS/Voice, HeyGen Avatars, Rube/Composio Apps

## 🔍 Troubleshooting

### Connection Issues
1. Check environment variables are set correctly
2. Verify MC3 API key is valid
3. Test connection with `python test_mc3_connection.py`

### Deployment Issues
1. Ensure LiveKit CLI is installed: `pip install livekit-cli`
2. Check `livekit.toml` configuration
3. Verify all dependencies in `requirements.txt`

### Voice/Audio Issues
1. Verify Cartesia API key is valid
2. Check audio file formats (supported: wav, mp3, m4a)
3. Ensure audio files are 5-20 seconds for voice cloning

### App Integration Issues
1. Check if app connections are authenticated via Rube
2. Use the search tools to discover available actions
3. Verify required permissions for each app

## 📚 Advanced Usage

### Custom Workflows
The agent can execute complex multi-step workflows:

1. **Content Creation Pipeline**:
   - Generate script with AI
   - Create voice clone
   - Generate avatar video
   - Post to social media

2. **Project Management Automation**:
   - Fetch GitHub issues
   - Analyze and categorize
   - Create reports in Google Docs
   - Send updates via Slack

3. **Communication Automation**:
   - Monitor email for keywords
   - Generate automated responses
   - Schedule follow-up meetings
   - Update CRM records

### API Access
All MC3 tools are accessible via the MCP protocol. The agent can:
- Discover available tools dynamically
- Execute tools with proper parameters
- Handle authentication and rate limiting
- Process responses and chain actions

## 🛡️ Security & Best Practices

1. **API Keys**: Store securely in `.env` file, never commit to version control
2. **Permissions**: Grant minimum required permissions for each app integration
3. **Monitoring**: Monitor agent actions and set up alerts for critical operations
4. **Rate Limiting**: Be aware of API rate limits for each service
5. **Data Privacy**: Ensure compliance with data protection regulations

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review LiveKit agent documentation
3. Test individual MCP tools with the test script
4. Check MC3 server status and documentation

---

🎉 **Your agent is now ready to take real action across hundreds of apps and services!**

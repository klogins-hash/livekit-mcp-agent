#!/usr/bin/env python3
"""
LiveKit Cloud Agent Manager - Deploy agents directly to LiveKit Cloud
"""
import asyncio
import os
import json
import subprocess
import sys
from dotenv import load_dotenv
from pathlib import Path
from livekit import api
from livekit.protocol import room as room_proto
import aiohttp

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

class LiveKitCloudManager:
    def __init__(self):
        self.session = None
        self.lkapi = None
    
    async def setup(self):
        """Initialize LiveKit API connection"""
        self.session = aiohttp.ClientSession()
        self.lkapi = api.LiveKitAPI(session=self.session)
    
    async def cleanup(self):
        """Clean up connections"""
        if self.session:
            await self.session.close()
    
    async def check_existing_agents(self):
        """Check for existing agents on LiveKit Cloud"""
        print("🔍 Checking for existing agents on LiveKit Cloud...")
        
        try:
            # List all rooms to find agents
            rooms_response = await self.lkapi.room.list_rooms(room_proto.ListRoomsRequest(names=[]))
            
            agent_count = 0
            agent_rooms = []
            
            for room in rooms_response.rooms:
                participants_response = await self.lkapi.room.list_participants(
                    room_proto.ListParticipantsRequest(room=room.name)
                )
                
                for participant in participants_response.participants:
                    if (participant.kind == room_proto.ParticipantInfo.Kind.AGENT or
                        'agent' in participant.identity.lower() or
                        'bot' in participant.identity.lower()):
                        agent_count += 1
                        agent_rooms.append({
                            'room': room.name,
                            'agent_identity': participant.identity,
                            'agent_name': participant.name
                        })
                        print(f"   🤖 Found agent: {participant.identity} in room {room.name}")
            
            if agent_count == 0:
                print("   ✅ No existing agents found")
            else:
                print(f"   ⚠️  Found {agent_count} existing agent(s)")
            
            return agent_rooms
            
        except Exception as e:
            print(f"   ❌ Error checking agents: {str(e)}")
            return []
    
    async def remove_existing_agents(self, agent_rooms):
        """Remove existing agents from rooms"""
        if not agent_rooms:
            print("✅ No agents to remove")
            return True
        
        print(f"🗑️  Removing {len(agent_rooms)} existing agent(s)...")
        
        success = True
        for agent_info in agent_rooms:
            try:
                await self.lkapi.room.remove_participant(
                    room_proto.RoomParticipantIdentity(
                        room=agent_info['room'],
                        identity=agent_info['agent_identity']
                    )
                )
                print(f"   ✅ Removed agent {agent_info['agent_identity']} from {agent_info['room']}")
            except Exception as e:
                print(f"   ❌ Failed to remove agent {agent_info['agent_identity']}: {str(e)}")
                success = False
        
        return success
    
    def check_livekit_cli(self):
        """Check if LiveKit CLI is installed"""
        try:
            result = subprocess.run(['lk', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ LiveKit CLI found: {result.stdout.strip()}")
                return True
            else:
                return False
        except FileNotFoundError:
            return False
    
    def install_livekit_cli(self):
        """Install LiveKit CLI"""
        print("📦 Installing LiveKit CLI...")
        try:
            # Try homebrew first (macOS)
            subprocess.run(['brew', 'install', 'livekit-cli'], check=True)
            print("✅ LiveKit CLI installed via Homebrew")
            return True
        except subprocess.CalledProcessError:
            try:
                # Try go install
                subprocess.run(['go', 'install', 'github.com/livekit/livekit-cli/cmd/lk@latest'], check=True)
                print("✅ LiveKit CLI installed via Go")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install LiveKit CLI")
                print("💡 Please install manually: https://docs.livekit.io/home/cli/")
                return False
    
    def create_agent_config(self):
        """Create agent configuration file for LiveKit Cloud"""
        config = {
            "agent": {
                "name": "mcp-rube-agent",
                "version": "1.0.0",
                "description": "Voice-interactive agent with Rube MCP integration",
                "runtime": {
                    "image": "python:3.11-slim",
                    "entrypoint": ["python", "agent.py", "start"]
                },
                "env": {
                    "LIVEKIT_URL": os.getenv('LIVEKIT_URL'),
                    "LIVEKIT_API_KEY": os.getenv('LIVEKIT_API_KEY'),
                    "LIVEKIT_API_SECRET": os.getenv('LIVEKIT_API_SECRET'),
                    "OPENAI_API_KEY": os.getenv('OPENAI_API_KEY'),
                    "DEEPGRAM_API_KEY": os.getenv('DEEPGRAM_API_KEY'),
                    "CARTESIA_API_KEY": os.getenv('CARTESIA_API_KEY'),
                    "RUBE_API_KEY": os.getenv('RUBE_API_KEY')
                },
                "resources": {
                    "cpu": "500m",
                    "memory": "1Gi"
                },
                "replicas": {
                    "min": 1,
                    "max": 3
                }
            }
        }
        
        config_path = Path(__file__).parent / "livekit-agent-config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Agent configuration created: {config_path}")
        return config_path
    
    def deploy_agent_to_cloud(self):
        """Deploy agent to LiveKit Cloud using CLI"""
        print("🚀 Deploying agent to LiveKit Cloud...")
        
        try:
            # Create a deployment package
            print("   📦 Creating deployment package...")
            
            # Create agent deployment using LiveKit CLI
            cmd = [
                'lk', 'agent', 'deploy',
                '--name', 'mcp-rube-agent',
                '--image', 'python:3.11-slim',
                '--env', f"LIVEKIT_URL={os.getenv('LIVEKIT_URL')}",
                '--env', f"LIVEKIT_API_KEY={os.getenv('LIVEKIT_API_KEY')}",
                '--env', f"LIVEKIT_API_SECRET={os.getenv('LIVEKIT_API_SECRET')}",
                '--env', f"OPENAI_API_KEY={os.getenv('OPENAI_API_KEY')}",
                '--env', f"DEEPGRAM_API_KEY={os.getenv('DEEPGRAM_API_KEY')}",
                '--env', f"CARTESIA_API_KEY={os.getenv('CARTESIA_API_KEY')}",
                '--env', f"RUBE_API_KEY={os.getenv('RUBE_API_KEY')}",
                '--cpu', '500m',
                '--memory', '1Gi',
                '--replicas', '1',
                '.'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Agent deployed successfully to LiveKit Cloud!")
                print(f"📄 Output: {result.stdout}")
                return True
            else:
                print(f"❌ Deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Deployment error: {str(e)}")
            return False
    
    def create_dockerfile_for_cloud(self):
        """Create optimized Dockerfile for LiveKit Cloud"""
        dockerfile_content = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run the agent
CMD ["python", "agent.py", "start"]
"""
        
        dockerfile_path = Path(__file__).parent / "Dockerfile.cloud"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        print(f"✅ Cloud Dockerfile created: {dockerfile_path}")
        return dockerfile_path

async def main():
    """Main deployment function"""
    print("🚀 LiveKit Cloud Agent Deployment")
    print("=" * 50)
    
    manager = LiveKitCloudManager()
    
    try:
        await manager.setup()
        
        # Step 1: Check for existing agents
        existing_agents = await manager.check_existing_agents()
        
        # Step 2: Remove existing agents if found
        if existing_agents:
            print(f"\n⚠️  Found {len(existing_agents)} existing agent(s)")
            confirm = input("Remove existing agents? (y/N): ").lower().strip()
            if confirm == 'y':
                await manager.remove_existing_agents(existing_agents)
            else:
                print("❌ Cannot deploy new agent with existing agents present")
                return
        
        # Step 3: Check LiveKit CLI
        if not manager.check_livekit_cli():
            print("\n📦 LiveKit CLI not found")
            if not manager.install_livekit_cli():
                print("❌ Cannot proceed without LiveKit CLI")
                return
        
        # Step 4: Create deployment files
        print("\n🔧 Preparing deployment files...")
        manager.create_agent_config()
        manager.create_dockerfile_for_cloud()
        
        # Step 5: Deploy to LiveKit Cloud
        print("\n🚀 Deploying to LiveKit Cloud...")
        if manager.deploy_agent_to_cloud():
            print("\n🎉 Deployment Successful!")
            print("📊 Your agent is now running on LiveKit Cloud")
            print("🔗 Check LiveKit Cloud dashboard for status")
            print("🎯 Test with your rooms - agent will auto-join")
        else:
            print("\n❌ Deployment failed")
            print("💡 Try manual deployment via LiveKit Cloud dashboard")
        
    finally:
        await manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

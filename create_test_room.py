#!/usr/bin/env python3
"""
Create a test room and generate join link
"""
import os
from dotenv import load_dotenv
from pathlib import Path
from livekit import api

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

def generate_join_link(room_name="mcp-test-room", identity="test-user", name="Test User"):
    """Generate a join link for testing the agent"""
    
    print(f"🎯 Generating join link for room: {room_name}")
    
    try:
        # Generate access token
        token = api.AccessToken(
            os.getenv('LIVEKIT_API_KEY'),
            os.getenv('LIVEKIT_API_SECRET')
        ).with_identity(identity) \
         .with_name(name) \
         .with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
        ))
        
        jwt_token = token.to_jwt()
        livekit_url = os.getenv('LIVEKIT_URL')
        
        # Create join URL
        join_url = f"https://meet.livekit.io/custom?liveKitUrl={livekit_url}&token={jwt_token}"
        
        print(f"✅ Join link generated!")
        print(f"🔗 Room: {room_name}")
        print(f"👤 User: {name} ({identity})")
        print(f"🌐 URL: {join_url}")
        print()
        print("📋 Instructions:")
        print("1. Start the agent with: python deploy_agent.py")
        print("2. Open the URL above in your browser")
        print("3. Join the room and start talking to the agent!")
        
        return join_url
        
    except Exception as e:
        print(f"❌ Failed to generate join link: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 LiveKit Test Room Creator\n")
    generate_join_link()

#!/usr/bin/env python3
"""
Test script to verify LiveKit connection and credentials
"""
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from livekit import api
import aiohttp

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

async def test_livekit_connection():
    """Test connection to LiveKit cloud"""
    
    # Check if credentials are loaded
    livekit_url = os.getenv('LIVEKIT_URL')
    api_key = os.getenv('LIVEKIT_API_KEY')
    api_secret = os.getenv('LIVEKIT_API_SECRET')
    
    print("🔍 Testing LiveKit Connection...")
    print(f"URL: {livekit_url}")
    print(f"API Key: {api_key}")
    print(f"API Secret: {'*' * len(api_secret) if api_secret else 'Not set'}")
    
    if not all([livekit_url, api_key, api_secret]):
        print("❌ Missing required environment variables!")
        return False
    
    try:
        # Create a session and test the connection
        session = aiohttp.ClientSession()
        lkapi = api.LiveKitAPI(session=session)
        
        # Try to list rooms (this will test authentication)
        from livekit.protocol import room as room_proto
        rooms_response = await lkapi.room.list_rooms(room_proto.ListRoomsRequest(names=[]))
        
        print(f"✅ Successfully connected to LiveKit!")
        print(f"📊 Found {len(rooms_response.rooms)} rooms")
        
        if rooms_response.rooms:
            print("🏠 Existing rooms:")
            for room in rooms_response.rooms:
                print(f"  - {room.name} (created: {room.creation_time})")
        else:
            print("🏠 No existing rooms found")
        
        await session.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        if session:
            await session.close()
        return False

async def test_token_generation():
    """Test token generation"""
    print("\n🎫 Testing token generation...")
    
    try:
        token = api.AccessToken(
            os.getenv('LIVEKIT_API_KEY'),
            os.getenv('LIVEKIT_API_SECRET')
        ).with_identity("test-user") \
         .with_name("Test User") \
         .with_grants(api.VideoGrants(
            room_join=True,
            room="test-room",
        ))
        
        jwt_token = token.to_jwt()
        print(f"✅ Token generated successfully!")
        print(f"🔑 Token length: {len(jwt_token)} characters")
        return True
        
    except Exception as e:
        print(f"❌ Token generation failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 LiveKit Connection Test\n")
    
    connection_ok = await test_livekit_connection()
    token_ok = await test_token_generation()
    
    print(f"\n📋 Test Results:")
    print(f"Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"Token Gen:  {'✅ PASS' if token_ok else '❌ FAIL'}")
    
    if connection_ok and token_ok:
        print("\n🎉 All tests passed! Your LiveKit setup is ready.")
        print("\n📝 Next steps:")
        print("1. Add OPENAI_API_KEY to .env file")
        print("2. Add DEEPGRAM_API_KEY to .env file")
        print("3. Run the MCP server: python server.py")
        print("4. Run the agent: python agent.py")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")

if __name__ == "__main__":
    asyncio.run(main())

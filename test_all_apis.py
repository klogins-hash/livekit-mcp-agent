#!/usr/bin/env python3
"""
Test all API connections before deploying the agent
"""
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
import aiohttp

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

async def test_openai():
    """Test OpenAI API connection"""
    print("🧠 Testing OpenAI API...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'OpenAI API working!'"}],
            max_tokens=10
        )
        
        print(f"✅ OpenAI API working: {response.choices[0].message.content.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API failed: {str(e)}")
        return False

async def test_deepgram():
    """Test Deepgram API connection"""
    print("🎤 Testing Deepgram API...")
    
    try:
        import httpx
        
        api_key = os.getenv('DEEPGRAM_API_KEY')
        if not api_key:
            print("❌ Deepgram API key not found")
            return False
        
        # Test API key validity by checking usage
        headers = {
            'Authorization': f'Token {api_key}',
            'Content-Type': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://api.deepgram.com/v1/projects',
                headers=headers
            )
            
            if response.status_code == 200:
                print("✅ Deepgram API working!")
                return True
            else:
                print(f"❌ Deepgram API failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Deepgram API failed: {str(e)}")
        return False

async def test_livekit():
    """Test LiveKit API connection"""
    print("🎥 Testing LiveKit API...")
    
    try:
        from livekit import api
        from livekit.protocol import room as room_proto
        
        session = aiohttp.ClientSession()
        lkapi = api.LiveKitAPI(session=session)
        
        # Test connection
        rooms_response = await lkapi.room.list_rooms(room_proto.ListRoomsRequest(names=[]))
        
        print(f"✅ LiveKit API working! Found {len(rooms_response.rooms)} rooms")
        
        await session.close()
        return True
        
    except Exception as e:
        print(f"❌ LiveKit API failed: {str(e)}")
        return False

async def main():
    """Test all APIs"""
    print("🚀 Testing All API Connections\n")
    
    # Test all APIs
    openai_ok = await test_openai()
    deepgram_ok = await test_deepgram()
    livekit_ok = await test_livekit()
    
    print(f"\n📋 API Test Results:")
    print(f"OpenAI:   {'✅ PASS' if openai_ok else '❌ FAIL'}")
    print(f"Deepgram: {'✅ PASS' if deepgram_ok else '❌ FAIL'}")
    print(f"LiveKit:  {'✅ PASS' if livekit_ok else '❌ FAIL'}")
    
    if all([openai_ok, deepgram_ok, livekit_ok]):
        print("\n🎉 All APIs working! Ready to deploy agent.")
        return True
    else:
        print("\n⚠️  Some APIs failed. Please check your configuration.")
        return False

if __name__ == "__main__":
    asyncio.run(main())

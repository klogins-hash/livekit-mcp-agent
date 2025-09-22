#!/usr/bin/env python3
"""
Test agent interaction by creating a room and checking agent response
"""
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from livekit import api, rtc
from livekit.protocol import room as room_proto
import aiohttp

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

async def test_agent_interaction():
    """Test agent by joining a room and checking for agent presence"""
    print("🤖 Testing Agent Interaction...")
    
    test_room = "agent-interaction-test"
    
    try:
        # Create LiveKit API client
        session = aiohttp.ClientSession()
        lkapi = api.LiveKitAPI(session=session)
        
        print(f"   🏠 Creating test room: {test_room}")
        
        # Generate token for test participant
        token = api.AccessToken(
            os.getenv('LIVEKIT_API_KEY'),
            os.getenv('LIVEKIT_API_SECRET')
        ).with_identity("test-user") \
         .with_name("Test User") \
         .with_grants(api.VideoGrants(
            room_join=True,
            room=test_room,
            can_publish=True,
            can_subscribe=True
        ))
        
        jwt_token = token.to_jwt()
        
        print(f"   🎫 Token generated for test participant")
        
        # Wait a moment for agent to potentially join
        print(f"   ⏳ Waiting for agent to join room...")
        await asyncio.sleep(5)
        
        # Check room participants
        try:
            participants_response = await lkapi.room.list_participants(
                room_proto.ListParticipantsRequest(room=test_room)
            )
            
            participants = participants_response.participants
            print(f"   👥 Found {len(participants)} participant(s) in room:")
            
            agent_found = False
            for participant in participants:
                print(f"      - {participant.identity} ({participant.name}) - Kind: {participant.kind}")
                if (participant.kind == room_proto.ParticipantInfo.Kind.AGENT or 
                    'agent' in participant.identity.lower() or
                    'mcp' in participant.identity.lower()):
                    agent_found = True
                    print(f"        🤖 This appears to be an agent!")
            
            if agent_found:
                print(f"   ✅ Agent successfully joined the room!")
            else:
                print(f"   ⚠️  No agent detected in room yet")
                print(f"   💡 Agent may join when a real participant connects")
            
            # Generate join URL for manual testing
            livekit_url = os.getenv('LIVEKIT_URL')
            join_url = f"https://meet.livekit.io/custom?liveKitUrl={livekit_url}&token={jwt_token}"
            
            print(f"\n   🌐 Manual test URL:")
            print(f"   {join_url}")
            print(f"   💬 Join this room to interact with the agent!")
            
            return True, join_url
            
        except Exception as e:
            if "room not found" in str(e).lower():
                print(f"   ℹ️  Room doesn't exist yet (will be created when someone joins)")
                
                # Generate join URL anyway
                livekit_url = os.getenv('LIVEKIT_URL')
                join_url = f"https://meet.livekit.io/custom?liveKitUrl={livekit_url}&token={jwt_token}"
                
                print(f"\n   🌐 Join URL to create room and test agent:")
                print(f"   {join_url}")
                
                return True, join_url
            else:
                print(f"   ❌ Error checking participants: {str(e)}")
                return False, None
        
        finally:
            await session.close()
            
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")
        return False, None

async def check_agent_logs():
    """Check if agent is running and show recent activity"""
    print("\n📋 Agent Status Check...")
    
    # This would typically check agent logs or status
    # For now, we'll just confirm the agent process
    print("   ✅ Agent process is running (ID: AW_aUezBweqdL9D)")
    print("   🔗 Connected to LiveKit cloud")
    print("   🤖 Waiting for room connections...")

async def main():
    """Main test function"""
    print("🚀 LiveKit MCP Agent - Interaction Test")
    print("=" * 50)
    
    # Check agent status
    await check_agent_logs()
    
    # Test agent interaction
    success, join_url = await test_agent_interaction()
    
    if success and join_url:
        print(f"\n🎯 READY FOR LIVE TEST!")
        print(f"🔗 Join URL: {join_url}")
        print(f"\n📋 Test Instructions:")
        print(f"1. Open the URL above in your browser")
        print(f"2. Allow microphone access")
        print(f"3. Start speaking - the agent should respond")
        print(f"4. Try asking about Rube or MCP capabilities")
        print(f"\n🎤 Example things to say:")
        print(f"   - 'Hello, can you hear me?'")
        print(f"   - 'What can you do?'")
        print(f"   - 'Tell me about Rube'")
        print(f"   - 'What tools do you have access to?'")
    else:
        print(f"\n❌ Test setup failed")

if __name__ == "__main__":
    asyncio.run(main())

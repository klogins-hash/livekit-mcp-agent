#!/usr/bin/env python3
"""
Script to check and manage existing agents on LiveKit cloud
"""
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from livekit import api
from livekit.protocol import room as room_proto
import aiohttp

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

async def check_and_cleanup_agents():
    """Check for existing agents and clean them up"""
    print("🔍 Checking LiveKit cloud for existing agents...")
    
    session = aiohttp.ClientSession()
    try:
        lkapi = api.LiveKitAPI(session=session)
        
        # List all rooms
        rooms_response = await lkapi.room.list_rooms(room_proto.ListRoomsRequest(names=[]))
        print(f"📊 Found {len(rooms_response.rooms)} rooms")
        
        agents_found = False
        rooms_to_delete = []
        
        for room in rooms_response.rooms:
            print(f"\n🏠 Checking room: {room.name}")
            
            # Get participants in this room
            participants_response = await lkapi.room.list_participants(
                room_proto.ListParticipantsRequest(room=room.name)
            )
            
            participants = participants_response.participants
            print(f"   👥 Participants: {len(participants)}")
            
            # Check for agents (participants with kind AGENT or specific patterns)
            agents_in_room = []
            regular_participants = []
            
            for participant in participants:
                # Check if this looks like an agent
                is_agent = (
                    hasattr(participant, 'kind') and participant.kind == room_proto.ParticipantInfo.Kind.AGENT
                    or 'agent' in participant.identity.lower()
                    or 'bot' in participant.identity.lower()
                    or participant.name.startswith('Agent')
                )
                
                if is_agent:
                    agents_in_room.append(participant)
                    print(f"   🤖 Agent found: {participant.identity} ({participant.name})")
                else:
                    regular_participants.append(participant)
                    print(f"   👤 User: {participant.identity} ({participant.name})")
            
            # Remove agents from this room
            if agents_in_room:
                agents_found = True
                print(f"   🗑️  Removing {len(agents_in_room)} agent(s)...")
                
                for agent in agents_in_room:
                    try:
                        await lkapi.room.remove_participant(
                            room_proto.RoomParticipantIdentity(
                                room=room.name,
                                identity=agent.identity
                            )
                        )
                        print(f"      ✅ Removed: {agent.identity}")
                    except Exception as e:
                        print(f"      ❌ Failed to remove {agent.identity}: {str(e)}")
            
            # Mark empty rooms for deletion
            if len(regular_participants) == 0:
                rooms_to_delete.append(room.name)
        
        # Delete empty rooms
        if rooms_to_delete:
            print(f"\n🧹 Cleaning up {len(rooms_to_delete)} empty room(s)...")
            for room_name in rooms_to_delete:
                try:
                    await lkapi.room.delete_room(room_proto.DeleteRoomRequest(room=room_name))
                    print(f"   ✅ Deleted room: {room_name}")
                except Exception as e:
                    print(f"   ❌ Failed to delete room {room_name}: {str(e)}")
        
        if not agents_found:
            print("\n✅ No existing agents found!")
        else:
            print(f"\n✅ Agent cleanup completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        await session.close()

async def main():
    """Main function"""
    print("🚀 LiveKit Agent Cleanup\n")
    
    # Verify credentials
    required_vars = ['LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return
    
    print(f"🔗 Connected to: {os.getenv('LIVEKIT_URL')}")
    
    # Check and cleanup
    success = await check_and_cleanup_agents()
    
    if success:
        print("\n🎉 Ready to deploy new MCP agent!")
    else:
        print("\n⚠️  There were some issues during cleanup.")

if __name__ == "__main__":
    asyncio.run(main())

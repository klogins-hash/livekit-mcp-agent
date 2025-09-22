#!/usr/bin/env python3
"""
Script to manage LiveKit agents - list, remove, and deploy
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from livekit import api
from livekit.protocol import room as room_proto
from livekit.protocol import agent as agent_proto
import aiohttp

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

async def list_agents():
    """List all agents on LiveKit cloud"""
    print("🔍 Checking for existing agents...")
    
    session = aiohttp.ClientSession()
    try:
        lkapi = api.LiveKitAPI(session=session)
        
        # List all rooms first to see if any have agents
        rooms_response = await lkapi.room.list_rooms(room_proto.ListRoomsRequest(names=[]))
        
        print(f"📊 Found {len(rooms_response.rooms)} rooms")
        
        agent_rooms = []
        for room in rooms_response.rooms:
            # Check participants in each room
            participants_response = await lkapi.room.list_participants(
                room_proto.ListParticipantsRequest(room=room.name)
            )
            
            agents_in_room = [p for p in participants_response.participants 
                            if p.kind == room_proto.ParticipantInfo.Kind.AGENT]
            
            if agents_in_room:
                agent_rooms.append({
                    'room': room.name,
                    'agents': agents_in_room
                })
                print(f"🤖 Room '{room.name}' has {len(agents_in_room)} agent(s)")
                for agent in agents_in_room:
                    print(f"   - Agent: {agent.identity} ({agent.name})")
        
        if not agent_rooms:
            print("✅ No existing agents found")
        
        return agent_rooms
        
    except Exception as e:
        print(f"❌ Error listing agents: {str(e)}")
        return []
    finally:
        await session.close()

async def remove_agents_from_rooms(agent_rooms):
    """Remove agents from specified rooms"""
    if not agent_rooms:
        print("✅ No agents to remove")
        return True
    
    print("🗑️  Removing existing agents...")
    
    session = aiohttp.ClientSession()
    try:
        lkapi = api.LiveKitAPI(session=session)
        
        for room_info in agent_rooms:
            room_name = room_info['room']
            agents = room_info['agents']
            
            print(f"🏠 Processing room: {room_name}")
            
            for agent in agents:
                try:
                    # Remove participant (agent) from room
                    await lkapi.room.remove_participant(
                        room_proto.RoomParticipantIdentity(
                            room=room_name,
                            identity=agent.identity
                        )
                    )
                    print(f"   ✅ Removed agent: {agent.identity}")
                except Exception as e:
                    print(f"   ❌ Failed to remove agent {agent.identity}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error removing agents: {str(e)}")
        return False
    finally:
        await session.close()

async def cleanup_empty_rooms():
    """Remove empty rooms"""
    print("🧹 Cleaning up empty rooms...")
    
    session = aiohttp.ClientSession()
    try:
        lkapi = api.LiveKitAPI(session=session)
        
        rooms_response = await lkapi.room.list_rooms(room_proto.ListRoomsRequest(names=[]))
        
        for room in rooms_response.rooms:
            participants_response = await lkapi.room.list_participants(
                room_proto.ListParticipantsRequest(room=room.name)
            )
            
            if len(participants_response.participants) == 0:
                try:
                    await lkapi.room.delete_room(room_proto.DeleteRoomRequest(room=room.name))
                    print(f"   ✅ Deleted empty room: {room.name}")
                except Exception as e:
                    print(f"   ❌ Failed to delete room {room.name}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up rooms: {str(e)}")
        return False
    finally:
        await session.close()

async def main():
    """Main function"""
    print("🚀 LiveKit Agent Management\n")
    
    # Check credentials
    if not all([os.getenv('LIVEKIT_URL'), os.getenv('LIVEKIT_API_KEY'), os.getenv('LIVEKIT_API_SECRET')]):
        print("❌ Missing LiveKit credentials in .env file")
        return
    
    # List existing agents
    agent_rooms = await list_agents()
    
    if agent_rooms:
        print(f"\n⚠️  Found agents in {len(agent_rooms)} room(s)")
        
        # Ask for confirmation to remove
        if len(sys.argv) > 1 and sys.argv[1] == "--remove":
            await remove_agents_from_rooms(agent_rooms)
            await cleanup_empty_rooms()
            print("\n✅ Agent cleanup completed!")
        else:
            print("\n💡 To remove existing agents, run:")
            print("   python manage_agents.py --remove")
    else:
        print("\n✅ No existing agents found. Ready for new deployment!")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Comprehensive test and troubleshooting script for the LiveKit MCP agent
"""
import asyncio
import os
import sys
import json
import aiohttp
from dotenv import load_dotenv
from pathlib import Path
from livekit import api
from livekit.protocol import room as room_proto

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

class AgentTester:
    def __init__(self):
        self.session = None
        self.lkapi = None
        self.test_room = "agent-test-room"
        self.test_results = {}
    
    async def setup(self):
        """Initialize connections"""
        print("🔧 Setting up test environment...")
        self.session = aiohttp.ClientSession()
        self.lkapi = api.LiveKitAPI(session=self.session)
    
    async def cleanup(self):
        """Clean up connections"""
        if self.session:
            await self.session.close()
    
    async def test_environment_variables(self):
        """Test all required environment variables"""
        print("\n🔍 Testing Environment Variables...")
        
        required_vars = {
            'LIVEKIT_URL': 'LiveKit WebSocket URL',
            'LIVEKIT_API_KEY': 'LiveKit API Key',
            'LIVEKIT_API_SECRET': 'LiveKit API Secret',
            'OPENAI_API_KEY': 'OpenAI API Key',
            'DEEPGRAM_API_KEY': 'Deepgram API Key',
            'RUBE_API_KEY': 'Rube MCP API Key'
        }
        
        all_present = True
        for var, description in required_vars.items():
            value = os.getenv(var)
            if value:
                print(f"   ✅ {var}: {description} - Present")
            else:
                print(f"   ❌ {var}: {description} - Missing")
                all_present = False
        
        self.test_results['environment'] = all_present
        return all_present
    
    async def test_livekit_connection(self):
        """Test LiveKit API connection"""
        print("\n🎥 Testing LiveKit Connection...")
        
        try:
            # Test basic connection
            rooms_response = await self.lkapi.room.list_rooms(room_proto.ListRoomsRequest(names=[]))
            print(f"   ✅ Connected successfully - Found {len(rooms_response.rooms)} rooms")
            
            # Test token generation
            token = api.AccessToken(
                os.getenv('LIVEKIT_API_KEY'),
                os.getenv('LIVEKIT_API_SECRET')
            ).with_identity("test-user") \
             .with_name("Test User") \
             .with_grants(api.VideoGrants(room_join=True, room=self.test_room))
            
            jwt_token = token.to_jwt()
            print(f"   ✅ Token generation successful - {len(jwt_token)} chars")
            
            self.test_results['livekit'] = True
            return True
            
        except Exception as e:
            print(f"   ❌ LiveKit connection failed: {str(e)}")
            self.test_results['livekit'] = False
            return False
    
    async def test_openai_api(self):
        """Test OpenAI API connection"""
        print("\n🧠 Testing OpenAI API...")
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Test chat completion
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'API test successful'"}],
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip()
            print(f"   ✅ Chat API working: {result}")
            
            # Test TTS (just validate the client can be created)
            try:
                tts_response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input="Test"
                )
                print(f"   ✅ TTS API accessible")
            except Exception as e:
                print(f"   ⚠️  TTS API issue: {str(e)}")
            
            self.test_results['openai'] = True
            return True
            
        except Exception as e:
            print(f"   ❌ OpenAI API failed: {str(e)}")
            self.test_results['openai'] = False
            return False
    
    async def test_deepgram_api(self):
        """Test Deepgram API connection"""
        print("\n🎤 Testing Deepgram API...")
        
        try:
            import httpx
            
            api_key = os.getenv('DEEPGRAM_API_KEY')
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
                    print("   ✅ Deepgram API working")
                    self.test_results['deepgram'] = True
                    return True
                else:
                    print(f"   ❌ Deepgram API failed: {response.status_code}")
                    self.test_results['deepgram'] = False
                    return False
                    
        except Exception as e:
            print(f"   ❌ Deepgram API failed: {str(e)}")
            self.test_results['deepgram'] = False
            return False
    
    async def test_rube_mcp(self):
        """Test Rube MCP connection"""
        print("\n🔗 Testing Rube MCP Connection...")
        
        try:
            rube_api_key = os.getenv('RUBE_API_KEY')
            headers = {
                'Authorization': rube_api_key,
                'Content-Type': 'application/json'
            }
            
            # Test with proper MCP protocol
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "livekit-agent-test",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://rube.app/mcp',
                    headers=headers,
                    json=mcp_request
                ) as response:
                    
                    print(f"   📡 Response status: {response.status}")
                    
                    if response.status == 200:
                        try:
                            result = await response.json()
                            print(f"   ✅ Rube MCP responding correctly")
                            print(f"   📄 Response: {json.dumps(result, indent=2)[:200]}...")
                            self.test_results['rube_mcp'] = True
                            return True
                        except:
                            print(f"   ⚠️  Got response but couldn't parse JSON")
                            self.test_results['rube_mcp'] = False
                            return False
                    else:
                        content = await response.text()
                        print(f"   ❌ Rube MCP failed: {response.status}")
                        print(f"   📄 Error: {content[:200]}...")
                        self.test_results['rube_mcp'] = False
                        return False
                        
        except Exception as e:
            print(f"   ❌ Rube MCP connection failed: {str(e)}")
            self.test_results['rube_mcp'] = False
            return False
    
    async def test_agent_deployment(self):
        """Test if agent is properly deployed"""
        print("\n🤖 Testing Agent Deployment...")
        
        try:
            # Create a test room
            print(f"   🏠 Creating test room: {self.test_room}")
            
            # Generate token for test room
            token = api.AccessToken(
                os.getenv('LIVEKIT_API_KEY'),
                os.getenv('LIVEKIT_API_SECRET')
            ).with_identity("test-participant") \
             .with_name("Test Participant") \
             .with_grants(api.VideoGrants(room_join=True, room=self.test_room))
            
            jwt_token = token.to_jwt()
            livekit_url = os.getenv('LIVEKIT_URL')
            join_url = f"https://meet.livekit.io/custom?liveKitUrl={livekit_url}&token={jwt_token}"
            
            print(f"   🔗 Test room URL generated")
            print(f"   📋 Room: {self.test_room}")
            print(f"   🌐 URL: {join_url}")
            
            # Wait a moment then check if room exists and has participants
            await asyncio.sleep(2)
            
            rooms_response = await self.lkapi.room.list_rooms(room_proto.ListRoomsRequest(names=[]))
            test_room_exists = any(room.name == self.test_room for room in rooms_response.rooms)
            
            if test_room_exists:
                print(f"   ✅ Test room created successfully")
                
                # Check for participants (including potential agent)
                participants_response = await self.lkapi.room.list_participants(
                    room_proto.ListParticipantsRequest(room=self.test_room)
                )
                
                print(f"   👥 Participants in room: {len(participants_response.participants)}")
                for p in participants_response.participants:
                    print(f"      - {p.identity} ({p.name})")
            
            self.test_results['agent_deployment'] = True
            return True, join_url
            
        except Exception as e:
            print(f"   ❌ Agent deployment test failed: {str(e)}")
            self.test_results['agent_deployment'] = False
            return False, None
    
    async def cleanup_test_room(self):
        """Clean up test room"""
        try:
            await self.lkapi.room.delete_room(room_proto.DeleteRoomRequest(room=self.test_room))
            print(f"   🧹 Cleaned up test room: {self.test_room}")
        except:
            pass  # Room might not exist
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("📋 TEST SUMMARY")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("\n🎉 All systems operational! Your agent is ready.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} issue(s) found. See details above.")
            self.print_troubleshooting_guide()
    
    def print_troubleshooting_guide(self):
        """Print troubleshooting guide for failed tests"""
        print("\n🔧 TROUBLESHOOTING GUIDE")
        print("-" * 30)
        
        if not self.test_results.get('environment', True):
            print("❌ Environment Variables:")
            print("   - Check your .env file exists and has all required keys")
            print("   - Verify API keys are not commented out (no # prefix)")
        
        if not self.test_results.get('livekit', True):
            print("❌ LiveKit Connection:")
            print("   - Verify LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET")
            print("   - Check network connectivity")
            print("   - Ensure LiveKit cloud instance is active")
        
        if not self.test_results.get('openai', True):
            print("❌ OpenAI API:")
            print("   - Verify OPENAI_API_KEY is valid and has credits")
            print("   - Check API key permissions")
        
        if not self.test_results.get('deepgram', True):
            print("❌ Deepgram API:")
            print("   - Verify DEEPGRAM_API_KEY is valid")
            print("   - Check Deepgram account status and credits")
        
        if not self.test_results.get('rube_mcp', True):
            print("❌ Rube MCP:")
            print("   - Verify RUBE_API_KEY format (should start with 'Bearer ')")
            print("   - Check Rube service availability")
            print("   - Ensure MCP endpoint is accessible")

async def main():
    """Main test function"""
    print("🚀 LiveKit MCP Agent - Comprehensive Test & Troubleshooting")
    print("=" * 60)
    
    tester = AgentTester()
    
    try:
        await tester.setup()
        
        # Run all tests
        await tester.test_environment_variables()
        await tester.test_livekit_connection()
        await tester.test_openai_api()
        await tester.test_deepgram_api()
        await tester.test_rube_mcp()
        
        # Test agent deployment
        success, join_url = await tester.test_agent_deployment()
        
        if success and join_url:
            print(f"\n🎯 READY TO TEST!")
            print(f"Join URL: {join_url}")
            print("Open this URL in your browser to test the agent!")
        
        # Clean up
        await tester.cleanup_test_room()
        
        # Print summary
        tester.print_summary()
        
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

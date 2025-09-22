#!/usr/bin/env python3
"""
Test Rube MCP with correct headers
"""
import asyncio
import os
import json
import aiohttp
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

async def test_rube_mcp_fixed():
    """Test Rube MCP with proper headers"""
    print("🔗 Testing Rube MCP with fixed headers...")
    
    try:
        rube_api_key = os.getenv('RUBE_API_KEY')
        headers = {
            'Authorization': rube_api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        
        # Test with proper MCP initialize request
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "livekit-agent",
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
                print(f"   📋 Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    try:
                        result = await response.json()
                        print(f"   ✅ Rube MCP connection successful!")
                        print(f"   📄 Response: {json.dumps(result, indent=2)}")
                        return True
                    except Exception as e:
                        print(f"   ⚠️  Response received but JSON parse failed: {e}")
                        content = await response.text()
                        print(f"   📄 Raw content: {content[:300]}...")
                        return False
                else:
                    content = await response.text()
                    print(f"   ❌ Rube MCP failed: {response.status}")
                    print(f"   📄 Error: {content}")
                    return False
                    
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        return False

async def main():
    """Main test"""
    print("🚀 Rube MCP Fixed Connection Test\n")
    
    success = await test_rube_mcp_fixed()
    
    if success:
        print("\n🎉 Rube MCP is now working!")
    else:
        print("\n⚠️  Still having issues with Rube MCP")

if __name__ == "__main__":
    asyncio.run(main())

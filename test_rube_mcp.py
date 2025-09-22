#!/usr/bin/env python3
"""
Test connection to Rube MCP server
"""
import asyncio
import os
import aiohttp
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

async def test_rube_mcp():
    """Test connection to Rube MCP server"""
    print("🔍 Testing Rube MCP connection...")
    
    rube_api_key = os.getenv('RUBE_API_KEY')
    if not rube_api_key:
        print("❌ RUBE_API_KEY not found in environment")
        return False
    
    print(f"🔑 API Key: {rube_api_key[:20]}...")
    
    try:
        headers = {
            'Authorization': rube_api_key,
            'Content-Type': 'application/json'
        }
        
        # Test basic connection to Rube MCP endpoint
        async with aiohttp.ClientSession() as session:
            # Try to get MCP server info or capabilities
            async with session.get('https://rube.app/mcp', headers=headers) as response:
                print(f"📡 Response status: {response.status}")
                
                if response.status == 200:
                    print("✅ Rube MCP connection successful!")
                    
                    # Try to get response content
                    try:
                        content = await response.text()
                        print(f"📄 Response preview: {content[:200]}...")
                    except:
                        print("📄 Response received (binary or large content)")
                    
                    return True
                elif response.status == 401:
                    print("❌ Authentication failed - check your API key")
                    return False
                elif response.status == 404:
                    print("❌ MCP endpoint not found")
                    return False
                else:
                    print(f"❌ Unexpected response: {response.status}")
                    try:
                        content = await response.text()
                        print(f"Error content: {content}")
                    except:
                        pass
                    return False
                    
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Rube MCP Connection Test\n")
    
    success = await test_rube_mcp()
    
    if success:
        print("\n🎉 Rube MCP is ready!")
        print("✅ You can now start the LiveKit agent")
    else:
        print("\n⚠️  Rube MCP connection failed")
        print("Please check your API key and network connection")

if __name__ == "__main__":
    asyncio.run(main())

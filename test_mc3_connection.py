#!/usr/bin/env python3
"""
Test script to verify MC3 MCP server connection
"""
import asyncio
import os
import logging
from dotenv import load_dotenv
from pathlib import Path
from livekit.agents import mcp

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mc3_connection():
    """Test connection to MC3 MCP server"""
    try:
        # Create MCP server connection
        mcp_server = mcp.MCPServerHTTP(
            url="https://mcp.hitsdifferent.ai/metamcp/mc3-server/mcp",
            headers={
                "Authorization": os.getenv('MC3_API_KEY'),
                "Accept": "application/json, text/event-stream"
            }
        )
        
        logger.info("🔌 Attempting to connect to MC3 MCP server...")
        
        # Initialize the server
        await mcp_server.initialize()
        
        logger.info("✅ Successfully connected to MC3 MCP server!")
        
        # List available tools
        logger.info("📋 Listing available tools...")
        tools = await mcp_server.list_tools()
        
        if tools:
            logger.info(f"🛠️  Found {len(tools)} available tools:")
            for i, tool in enumerate(tools[:10]):  # Show first 10 tools
                try:
                    name = getattr(tool, 'name', f'Tool_{i}')
                    description = getattr(tool, 'description', 'No description available')
                    logger.info(f"   - {name}: {description[:100]}...")
                except Exception as e:
                    logger.info(f"   - Tool {i}: {str(tool)[:100]}...")
        else:
            logger.warning("⚠️  No tools found")
            
        # Note: list_resources may not be available in this MCP server implementation
        logger.info("📚 Skipping resource listing (not available in this server)")
            
        logger.info("🎉 MC3 MCP server test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MC3 MCP server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_mc3_connection())

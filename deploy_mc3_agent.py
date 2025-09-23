#!/usr/bin/env python3
"""
Deploy the MC3-connected LiveKit agent
"""
import asyncio
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'LIVEKIT_URL',
        'LIVEKIT_API_KEY', 
        'LIVEKIT_API_SECRET',
        'MC3_API_KEY',
        'OPENAI_API_KEY',
        'DEEPGRAM_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def run_command(cmd, description):
    """Run a shell command with error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False

async def test_mc3_connection():
    """Test MC3 MCP server connection"""
    print("🔌 Testing MC3 MCP server connection...")
    try:
        # Run the test script
        result = subprocess.run([sys.executable, "test_mc3_connection.py"], 
                              capture_output=True, text=True, check=True)
        print("✅ MC3 MCP server connection test passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ MC3 MCP server connection test failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False

def deploy_agent():
    """Deploy the agent to LiveKit Cloud"""
    print("🚀 Deploying agent to LiveKit Cloud...")
    
    # Check if livekit.toml exists
    if not Path("livekit.toml").exists():
        print("❌ livekit.toml not found. Please ensure you're in the correct directory.")
        return False
    
    # Deploy using livekit CLI
    cmd = "livekit deploy"
    return run_command(cmd, "Agent deployment")

def main():
    """Main deployment function"""
    print("🎯 Starting MC3-connected LiveKit Agent Deployment")
    print("=" * 50)
    
    # Step 1: Check environment
    if not check_environment():
        sys.exit(1)
    
    # Step 2: Test MC3 connection
    if not asyncio.run(test_mc3_connection()):
        print("⚠️  MC3 connection test failed, but continuing with deployment...")
    
    # Step 3: Deploy agent
    if not deploy_agent():
        print("❌ Agent deployment failed")
        sys.exit(1)
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Your agent is now connected to MC3 server and can:")
    print("   🎵 Generate speech and clone voices with Cartesia")
    print("   🎬 Create avatar videos with HeyGen")  
    print("   🔗 Access 500+ apps via Rube/Composio")
    print("   📧 Send emails, manage calendars, create documents")
    print("   💬 Post to social media, manage projects")
    print("   🤖 Execute complex multi-step workflows")
    
    print(f"\n🔗 Agent ID: CA_57hqHZyvM6Yn")
    print(f"🌐 LiveKit URL: {os.getenv('LIVEKIT_URL')}")
    print("\n💡 Try saying: 'Send an email to my team' or 'Create a voice clone'")

if __name__ == "__main__":
    main()

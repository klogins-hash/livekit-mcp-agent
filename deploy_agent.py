#!/usr/bin/env python3
"""
Deploy the LiveKit MCP agent
"""
import asyncio
import os
import subprocess
import signal
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

class AgentDeployer:
    def __init__(self):
        self.mcp_server_process = None
        self.agent_process = None
    
    def start_mcp_server(self):
        """Start the MCP server in the background"""
        print("🚀 Starting MCP server...")
        
        try:
            # Start MCP server
            self.mcp_server_process = subprocess.Popen(
                [sys.executable, "server.py"],
                cwd=Path(__file__).parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            import time
            time.sleep(2)
            
            # Check if it's still running
            if self.mcp_server_process.poll() is None:
                print("✅ MCP server started successfully!")
                return True
            else:
                stdout, stderr = self.mcp_server_process.communicate()
                print(f"❌ MCP server failed to start:")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start MCP server: {str(e)}")
            return False
    
    def start_agent(self):
        """Start the LiveKit agent"""
        print("🤖 Starting LiveKit agent...")
        
        try:
            # Start the agent
            self.agent_process = subprocess.Popen(
                [sys.executable, "agent.py"],
                cwd=Path(__file__).parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print("✅ LiveKit agent started!")
            print("📡 Agent is now running and waiting for connections...")
            print("🔗 Connect to your LiveKit room to interact with the agent")
            
            # Monitor the agent output
            try:
                for line in iter(self.agent_process.stdout.readline, ''):
                    if line:
                        print(f"[AGENT] {line.strip()}")
                    
                    # Check if process is still running
                    if self.agent_process.poll() is not None:
                        break
                        
            except KeyboardInterrupt:
                print("\n🛑 Shutting down agent...")
                self.cleanup()
                
        except Exception as e:
            print(f"❌ Failed to start agent: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up processes"""
        print("🧹 Cleaning up processes...")
        
        if self.agent_process:
            try:
                self.agent_process.terminate()
                self.agent_process.wait(timeout=5)
                print("✅ Agent process terminated")
            except:
                self.agent_process.kill()
                print("🔨 Agent process killed")
        
        if self.mcp_server_process:
            try:
                self.mcp_server_process.terminate()
                self.mcp_server_process.wait(timeout=5)
                print("✅ MCP server process terminated")
            except:
                self.mcp_server_process.kill()
                print("🔨 MCP server process killed")
    
    def deploy(self):
        """Deploy both MCP server and agent"""
        print("🚀 Deploying LiveKit MCP Agent\n")
        
        # Verify environment
        required_vars = ['LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'OPENAI_API_KEY', 'DEEPGRAM_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        print(f"🔗 LiveKit URL: {os.getenv('LIVEKIT_URL')}")
        print(f"🔑 API Keys configured: ✅")
        print()
        
        # Start MCP server
        if not self.start_mcp_server():
            return False
        
        print()
        
        # Start agent
        self.start_agent()
        
        return True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Received interrupt signal...")
    sys.exit(0)

def main():
    """Main deployment function"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    deployer = AgentDeployer()
    
    try:
        deployer.deploy()
    except KeyboardInterrupt:
        print("\n🛑 Deployment interrupted")
    finally:
        deployer.cleanup()

if __name__ == "__main__":
    main()

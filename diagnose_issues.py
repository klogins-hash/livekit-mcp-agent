#!/usr/bin/env python3
"""
Diagnostic script to identify performance and connection issues
"""
import asyncio
import time
import os
import sys
import requests
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / '.env')

class AgentDiagnostics:
    def __init__(self):
        self.results = {}
    
    def print_header(self, title):
        print(f"\n{'='*50}")
        print(f"🔍 {title}")
        print('='*50)
    
    def print_result(self, test_name, success, details="", duration=None):
        status = "✅" if success else "❌"
        duration_str = f" ({duration:.2f}s)" if duration else ""
        print(f"{status} {test_name}{duration_str}")
        if details:
            print(f"   {details}")
        self.results[test_name] = {"success": success, "details": details, "duration": duration}
    
    def test_environment_variables(self):
        """Test if all required environment variables are set"""
        self.print_header("Environment Variables")
        
        required_vars = [
            'LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET',
            'MC3_API_KEY', 'OPENAI_API_KEY', 'DEEPGRAM_API_KEY'
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                masked_value = value[:10] + "..." if len(value) > 10 else value
                self.print_result(var, True, f"Set: {masked_value}")
            else:
                self.print_result(var, False, "Not set")
    
    def test_network_connectivity(self):
        """Test network connectivity to various services"""
        self.print_header("Network Connectivity")
        
        endpoints = [
            ("LiveKit Cloud", os.getenv('LIVEKIT_URL', '').replace('wss://', 'https://')),
            ("MC3 MCP Server", "https://mcp.hitsdifferent.ai"),
            ("OpenAI API", "https://api.openai.com"),
            ("Deepgram API", "https://api.deepgram.com"),
        ]
        
        for name, url in endpoints:
            if not url or url == "https://":
                self.print_result(name, False, "URL not configured")
                continue
                
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                duration = time.time() - start_time
                
                if response.status_code < 500:  # Accept 4xx as "reachable"
                    self.print_result(name, True, f"Status: {response.status_code}", duration)
                else:
                    self.print_result(name, False, f"Status: {response.status_code}", duration)
            except requests.exceptions.Timeout:
                self.print_result(name, False, "Connection timeout")
            except Exception as e:
                self.print_result(name, False, f"Error: {str(e)[:50]}")
    
    async def test_mcp_connection(self):
        """Test MCP server connection specifically"""
        self.print_header("MCP Server Connection")
        
        mc3_api_key = os.getenv('MC3_API_KEY')
        if not mc3_api_key:
            self.print_result("MC3 API Key", False, "Not configured")
            return
        
        try:
            start_time = time.time()
            
            # Test basic HTTP connection
            headers = {
                "Authorization": mc3_api_key,
                "Accept": "application/json, text/event-stream",
                "User-Agent": "LiveKit-MCP-Agent-Diagnostics/1.0"
            }
            
            response = requests.post(
                "https://mcp.hitsdifferent.ai/metamcp/mc3-server/mcp",
                headers=headers,
                json={"jsonrpc": "2.0", "method": "initialize", "id": 1},
                timeout=15
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.print_result("MCP HTTP Connection", True, "Connected successfully", duration)
                
                # Try to parse response
                try:
                    data = response.json()
                    if "result" in data:
                        self.print_result("MCP Initialize", True, "Server responded correctly")
                    else:
                        self.print_result("MCP Initialize", False, f"Unexpected response: {data}")
                except:
                    self.print_result("MCP Initialize", False, "Invalid JSON response")
                    
            else:
                self.print_result("MCP HTTP Connection", False, f"Status: {response.status_code}", duration)
                
        except requests.exceptions.Timeout:
            self.print_result("MCP Connection", False, "Connection timeout (>15s)")
        except Exception as e:
            self.print_result("MCP Connection", False, f"Error: {str(e)}")
    
    def test_system_resources(self):
        """Test system resources and performance"""
        self.print_header("System Resources")
        
        try:
            # CPU usage
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            self.print_result("CPU Usage", cpu_percent < 80, f"{cpu_percent}%")
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.print_result("Memory Usage", memory_percent < 80, f"{memory_percent}%")
            
            # Disk space
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.print_result("Disk Space", disk_percent < 90, f"{disk_percent:.1f}% used")
            
        except ImportError:
            self.print_result("System Resources", False, "psutil not installed (pip install psutil)")
        except Exception as e:
            self.print_result("System Resources", False, f"Error: {str(e)}")
    
    def test_python_dependencies(self):
        """Test Python dependencies"""
        self.print_header("Python Dependencies")
        
        dependencies = [
            'livekit-agents', 'openai', 'deepgram-sdk', 
            'python-dotenv', 'asyncio', 'aiohttp'
        ]
        
        for dep in dependencies:
            try:
                __import__(dep.replace('-', '_'))
                self.print_result(dep, True, "Installed")
            except ImportError:
                self.print_result(dep, False, "Not installed")
    
    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        self.print_header("Recommendations")
        
        failed_tests = [name for name, result in self.results.items() if not result["success"]]
        
        if not failed_tests:
            print("🎉 All tests passed! Your agent should work optimally.")
            return
        
        print("🔧 Issues found. Here are recommendations:")
        
        # Environment variable issues
        env_failures = [name for name in failed_tests if name in ['LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'MC3_API_KEY', 'OPENAI_API_KEY', 'DEEPGRAM_API_KEY']]
        if env_failures:
            print(f"\n📝 Missing environment variables: {', '.join(env_failures)}")
            print("   → Check your .env file and ensure all keys are properly set")
        
        # Network issues
        network_failures = [name for name in failed_tests if "Connection" in name or "API" in name]
        if network_failures:
            print(f"\n🌐 Network connectivity issues: {', '.join(network_failures)}")
            print("   → Check your internet connection and firewall settings")
            print("   → Try using agent_fast.py for local-only operation")
        
        # MCP specific issues
        if "MCP Connection" in failed_tests:
            print(f"\n🔌 MCP server issues detected")
            print("   → Verify MC3_API_KEY is correct and includes 'Bearer ' prefix")
            print("   → Try running: python test_mc3_connection.py")
            print("   → Consider using agent_fast.py without MCP for testing")
        
        # Performance issues
        slow_tests = [name for name, result in self.results.items() 
                     if result.get("duration") and result.get("duration", 0) > 5.0]
        if slow_tests:
            print(f"\n⚡ Slow connections detected: {', '.join(slow_tests)}")
            print("   → Use agent_fast.py for better performance")
            print("   → Consider local MCP server deployment")
        
        # System resource issues
        resource_failures = [name for name in failed_tests if name in ['CPU Usage', 'Memory Usage', 'Disk Space']]
        if resource_failures:
            print(f"\n💻 System resource issues: {', '.join(resource_failures)}")
            print("   → Close other applications to free up resources")
            print("   → Use lighter agent configuration")

async def main():
    """Run all diagnostic tests"""
    print("🔍 LiveKit MCP Agent Diagnostics")
    print("This will help identify performance and connection issues")
    
    diagnostics = AgentDiagnostics()
    
    # Run all tests
    diagnostics.test_environment_variables()
    diagnostics.test_network_connectivity()
    await diagnostics.test_mcp_connection()
    diagnostics.test_system_resources()
    diagnostics.test_python_dependencies()
    
    # Generate recommendations
    diagnostics.generate_recommendations()
    
    print(f"\n{'='*50}")
    print("🎯 Quick Fixes:")
    print("1. For maximum speed: python agent_fast.py dev")
    print("2. For MCP issues: python test_mc3_connection.py")
    print("3. For setup help: cat PERFORMANCE_OPTIMIZATION.md")
    print('='*50)

if __name__ == "__main__":
    asyncio.run(main())

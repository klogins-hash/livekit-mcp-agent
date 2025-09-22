#!/usr/bin/env python3
"""
Deploy LiveKit MCP Agent to Railway
"""
import os
import subprocess
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not installed")
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("📦 Installing Railway CLI...")
    try:
        # Install via npm
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("✅ Railway CLI installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Railway CLI via npm")
        try:
            # Try homebrew on macOS
            subprocess.run(['brew', 'install', 'railway'], check=True)
            print("✅ Railway CLI installed via Homebrew")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Railway CLI")
            print("💡 Please install manually: https://docs.railway.app/develop/cli")
            return False

def railway_login():
    """Login to Railway"""
    print("🔐 Logging into Railway...")
    try:
        subprocess.run(['railway', 'login'], check=True)
        print("✅ Successfully logged into Railway")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to login to Railway")
        return False

def create_railway_project():
    """Create Railway project"""
    print("🚀 Creating Railway project...")
    try:
        # Initialize Railway project
        result = subprocess.run(['railway', 'init'], capture_output=True, text=True, input='livekit-mcp-agent\n')
        if result.returncode == 0:
            print("✅ Railway project created")
            return True
        else:
            print(f"❌ Failed to create Railway project: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating Railway project: {e}")
        return False

def set_environment_variables():
    """Set environment variables in Railway"""
    print("🔧 Setting environment variables...")
    
    env_vars = {
        'LIVEKIT_URL': os.getenv('LIVEKIT_URL'),
        'LIVEKIT_API_KEY': os.getenv('LIVEKIT_API_KEY'),
        'LIVEKIT_API_SECRET': os.getenv('LIVEKIT_API_SECRET'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'DEEPGRAM_API_KEY': os.getenv('DEEPGRAM_API_KEY'),
        'RUBE_API_KEY': os.getenv('RUBE_API_KEY')
    }
    
    success = True
    for key, value in env_vars.items():
        if value:
            try:
                subprocess.run(['railway', 'variables', 'set', f'{key}={value}'], check=True)
                print(f"   ✅ Set {key}")
            except subprocess.CalledProcessError:
                print(f"   ❌ Failed to set {key}")
                success = False
        else:
            print(f"   ⚠️  {key} not found in .env file")
            success = False
    
    return success

def deploy_to_railway():
    """Deploy the application to Railway"""
    print("🚀 Deploying to Railway...")
    try:
        subprocess.run(['railway', 'up'], check=True)
        print("✅ Successfully deployed to Railway!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to deploy to Railway")
        return False

def get_deployment_info():
    """Get deployment information"""
    print("📊 Getting deployment information...")
    try:
        # Get project info
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Deployment Status:")
            print(result.stdout)
        
        # Get domain
        result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
        if result.returncode == 0:
            print("🌐 Domain Information:")
            print(result.stdout)
            
    except subprocess.CalledProcessError:
        print("⚠️  Could not get deployment info")

def main():
    """Main deployment function"""
    print("🚀 LiveKit MCP Agent - Railway Deployment")
    print("=" * 50)
    
    # Check if Railway CLI is available
    if not check_railway_cli():
        if not install_railway_cli():
            print("❌ Cannot proceed without Railway CLI")
            sys.exit(1)
    
    # Login to Railway
    if not railway_login():
        print("❌ Cannot proceed without Railway login")
        sys.exit(1)
    
    # Create project
    if not create_railway_project():
        print("❌ Failed to create Railway project")
        sys.exit(1)
    
    # Set environment variables
    if not set_environment_variables():
        print("⚠️  Some environment variables failed to set")
        print("You may need to set them manually in Railway dashboard")
    
    # Deploy
    if deploy_to_railway():
        print("\n🎉 Deployment Successful!")
        get_deployment_info()
        
        print("\n📋 Next Steps:")
        print("1. Check Railway dashboard for deployment status")
        print("2. Monitor logs: railway logs")
        print("3. Your agent is now running in the cloud!")
        print("4. Test with your LiveKit rooms")
        
    else:
        print("\n❌ Deployment failed")
        print("Check Railway dashboard for error details")

if __name__ == "__main__":
    main()

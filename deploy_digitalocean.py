#!/usr/bin/env python3
"""
Deploy LiveKit MCP Agent to DigitalOcean App Platform
"""
import os
import subprocess
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

class DigitalOceanDeployer:
    def __init__(self):
        self.app_name = "livekit-mcp-agent"
        self.github_repo = "klogins-hash/livekit-mcp-agent"
    
    def check_doctl(self):
        """Check if DigitalOcean CLI is installed"""
        try:
            result = subprocess.run(['doctl', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ DigitalOcean CLI found: {result.stdout.strip()}")
                return True
            else:
                return False
        except FileNotFoundError:
            return False
    
    def install_doctl(self):
        """Install DigitalOcean CLI"""
        print("📦 Installing DigitalOcean CLI...")
        try:
            # Try homebrew on macOS
            subprocess.run(['brew', 'install', 'doctl'], check=True)
            print("✅ DigitalOcean CLI installed via Homebrew")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install DigitalOcean CLI via Homebrew")
            print("💡 Please install manually: https://docs.digitalocean.com/reference/doctl/how-to/install/")
            return False
    
    def authenticate(self):
        """Authenticate with DigitalOcean"""
        print("🔐 Authenticating with DigitalOcean...")
        print("Please get your API token from: https://cloud.digitalocean.com/account/api/tokens")
        
        try:
            subprocess.run(['doctl', 'auth', 'init'], check=True)
            print("✅ Successfully authenticated with DigitalOcean")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to authenticate with DigitalOcean")
            return False
    
    def create_app(self):
        """Create DigitalOcean App"""
        print(f"🚀 Creating DigitalOcean App: {self.app_name}")
        
        app_spec = {
            "name": self.app_name,
            "services": [{
                "name": "agent",
                "source_dir": "/",
                "github": {
                    "repo": self.github_repo,
                    "branch": "main",
                    "deploy_on_push": True
                },
                "dockerfile_path": "Dockerfile",
                "instance_count": 1,
                "instance_size_slug": "basic-xxs",
                "health_check": {
                    "http_path": "/health",
                    "initial_delay_seconds": 60,
                    "period_seconds": 30,
                    "timeout_seconds": 10,
                    "failure_threshold": 3,
                    "success_threshold": 1
                },
                "envs": [
                    {"key": "LIVEKIT_URL", "scope": "RUN_TIME", "type": "SECRET"},
                    {"key": "LIVEKIT_API_KEY", "scope": "RUN_TIME", "type": "SECRET"},
                    {"key": "LIVEKIT_API_SECRET", "scope": "RUN_TIME", "type": "SECRET"},
                    {"key": "OPENAI_API_KEY", "scope": "RUN_TIME", "type": "SECRET"},
                    {"key": "DEEPGRAM_API_KEY", "scope": "RUN_TIME", "type": "SECRET"},
                    {"key": "CARTESIA_API_KEY", "scope": "RUN_TIME", "type": "SECRET"},
                    {"key": "RUBE_API_KEY", "scope": "RUN_TIME", "type": "SECRET"}
                ]
            }]
        }
        
        # Write app spec to temporary file
        spec_file = Path(__file__).parent / "do-app-spec.json"
        with open(spec_file, 'w') as f:
            json.dump(app_spec, f, indent=2)
        
        try:
            # Create the app
            result = subprocess.run([
                'doctl', 'apps', 'create', '--spec', str(spec_file)
            ], capture_output=True, text=True, check=True)
            
            print("✅ App created successfully!")
            print(f"📄 Output: {result.stdout}")
            
            # Clean up spec file
            spec_file.unlink()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create app: {e.stderr}")
            spec_file.unlink()
            return False
    
    def set_environment_variables(self, app_id):
        """Set environment variables for the app"""
        print("🔧 Setting environment variables...")
        
        env_vars = {
            'LIVEKIT_URL': os.getenv('LIVEKIT_URL'),
            'LIVEKIT_API_KEY': os.getenv('LIVEKIT_API_KEY'),
            'LIVEKIT_API_SECRET': os.getenv('LIVEKIT_API_SECRET'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'DEEPGRAM_API_KEY': os.getenv('DEEPGRAM_API_KEY'),
            'CARTESIA_API_KEY': os.getenv('CARTESIA_API_KEY'),
            'RUBE_API_KEY': os.getenv('RUBE_API_KEY')
        }
        
        success = True
        for key, value in env_vars.items():
            if value:
                try:
                    subprocess.run([
                        'doctl', 'apps', 'update', app_id,
                        '--spec', '-'
                    ], input=json.dumps({
                        "envs": [{"key": key, "value": value, "scope": "RUN_TIME", "type": "SECRET"}]
                    }), text=True, check=True)
                    print(f"   ✅ Set {key}")
                except subprocess.CalledProcessError:
                    print(f"   ❌ Failed to set {key}")
                    success = False
            else:
                print(f"   ⚠️  {key} not found in .env file")
                success = False
        
        return success
    
    def get_app_info(self):
        """Get information about deployed apps"""
        print("📊 Getting app information...")
        try:
            result = subprocess.run(['doctl', 'apps', 'list'], capture_output=True, text=True, check=True)
            print("✅ Your DigitalOcean Apps:")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to get app information")
            return False
    
    def deploy_via_yaml(self):
        """Deploy using the app.yaml file"""
        print("🚀 Deploying via app.yaml...")
        
        app_yaml = Path(__file__).parent / ".do" / "app.yaml"
        if not app_yaml.exists():
            print("❌ app.yaml not found")
            return False
        
        try:
            result = subprocess.run([
                'doctl', 'apps', 'create', '--spec', str(app_yaml)
            ], capture_output=True, text=True, check=True)
            
            print("✅ App deployed successfully!")
            print(f"📄 Output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e.stderr}")
            return False

def main():
    """Main deployment function"""
    print("🚀 DigitalOcean App Platform Deployment")
    print("=" * 50)
    
    deployer = DigitalOceanDeployer()
    
    # Check if doctl is installed
    if not deployer.check_doctl():
        print("📦 DigitalOcean CLI not found")
        if not deployer.install_doctl():
            print("❌ Cannot proceed without DigitalOcean CLI")
            sys.exit(1)
    
    # Authenticate
    if not deployer.authenticate():
        print("❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Deploy the app
    print("\n🎯 Choose deployment method:")
    print("1. Deploy via app.yaml (recommended)")
    print("2. Deploy via Python script")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        if deployer.deploy_via_yaml():
            print("\n🎉 Deployment initiated!")
            print("📊 Check status with: doctl apps list")
            print("📋 View logs with: doctl apps logs <app-id>")
            print("🌐 Your app will be available at: https://<app-name>-<random>.ondigitalocean.app")
        else:
            print("\n❌ Deployment failed")
    
    elif choice == "2":
        if deployer.create_app():
            print("\n🎉 App created!")
            print("⚠️  You'll need to set environment variables manually in the DO dashboard")
            print("🌐 Visit: https://cloud.digitalocean.com/apps")
        else:
            print("\n❌ App creation failed")
    
    else:
        print("❌ Invalid choice")
    
    # Show app info
    deployer.get_app_info()

if __name__ == "__main__":
    main()

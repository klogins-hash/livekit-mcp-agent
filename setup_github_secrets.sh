#!/bin/bash

# GitHub Secrets Setup Helper Script
# This script helps you set up GitHub repository secrets for auto-deployment

set -e

echo "🔧 GitHub Secrets Setup for LiveKit MCP Agent Auto-Deployment"
echo "============================================================="
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "📦 Install it with: brew install gh"
    echo "🔗 Or visit: https://cli.github.com/"
    echo ""
    echo "💡 Alternative: Set secrets manually in GitHub web interface:"
    echo "   Go to: Settings → Secrets and variables → Actions"
    exit 1
fi

# Check if user is logged in to GitHub CLI
if ! gh auth status &> /dev/null; then
    echo "🔐 Please log in to GitHub CLI first:"
    echo "   gh auth login"
    exit 1
fi

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "📄 Loading environment variables from .env file..."
    source .env
else
    echo "❌ .env file not found. Please ensure you're in the correct directory."
    exit 1
fi

# Function to set a GitHub secret
set_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if [ -z "$secret_value" ]; then
        echo "⚠️  Warning: $secret_name is empty or not set in .env file"
        return 1
    fi
    
    echo "🔑 Setting secret: $secret_name"
    echo "$secret_value" | gh secret set "$secret_name"
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully set $secret_name"
    else
        echo "❌ Failed to set $secret_name"
        return 1
    fi
}

echo "🚀 Setting up GitHub repository secrets..."
echo ""

# Required secrets
echo "📋 Setting required secrets:"
set_secret "LIVEKIT_URL" "$LIVEKIT_URL"
set_secret "LIVEKIT_API_KEY" "$LIVEKIT_API_KEY"
set_secret "LIVEKIT_API_SECRET" "$LIVEKIT_API_SECRET"
set_secret "MC3_API_KEY" "$MC3_API_KEY"
set_secret "OPENAI_API_KEY" "$OPENAI_API_KEY"
set_secret "DEEPGRAM_API_KEY" "$DEEPGRAM_API_KEY"
set_secret "CARTESIA_API_KEY" "$CARTESIA_API_KEY"

echo ""
echo "📋 Setting optional secrets:"
set_secret "RUBE_API_KEY" "$RUBE_API_KEY" || echo "ℹ️  RUBE_API_KEY not set (optional)"

echo ""
echo "🎉 GitHub secrets setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Commit and push your changes to trigger auto-deployment"
echo "2. Go to GitHub Actions tab to monitor deployment"
echo "3. Check the GITHUB_ACTIONS_SETUP.md file for troubleshooting"
echo ""
echo "🔗 GitHub Actions: https://github.com/$(gh repo view --json owner,name -q '.owner.login + \"/\" + .name')/actions"
echo ""
echo "🚀 Test auto-deployment with:"
echo "   git add ."
echo "   git commit -m 'feat: enable auto-deployment'"
echo "   git push origin main"

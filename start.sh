#!/bin/bash
set -e

echo "🚀 Starting LiveKit MCP Agent on DigitalOcean..."

# Check if all required environment variables are set
echo "🔍 Checking environment variables..."
required_vars=("LIVEKIT_URL" "LIVEKIT_API_KEY" "LIVEKIT_API_SECRET" "OPENAI_API_KEY" "DEEPGRAM_API_KEY" "RUBE_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required environment variable: $var"
        exit 1
    else
        echo "✅ $var is set"
    fi
done

# Start health check server in background
echo "📊 Starting health check server on port 8080..."
python health_check.py &
HEALTH_PID=$!

# Wait for health server to start
sleep 5
echo "✅ Health check server started (PID: $HEALTH_PID)"

# Start the main agent in background
echo "🤖 Starting LiveKit agent..."
python agent.py start &
AGENT_PID=$!

echo "✅ Agent started (PID: $AGENT_PID)"

# Keep the container running by monitoring both processes
while true; do
    if ! kill -0 $HEALTH_PID 2>/dev/null; then
        echo "❌ Health server died, restarting..."
        python health_check.py &
        HEALTH_PID=$!
    fi
    
    if ! kill -0 $AGENT_PID 2>/dev/null; then
        echo "❌ Agent died, restarting..."
        python agent.py start &
        AGENT_PID=$!
    fi
    
    sleep 30
done

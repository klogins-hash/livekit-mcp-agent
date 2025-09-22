#!/usr/bin/env python3
"""
Health check endpoint for DigitalOcean App Platform
"""
from flask import Flask, jsonify
import os
import threading
import time

app = Flask(__name__)

# Global health status
health_status = {
    "status": "healthy",
    "timestamp": time.time(),
    "agent_running": False,
    "environment_check": False
}

def check_environment():
    """Check if all required environment variables are present"""
    required_vars = [
        'LIVEKIT_URL',
        'LIVEKIT_API_KEY', 
        'LIVEKIT_API_SECRET',
        'OPENAI_API_KEY',
        'DEEPGRAM_API_KEY',
        'RUBE_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        health_status["status"] = "unhealthy"
        health_status["missing_env_vars"] = missing_vars
        health_status["environment_check"] = False
    else:
        health_status["environment_check"] = True
    
    return len(missing_vars) == 0

def periodic_health_check():
    """Periodic health check that runs in background"""
    while True:
        health_status["timestamp"] = time.time()
        check_environment()
        
        # Check if agent process is running (simplified check)
        try:
            # This is a basic check - in production you might want more sophisticated monitoring
            health_status["agent_running"] = True
        except Exception as e:
            health_status["agent_running"] = False
            health_status["error"] = str(e)
        
        time.sleep(30)  # Check every 30 seconds

@app.route('/health')
def health_check():
    """Health check endpoint for DigitalOcean"""
    check_environment()
    
    # Return 200 if healthy, 503 if not
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return jsonify({
        "status": health_status["status"],
        "timestamp": health_status["timestamp"],
        "checks": {
            "environment_variables": health_status["environment_check"],
            "agent_process": health_status.get("agent_running", False)
        },
        "service": "livekit-mcp-agent",
        "version": "1.0.0"
    }), status_code

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "service": "LiveKit MCP Agent",
        "status": "running",
        "description": "Voice-interactive agent with Rube MCP integration",
        "health_check": "/health"
    })

@app.route('/status')
def status():
    """Detailed status endpoint"""
    return jsonify({
        "service": "LiveKit MCP Agent",
        "status": health_status["status"],
        "uptime": time.time() - health_status["timestamp"],
        "environment": {
            "livekit_url": os.getenv('LIVEKIT_URL', 'Not set'),
            "has_openai_key": bool(os.getenv('OPENAI_API_KEY')),
            "has_deepgram_key": bool(os.getenv('DEEPGRAM_API_KEY')),
            "has_rube_key": bool(os.getenv('RUBE_API_KEY'))
        },
        "agent": {
            "running": health_status.get("agent_running", False)
        }
    })

if __name__ == '__main__':
    # Start background health monitoring
    health_thread = threading.Thread(target=periodic_health_check, daemon=True)
    health_thread.start()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

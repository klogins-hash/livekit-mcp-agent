# DigitalOcean App Platform Deployment Guide

Deploy your LiveKit MCP Agent to DigitalOcean App Platform for production use.

## 🚀 Why DigitalOcean App Platform?

✅ **Zero Server Management** - No OS updates, security patches, or server maintenance  
✅ **Automatic Scaling** - Handles traffic spikes automatically  
✅ **GitHub Integration** - Deploy on every push  
✅ **Built-in Load Balancing** - High availability out of the box  
✅ **Secure Secrets Management** - Environment variables encrypted at rest  
✅ **Cost Effective** - Starting at $5/month with auto-scaling  

## 📋 Prerequisites

1. **DigitalOcean Account**: [Sign up here](https://cloud.digitalocean.com/)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **API Keys**: All your service API keys ready
4. **DigitalOcean CLI**: We'll install this during setup

## ⚡ Quick Deploy (Automated)

### Option 1: One-Click Deploy

```bash
# Run the automated deployment script
python deploy_digitalocean.py
```

This script will:
- Install DigitalOcean CLI if needed
- Authenticate with your DO account
- Create the app with proper configuration
- Set up health checks and auto-scaling

### Option 2: Manual Deploy via Dashboard

1. **Go to DigitalOcean Dashboard**
   - Visit: https://cloud.digitalocean.com/apps
   - Click "Create App"

2. **Connect GitHub Repository**
   - Select "GitHub" as source
   - Choose repository: `klogins-hash/livekit-mcp-agent`
   - Branch: `main`
   - Auto-deploy: ✅ Enabled

3. **Configure Build Settings**
   - Build Command: `(auto-detected from Dockerfile)`
   - Run Command: `/app/start.sh`
   - Dockerfile Path: `Dockerfile`

4. **Set Environment Variables**
   ```
   LIVEKIT_URL=wss://your-instance.livekit.cloud
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   OPENAI_API_KEY=sk-your_openai_key
   DEEPGRAM_API_KEY=your_deepgram_key
   CARTESIA_API_KEY=sk_car_your_cartesia_key
   RUBE_API_KEY=Bearer your_rube_token
   ```
   
   **Note**: Use your actual API keys from the `.env` file

5. **Configure Resources**
   - Plan: Basic ($5/month)
   - Instance Size: Basic XXS (512MB RAM, 1 vCPU)
   - Auto-scaling: 1-3 instances

6. **Deploy**
   - Click "Create Resources"
   - Wait for build and deployment (5-10 minutes)

## 🔧 Configuration Details

### App Specification (`.do/app.yaml`)

```yaml
name: livekit-mcp-agent
services:
- name: agent
  dockerfile_path: Dockerfile
  instance_count: 1
  instance_size_slug: basic-xxs
  health_check:
    http_path: /health
    initial_delay_seconds: 60
  autoscaling:
    min_instance_count: 1
    max_instance_count: 3
```

### Health Check Endpoint

The app includes a health check at `/health` that monitors:
- Environment variables presence
- Agent process status
- Service availability

### Auto-Scaling

Configured to scale 1-3 instances based on:
- CPU utilization (target: 70%)
- Memory usage
- Request volume

## 📊 Monitoring & Management

### View App Status
```bash
doctl apps list
doctl apps get <app-id>
```

### View Logs
```bash
doctl apps logs <app-id> --follow
```

### Update App
```bash
# Push to GitHub - auto-deploys
git push origin main

# Or manual update
doctl apps update <app-id> --spec .do/app.yaml
```

### Scale App
```bash
doctl apps update <app-id> --spec .do/app.yaml
```

## 🌐 Access Your Deployed Agent

After deployment, your agent will be available at:
```
https://livekit-mcp-agent-<random>.ondigitalocean.app
```

### Health Check
```
https://your-app-url.ondigitalocean.app/health
```

### Status Page
```
https://your-app-url.ondigitalocean.app/status
```

## 🎯 Testing the Deployed Agent

1. **Create Test Room**
   ```bash
   python create_test_room.py
   ```

2. **Use Agent Playground**
   - Your agent will be accessible from any LiveKit room
   - Use the same credentials as before
   - Agent will auto-join when participants connect

3. **Monitor Performance**
   - Check DigitalOcean dashboard for metrics
   - View logs for any issues
   - Monitor auto-scaling behavior

## 💰 Cost Breakdown

| Resource | Cost | Description |
|----------|------|-------------|
| Basic XXS | $5/month | 512MB RAM, 1 vCPU |
| Bandwidth | $0.01/GB | Outbound data transfer |
| Build Minutes | Free | 400 minutes/month included |

**Estimated Monthly Cost: $5-12** (depending on usage)

## 🔒 Security Features

✅ **Encrypted Environment Variables** - All secrets encrypted at rest  
✅ **HTTPS by Default** - SSL/TLS termination included  
✅ **Private Networking** - Isolated from other apps  
✅ **Automatic Security Updates** - Platform managed  
✅ **DDoS Protection** - Built-in protection  

## 🚨 Troubleshooting

### Build Failures
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Check build logs in DO dashboard

### Runtime Issues
- Check environment variables are set
- View application logs
- Verify health check endpoint responds

### Agent Not Connecting
- Verify LiveKit credentials
- Check network connectivity
- Ensure agent process is running

### Performance Issues
- Monitor CPU/memory usage
- Check auto-scaling configuration
- Consider upgrading instance size

## 📈 Scaling Considerations

### Vertical Scaling (Upgrade Instance)
- Basic XS: $12/month (1GB RAM, 1 vCPU)
- Basic S: $25/month (2GB RAM, 1 vCPU)
- Basic M: $50/month (4GB RAM, 2 vCPU)

### Horizontal Scaling (More Instances)
- Auto-scaling handles this automatically
- Configure max instances based on expected load
- Each instance can handle multiple concurrent sessions

## 🔄 CI/CD Pipeline

With GitHub integration enabled:

1. **Push to main branch** → Automatic deployment
2. **Build process** → Docker image creation
3. **Health checks** → Verify deployment success
4. **Rolling deployment** → Zero-downtime updates
5. **Rollback** → Automatic if health checks fail

## 📞 Support

- **DigitalOcean Docs**: https://docs.digitalocean.com/products/app-platform/
- **Community**: https://www.digitalocean.com/community/
- **Support**: Available via DO dashboard

---

**Your LiveKit MCP Agent will be production-ready on DigitalOcean! 🚀**

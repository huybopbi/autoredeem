# Railway Deployment Guide

Hướng dẫn deploy CyborX Redeem Tool lên Railway (free hosting platform).

## 🚀 Quick Deploy to Railway

### Method 1: Deploy from GitHub (Recommended)

1. **Fork Repository**
   - Go to https://github.com/huybopbi/autoredeem
   - Click "Fork" to create your own copy

2. **Connect to Railway**
   - Go to https://railway.app
   - Sign up/Login with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your forked repository

3. **Configure Environment Variables**
   ```
   SECRET_KEY=your-very-secure-secret-key-here
   FLASK_ENV=production
   FLASK_DEBUG=False
   SESSION_DIR=/tmp/flask_session
   ```

4. **Deploy**
   - Railway will automatically detect the configuration
   - Wait for deployment to complete
   - Your app will be available at the provided URL

### Method 2: Deploy with Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   # or
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Deploy**
   ```bash
   # Clone repository
   git clone https://github.com/huybopbi/autoredeem.git
   cd autoredeem
   
   # Deploy to Railway
   railway up
   ```

## 🔧 Configuration Files

### Procfile
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
```

### runtime.txt
```
python-3.11.7
```

Railway sẽ tự động detect Python app và sử dụng Procfile để start.

## 🌐 Environment Variables

Set these in Railway dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `SECRET_KEY` | `your-secret-key` | Flask secret key for sessions |
| `FLASK_ENV` | `production` | Flask environment |
| `FLASK_DEBUG` | `False` | Debug mode |
| `SESSION_DIR` | `/tmp/flask_session` | Session storage directory |
| `PORT` | `5000` | Port (auto-set by Railway) |

## 📊 Railway Features

### Free Tier Limits
- **$5 credit monthly** (usually enough for small apps)
- **512MB RAM**
- **1GB storage**
- **Custom domains** (with paid plan)

### Automatic Features
- **Auto-deploy** from GitHub
- **Health checks**
- **Auto-restart** on failure
- **Logs** in dashboard
- **Metrics** and monitoring

## 🔄 Updates

### Auto-deploy from GitHub
1. Push changes to your GitHub repository
2. Railway automatically detects changes
3. Triggers new deployment
4. Zero-downtime deployment

### Manual Deploy
```bash
# Using Railway CLI
railway up

# Or trigger from Railway dashboard
```

## 📝 Custom Domain

### Free Domain
Railway provides a free domain like: `https://your-app-name.railway.app`

### Custom Domain (Paid)
1. Go to Railway dashboard
2. Select your project
3. Go to "Settings" → "Domains"
4. Add your custom domain
5. Update DNS records as instructed

## 🔍 Monitoring

### Railway Dashboard
- **Logs**: Real-time application logs
- **Metrics**: CPU, Memory, Network usage
- **Deployments**: Deployment history
- **Environment**: Environment variables

### Health Check
Railway automatically checks: `GET /` endpoint
- Returns 200 OK = Healthy
- Returns error = Unhealthy (auto-restart)

## 🚨 Troubleshooting

### Common Issues

1. **Build Fails**
   ```
   Check requirements.txt
   Ensure all dependencies are listed
   ```

2. **App Crashes**
   ```
   Check logs in Railway dashboard
   Verify environment variables
   ```

3. **Session Issues**
   ```
   Ensure SESSION_DIR is writable
   Check /tmp/flask_session permissions
   ```

4. **Port Issues**
   ```
   Railway sets PORT automatically
   Don't hardcode port numbers
   Use $PORT environment variable
   ```

### Debug Commands
```bash
# View logs
railway logs

# Connect to container
railway shell

# Check environment
railway variables
```

## 💰 Pricing

### Free Tier
- $5 credit monthly
- Usually enough for small applications
- No credit card required

### Paid Plans
- **Developer**: $5/month
- **Team**: $20/month
- **Enterprise**: Custom pricing

## 🔒 Security

### Environment Variables
- Never commit secrets to GitHub
- Use Railway's environment variables
- Rotate SECRET_KEY regularly

### HTTPS
- Railway provides HTTPS by default
- All traffic encrypted
- No additional configuration needed

## 📱 Access Your App

After deployment:
1. Go to Railway dashboard
2. Click on your project
3. Click on the generated URL
4. Your app will be live!

## 🎯 Best Practices

1. **Use Environment Variables** for configuration
2. **Monitor Logs** regularly
3. **Set up Health Checks**
4. **Use HTTPS** (automatic on Railway)
5. **Keep Dependencies Updated**
6. **Monitor Usage** to avoid overages

## 🔄 Migration from VPS

If you want to migrate from VPS to Railway:

1. **Export Environment Variables**
   ```bash
   # From your VPS
   printenv | grep -E "(SECRET_KEY|FLASK_)"
   ```

2. **Deploy to Railway**
   - Follow the deployment steps above
   - Set the same environment variables

3. **Update DNS**
   - Point your domain to Railway
   - Or use Railway's free domain

## 📞 Support

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **GitHub Issues**: https://github.com/huybopbi/autoredeem/issues

---

**Railway makes deployment super easy! 🚀**

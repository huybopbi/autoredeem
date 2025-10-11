# Railway Deployment Guide

🚀 **Hướng dẫn deploy CyborX Redeem Tool lên Railway**

## 📋 **Prerequisites**

1. **Railway Account**: Đăng ký tại [railway.app](https://railway.app)
2. **GitHub Repository**: Code đã push lên GitHub
3. **Redis Service**: Cần Redis để lưu session data

## 🚀 **Deployment Steps**

### 1. **Connect GitHub Repository**

1. Đăng nhập Railway
2. Click **"New Project"**
3. Chọn **"Deploy from GitHub repo"**
4. Chọn repository `huybopbi/autoredeem`
5. Railway sẽ tự động detect Dockerfile

### 2. **Add Redis Service**

1. Trong project dashboard, click **"+ New"**
2. Chọn **"Database"** → **"Add Redis"**
3. Railway sẽ tạo Redis instance
4. Copy **Redis URL** từ service settings

### 3. **Configure Environment Variables**

Trong **Variables** tab, thêm:

```bash
# Redis Configuration
REDIS_URL=redis://default:password@redis.railway.internal:6379

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Security
SECRET_KEY=your-very-secure-secret-key-here

# Session Configuration
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### 4. **Deploy**

1. Railway sẽ tự động build và deploy
2. Check **Deployments** tab để xem progress
3. App sẽ available tại URL được generate

## 🔧 **Railway Configuration**

### **railway.json**
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **Dockerfile**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p user_files
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5000
EXPOSE $PORT
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app"]
```

## 🌐 **Environment Variables**

### **Required Variables:**
```bash
REDIS_URL=redis://default:password@redis.railway.internal:6379
SECRET_KEY=your-secure-secret-key
FLASK_ENV=production
```

### **Optional Variables:**
```bash
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

## 🔍 **Troubleshooting**

### **Common Issues:**

#### **1. Gunicorn not found**
```bash
# Solution: Add gunicorn to requirements.txt
gunicorn==21.2.0
```

#### **2. Redis connection failed**
```bash
# Check Redis URL format
REDIS_URL=redis://default:password@redis.railway.internal:6379
```

#### **3. Port binding error**
```bash
# Error: '$PORT' is not a valid port number
# Solution: Use fixed port 5000
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

# Or use fallback syntax
gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 app:app
```

#### **4. Build timeout**
```bash
# Optimize Dockerfile layers
# Use .dockerignore to exclude unnecessary files
```

### **Debug Commands:**

#### **Check logs:**
```bash
# Railway dashboard → Deployments → View logs
```

#### **Test Redis connection:**
```bash
# Add to app.py for debugging
try:
    redis_client.ping()
    print("✅ Redis connection successful")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
```

## 📊 **Monitoring**

### **Railway Dashboard:**
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: Build and deployment history

### **Health Check:**
- **Endpoint**: `https://your-app.railway.app/`
- **Status**: 200 OK means app is running

## 🔄 **Updates**

### **Auto Deploy:**
- Railway auto-deploys khi push code lên GitHub
- Check **Deployments** tab để monitor

### **Manual Deploy:**
- Click **"Redeploy"** trong Railway dashboard
- Hoặc push commit mới lên GitHub

## 💰 **Pricing**

### **Free Tier:**
- $5 credit/month
- Sufficient for small applications
- Auto-sleep after inactivity

### **Pro Plan:**
- $5/month per service
- Always-on deployment
- Better performance

## 🎯 **Best Practices**

### **Security:**
- Use strong SECRET_KEY
- Enable HTTPS (Railway provides automatically)
- Set SESSION_COOKIE_SECURE=True

### **Performance:**
- Use Redis for session storage
- Optimize Docker image size
- Monitor resource usage

### **Monitoring:**
- Check logs regularly
- Monitor Redis connection
- Set up alerts for errors

## 🆘 **Support**

### **Railway Support:**
- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Railway GitHub](https://github.com/railwayapp)

### **App Issues:**
- Check application logs
- Verify environment variables
- Test Redis connection

---

**🎉 Happy Deploying!**

# 🚀 Deployment Guide - AI Thumbnail Toolkit

## Quick Comparison

| Platform | Ease | Cost | Best For |
|----------|------|------|----------|
| **Railway** | ⭐⭐⭐⭐⭐ | $5/mo after free tier | **Recommended - Easiest** |
| **Render** | ⭐⭐⭐⭐ | Free tier available | Small teams, testing |
| **Heroku** | ⭐⭐⭐⭐ | $7/mo (no free tier) | Established platform |
| **Google Cloud Run** | ⭐⭐⭐ | Pay per use (~$10/mo) | Google API integration |
| **DigitalOcean** | ⭐⭐⭐ | $5/mo | Custom VPS option |

---

## 🎯 Option 1: Railway (RECOMMENDED - 5 mins)

**Perfect for:** Quick deployment, team sharing, auto-scaling

### Steps:

1. **Push to GitHub**
   ```bash
   cd /Users/noorgupta/Downloads/Cursor/thumbnail_tookit
   git init
   git add .
   git commit -m "Initial commit - AI Thumbnail Toolkit"
   
   # Create a new repo on GitHub, then:
   git remote add origin https://github.com/YOUR_USERNAME/thumbnail-toolkit.git
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `thumbnail-toolkit` repository
   - Railway auto-detects Python and deploys! 🎉

3. **Add Environment Variables**
   - In Railway project, go to "Variables" tab
   - Add:
     ```
     OPENAI_API_KEY=your_key_here
     GOOGLE_API_KEY=your_key_here
     FREEPIK_API_KEY=your_key_here (optional)
     REPLICATE_API_TOKEN=your_key_here (optional)
     FAL_KEY=your_key_here (optional)
     PORT=5002
     ```

4. **Get Your URL**
   - Railway auto-generates a URL like: `https://your-app.up.railway.app`
   - Share this with your team! ✅

**Cost:**
- Free tier: 500 hours/month + $5 credit
- After: ~$5-10/month depending on usage

---

## 🎨 Option 2: Render (FREE tier available)

**Perfect for:** Testing, small teams, budget-conscious

### Steps:

1. **Push to GitHub** (same as Railway step 1)

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render auto-detects settings from `render.yaml`

3. **Configure**
   - Name: `thumbnail-toolkit`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn web_app:app`
   - Select "Free" plan

4. **Add Environment Variables**
   - In Render dashboard, go to "Environment"
   - Add the same API keys as Railway

5. **Deploy!**
   - URL: `https://thumbnail-toolkit.onrender.com`

**Cost:**
- Free tier: Yes! (spins down after inactivity, takes 30s to wake up)
- Paid: $7/month (always on)

---

## 🔧 Option 3: Heroku (Classic choice)

**Perfect for:** Established platform, lots of add-ons

### Steps:

1. **Install Heroku CLI**
   ```bash
   brew tap heroku/brew && brew install heroku
   ```

2. **Deploy**
   ```bash
   cd /Users/noorgupta/Downloads/Cursor/thumbnail_tookit
   heroku login
   heroku create thumbnail-toolkit-yourname
   
   # Add environment variables
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set GOOGLE_API_KEY=your_key
   
   # Deploy
   git push heroku main
   ```

3. **Scale**
   ```bash
   heroku ps:scale web=1
   ```

**Cost:**
- No free tier anymore
- Basic: $7/month

---

## ☁️ Option 4: Google Cloud Run (Advanced)

**Perfect for:** Google API integration, pay-per-use, auto-scaling

### Steps:

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   ENV PORT=8080
   CMD exec gunicorn --bind :$PORT --workers 2 --timeout 300 web_app:app
   ```

2. **Deploy to Cloud Run**
   ```bash
   # Install gcloud CLI first
   gcloud init
   gcloud auth login
   
   # Build and deploy
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/thumbnail-toolkit
   gcloud run deploy thumbnail-toolkit \
     --image gcr.io/YOUR_PROJECT_ID/thumbnail-toolkit \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=your_key,GOOGLE_API_KEY=your_key
   ```

**Cost:**
- Free tier: 2 million requests/month
- After: ~$10-20/month depending on usage

---

## 🖥️ Option 5: DigitalOcean Droplet (VPS - Full Control)

**Perfect for:** Custom setup, full control, multiple apps

### Quick Setup:

1. **Create Droplet**
   - Go to DigitalOcean
   - Create Ubuntu 22.04 droplet ($6/month)
   - SSH into server

2. **Setup**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3-pip python3-venv nginx -y
   
   # Clone your repo
   git clone https://github.com/YOUR_USERNAME/thumbnail-toolkit.git
   cd thumbnail-toolkit
   
   # Setup virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Create .env file
   nano .env
   # Add your API keys
   
   # Run with gunicorn
   gunicorn --bind 0.0.0.0:5002 --workers 2 --timeout 300 web_app:app
   ```

3. **Setup Nginx as reverse proxy**
   ```nginx
   server {
       listen 80;
       server_name your_domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5002;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Setup systemd service** (to keep it running)
   ```bash
   sudo nano /etc/systemd/system/thumbnail-toolkit.service
   ```
   
   ```ini
   [Unit]
   Description=AI Thumbnail Toolkit
   After=network.target
   
   [Service]
   User=your_user
   WorkingDirectory=/home/your_user/thumbnail-toolkit
   Environment="PATH=/home/your_user/thumbnail-toolkit/venv/bin"
   ExecStart=/home/your_user/thumbnail-toolkit/venv/bin/gunicorn --bind 0.0.0.0:5002 --workers 2 --timeout 300 web_app:app
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   ```bash
   sudo systemctl start thumbnail-toolkit
   sudo systemctl enable thumbnail-toolkit
   ```

**Cost:**
- Basic Droplet: $6/month
- Domain (optional): ~$12/year

---

## 🔐 Important: Security & Setup

### 1. Environment Variables

**Never commit API keys!** Your `.env` file should be in `.gitignore` (it already is).

Add these environment variables in your hosting platform:
```bash
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AI...
FREEPIK_API_KEY=... (optional)
REPLICATE_API_TOKEN=... (optional)
FAL_KEY=... (optional)
PORT=5002
```

### 2. Add Authentication (Optional but Recommended)

If you want to restrict access to your team only, you can add simple password protection:

```python
# Add to web_app.py at the top
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    """Check if username/password is valid"""
    return username == 'team' and password == 'your_secure_password_here'

def authenticate():
    """Send 401 response"""
    return Response(
        'Please login', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Then add @requires_auth to your routes:
@app.route('/')
@requires_auth
def index():
    return render_template('index.html')
```

### 3. Custom Domain (Optional)

Most platforms allow custom domains:
- **Railway**: Project Settings → Domains → Add Custom Domain
- **Render**: Settings → Custom Domain
- **Heroku**: `heroku domains:add yourdomain.com`

Buy domain from: Namecheap, Google Domains, or Cloudflare

---

## 📊 Monitoring & Maintenance

### Check Logs:
- **Railway**: Click on "Deployments" → View logs
- **Render**: Dashboard → Logs tab
- **Heroku**: `heroku logs --tail`

### Update App:
Just push to GitHub - Railway/Render auto-deploy!
```bash
git add .
git commit -m "Update features"
git push origin main
```

---

## 💡 My Recommendation

**For your team, I recommend Railway:**

✅ **Easiest setup** (5 minutes)  
✅ **Auto-deploys** from GitHub  
✅ **Good free tier** to start  
✅ **Scales automatically**  
✅ **Great dashboard** for monitoring  
✅ **Team-friendly** pricing

**Steps:**
1. Push code to GitHub (2 mins)
2. Connect Railway to GitHub (1 min)
3. Add API keys in Railway dashboard (1 min)
4. Share URL with team! (1 min)

**Total time: 5 minutes** ⚡

---

## 🆘 Need Help?

Common issues:

**Issue:** "Application Error" on deployment
- **Fix:** Check logs, ensure all environment variables are set

**Issue:** Images not loading
- **Fix:** Make sure `generated_thumbnails/` directory is created (happens automatically)

**Issue:** Slow performance
- **Fix:** Upgrade to paid tier with more resources

**Issue:** API rate limits
- **Fix:** Each user's API keys have limits. Monitor usage in OpenAI/Google dashboards

---

## 📱 Sharing with Your Team

Once deployed, share:
1. **URL**: `https://your-app.railway.app`
2. **Instructions**: "Just open the URL and start generating!"
3. **API Keys**: Each team member can use the same keys (set in environment variables), or you can have them enter their own keys in the UI

**Optional:** Create a Slack/Discord webhook to notify when new thumbnails are generated!

---

Good luck with your deployment! 🚀


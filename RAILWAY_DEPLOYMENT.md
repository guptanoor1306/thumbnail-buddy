# 🚂 Railway Deployment Guide for Thumbnail Buddy

Complete step-by-step guide to deploy your Thumbnail Toolkit on Railway.app with GitHub integration.

---

## 📋 Prerequisites

1. ✅ GitHub account
2. ✅ Railway account (sign up at https://railway.app)
3. ✅ Your API keys ready:
   - `OPENAI_API_KEY`
   - `GOOGLE_API_KEY`

---

## 🚀 Deployment Steps

### **Step 1: Push Your Code to GitHub**

1. **Initialize Git (if not already done):**
   ```bash
   cd /Users/noorgupta/Downloads/Cursor/thumbnail_tookit
   git init
   git add .
   git commit -m "Initial commit - Thumbnail Buddy"
   ```

2. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Name it: `thumbnail-buddy` (or any name you like)
   - Don't initialize with README (you already have files)
   - Click "Create repository"

3. **Push your code:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/thumbnail-buddy.git
   git branch -M main
   git push -u origin main
   ```

---

### **Step 2: Deploy to Railway**

1. **Go to Railway Dashboard:**
   - Visit https://railway.app
   - Click "Login" (use GitHub to login)

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub
   - Select your `thumbnail-buddy` repository

3. **Railway will automatically:**
   - ✅ Detect it's a Python Flask app
   - ✅ Read `requirements.txt`
   - ✅ Use `railway.json` configuration
   - ✅ Start building your app

---

### **Step 3: Add Environment Variables**

1. **In Railway Dashboard:**
   - Click on your deployed service
   - Go to "Variables" tab
   - Click "New Variable"

2. **Add these variables ONE BY ONE:**

   ```
   Variable Name: OPENAI_API_KEY
   Value: sk-proj-...your-actual-key...
   ```

   ```
   Variable Name: GOOGLE_API_KEY
   Value: AIza...your-actual-key...
   ```

   ```
   Variable Name: PORT
   Value: 5001
   ```

   ```
   Variable Name: FLASK_ENV
   Value: production
   ```

3. **Click "Add" for each variable**

---

### **Step 4: Configure Persistent Storage (IMPORTANT)**

Your thumbnails and generated images need persistent storage!

1. **In Railway Dashboard:**
   - Click on your service
   - Go to "Settings" tab
   - Scroll to "Volumes"
   - Click "New Volume"

2. **Create Volume:**
   ```
   Mount Path: /app/thumbnails
   ```
   - Click "Add"

3. **Create Another Volume:**
   ```
   Mount Path: /app/generated_thumbnails
   ```
   - Click "Add"

---

### **Step 5: Deploy & Monitor**

1. **Trigger Deployment:**
   - Railway auto-deploys on every git push
   - Or click "Deploy" button manually

2. **Monitor Build:**
   - Go to "Deployments" tab
   - Watch the build logs
   - Build takes ~5-10 minutes (installing torch, etc.)

3. **Check Logs:**
   - Click "View Logs"
   - Look for:
     ```
     ✅ Thumbnails indexed successfully!
     ✅ Server started on port 5001
     ```

---

### **Step 6: Get Your Live URL**

1. **In Railway Dashboard:**
   - Click "Settings" tab
   - Scroll to "Networking"
   - Click "Generate Domain"
   - Copy your URL: `your-app.railway.app`

2. **Visit Your App:**
   - Open `https://your-app.railway.app`
   - 🎉 Your Thumbnail Buddy is live!

---

## 📤 Upload Your Thumbnails to Railway

Your thumbnails are currently local. Here's how to get them on Railway:

### **Option 1: Include in Git (Small collections)**

If you have < 100MB of thumbnails:

```bash
# Add thumbnails to git
git add thumbnails/
git commit -m "Add thumbnail collection"
git push
```

Railway will redeploy automatically with thumbnails included.

### **Option 2: Upload via SCP/SFTP (Large collections)**

For 400+ thumbnails:

1. **Use Railway CLI:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Link to your project
   railway link
   
   # Upload thumbnails
   railway run bash
   # Then manually upload using file manager
   ```

### **Option 3: Start Fresh on Railway**

Upload thumbnails directly through your web app after deployment:
- You can modify the app to add an admin upload feature
- Or use Railway's file browser in dashboard

---

## 🔄 Automatic Deployments

Every time you push to GitHub, Railway auto-deploys:

```bash
# Make changes locally
git add .
git commit -m "Update thumbnail analyzer"
git push

# Railway automatically:
# 1. Detects the push
# 2. Rebuilds the app
# 3. Deploys new version
# 4. Keeps your volumes intact
```

---

## 💰 Pricing & Limits

### **Free Trial:**
- $5 free credit
- Good for ~1 month of testing
- No credit card required

### **Hobby Plan ($5/month):**
- $5 credit per month
- Enough for your app
- ~500 hours of uptime
- Persistent volumes included

### **Expected Usage:**
- Your app: ~$3-5/month
- Mostly idle when not generating
- Pay only for what you use

---

## 🐛 Troubleshooting

### **Build Fails:**

**Error:** "Out of memory"
- **Fix:** In Railway settings, increase memory limit (Settings > Resources)

**Error:** "Timeout during build"
- **Fix:** Reduce dependencies or split into stages

### **App Not Starting:**

1. **Check Logs:**
   - Railway Dashboard > Deployments > View Logs
   - Look for Python errors

2. **Common Issues:**
   - Missing environment variables
   - Port binding (should use `$PORT`)
   - File permissions

### **Thumbnails Not Loading:**

1. **Check Volumes:**
   - Settings > Volumes
   - Ensure `/app/thumbnails` is mounted

2. **Re-upload thumbnails** using one of the methods above

### **Slow Generation:**

- Railway free tier has CPU limits
- Upgrade to Hobby plan for better performance
- Consider adding more workers in `railway.json`

---

## 📊 Monitoring Your App

1. **Railway Dashboard:**
   - CPU/Memory usage
   - Request logs
   - Deployment history

2. **Set Up Alerts:**
   - Settings > Notifications
   - Get notified on failures

---

## 🔐 Security Best Practices

1. **Never commit `.env` to GitHub:**
   - Already in `.gitignore` ✅
   - Always use Railway Variables

2. **Rotate API Keys regularly:**
   - Update in Railway Variables
   - No need to redeploy

3. **Use Private Repository:**
   - Make GitHub repo private
   - Keeps your code secure

---

## 🎯 Next Steps After Deployment

1. **Test All Features:**
   - Upload/select thumbnails
   - Run AI analysis
   - Generate with both Gemini & DALL-E

2. **Monitor Costs:**
   - Railway Dashboard > Usage
   - Track monthly spending

3. **Share Your App:**
   - Share the Railway URL
   - Add authentication if needed (future enhancement)

---

## 🆘 Need Help?

**Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app

**Common Commands:**
```bash
# View logs
railway logs

# Restart app
railway restart

# Open app in browser
railway open
```

---

## 📝 Summary

```
✅ Files created:
   - railway.json (Railway configuration)
   - Procfile (Backup start command)
   - .railwayignore (Exclude unnecessary files)
   - runtime.txt (Python version)
   - requirements.txt (Updated with gunicorn)

✅ Ready to deploy:
   1. Push to GitHub
   2. Connect Railway to GitHub
   3. Add environment variables
   4. Configure volumes
   5. Deploy & enjoy!
```

---

**🎉 Your Thumbnail Buddy will be live in ~10 minutes after following these steps!**

Need help with any step? Let me know!


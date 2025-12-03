#!/bin/bash

# 🚀 Quick Deployment Script for AI Thumbnail Toolkit

echo "=================================================="
echo "🎨 AI Thumbnail Toolkit - Deployment Helper"
echo "=================================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📝 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - AI Thumbnail Toolkit"
    echo "✅ Git initialized!"
    echo ""
else
    echo "✅ Git already initialized"
    echo ""
fi

# Show deployment options
echo "Choose your deployment platform:"
echo ""
echo "1) Railway (Recommended - Easiest)"
echo "2) Render (Free tier available)"
echo "3) Heroku (Classic)"
echo "4) Manual setup (I'll do it myself)"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚂 Railway Deployment"
        echo "===================="
        echo ""
        echo "Steps:"
        echo "1. Go to https://railway.app and sign up with GitHub"
        echo "2. Click 'New Project' → 'Deploy from GitHub repo'"
        echo "3. Push this code to GitHub first:"
        echo ""
        echo "   git remote add origin https://github.com/YOUR_USERNAME/thumbnail-toolkit.git"
        echo "   git branch -M main"
        echo "   git push -u origin main"
        echo ""
        echo "4. Select your repo in Railway"
        echo "5. Add environment variables in Railway dashboard:"
        echo "   - OPENAI_API_KEY"
        echo "   - GOOGLE_API_KEY"
        echo "   - PORT=5002"
        echo ""
        echo "✅ Railway will auto-deploy! Get your URL from the dashboard."
        ;;
    2)
        echo ""
        echo "🎨 Render Deployment"
        echo "==================="
        echo ""
        echo "Steps:"
        echo "1. Go to https://render.com and sign up with GitHub"
        echo "2. Click 'New +' → 'Web Service'"
        echo "3. Push this code to GitHub first:"
        echo ""
        echo "   git remote add origin https://github.com/YOUR_USERNAME/thumbnail-toolkit.git"
        echo "   git branch -M main"
        echo "   git push -u origin main"
        echo ""
        echo "4. Connect your GitHub repo"
        echo "5. Render will detect settings from render.yaml"
        echo "6. Add environment variables in Render dashboard"
        echo ""
        echo "✅ Deploy! Free tier available."
        ;;
    3)
        echo ""
        echo "☁️ Heroku Deployment"
        echo "==================="
        echo ""
        
        # Check if Heroku CLI is installed
        if ! command -v heroku &> /dev/null; then
            echo "❌ Heroku CLI not found. Installing..."
            echo ""
            echo "Run: brew tap heroku/brew && brew install heroku"
            echo "Then run this script again."
            exit 1
        fi
        
        echo "Heroku CLI found! ✅"
        echo ""
        read -p "Enter your app name (e.g., thumbnail-toolkit-yourname): " appname
        
        echo ""
        echo "Creating Heroku app..."
        heroku create $appname
        
        echo ""
        echo "Setting environment variables..."
        read -p "Enter your OPENAI_API_KEY: " openai_key
        read -p "Enter your GOOGLE_API_KEY: " google_key
        
        heroku config:set OPENAI_API_KEY=$openai_key
        heroku config:set GOOGLE_API_KEY=$google_key
        
        echo ""
        echo "Deploying to Heroku..."
        git push heroku main
        
        echo ""
        echo "✅ Deployed! Opening app..."
        heroku open
        ;;
    4)
        echo ""
        echo "📖 Manual Setup"
        echo "==============="
        echo ""
        echo "Check DEPLOYMENT.md for detailed instructions for:"
        echo "- Google Cloud Run"
        echo "- DigitalOcean VPS"
        echo "- Custom Docker deployment"
        echo ""
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "🎉 Need help? Check DEPLOYMENT.md for full guide"
echo "=================================================="


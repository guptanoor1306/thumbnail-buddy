# 🎨 Thumbnail Buddy - AI-Powered YouTube Thumbnail Generator

An intelligent web application that analyzes YouTube thumbnails using AI and generates variations using DALL-E 3 and Google's Gemini 2.5 Flash Image (Nano Banana).

---

## ✨ Features

- 🔍 **Smart Thumbnail Search** - CLIP-powered semantic search across 400+ thumbnails
- 🏷️ **Category Organization** - Browse thumbnails by categories (Movies, Podcast, Documentary, etc.)
- 🧠 **AI Analysis** - GPT-4o Vision analyzes thumbnails for psychological triggers, CTR optimization
- 🎨 **Dual AI Generation**:
  - **Gemini 2.5 Flash Image (Nano Banana)** - Fast, high-quality generation
  - **DALL-E 3** - Creative redesigns with GPT-4o Vision analysis
- ✏️ **Editable Prompts** - Customize generation prompts before creating
- 📤 **Manual Upload** - Override with your own reference images
- 🎯 **Multi-Generation** - Generate variations for multiple thumbnails independently

---

## 🚀 Quick Start

### Local Development

1. **Clone and Install:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/thumbnail-buddy.git
   cd thumbnail-buddy
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up API Keys:**
   ```bash
   cp env.example .env
   # Edit .env and add your API keys:
   # OPENAI_API_KEY=sk-proj-...
   # GOOGLE_API_KEY=AIza...
   ```

3. **Add Thumbnails:**
   ```bash
   # Organize thumbnails in subdirectories by category:
   thumbnails/
   ├── Movies/
   ├── Podcast/
   ├── Documentary/
   └── ...
   ```

4. **Run the App:**
   ```bash
   python web_app.py
   # Open http://localhost:5001
   ```

---

## 🚂 Deploy to Railway

See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for complete deployment guide.

**Quick Steps:**
1. Push to GitHub
2. Connect Railway to your repo
3. Add environment variables (`OPENAI_API_KEY`, `GOOGLE_API_KEY`)
4. Configure persistent volumes for thumbnails
5. Deploy! 🎉

---

## 🎯 How It Works

### 1. **Search & Select**
- Browse all thumbnails or filter by category
- Use semantic search to find similar styles
- Select one or multiple thumbnails

### 2. **AI Analysis**
- GPT-4o Vision analyzes the thumbnail
- Identifies psychological triggers
- Suggests strategic modifications
- Generates optimized prompt

### 3. **Customize**
- Edit the generation prompt
- Choose AI service (Gemini or DALL-E)
- Optionally upload different reference image

### 4. **Generate**
- AI creates new thumbnail based on your specs
- Download and use for your videos!

---

## 🛠️ Tech Stack

**Backend:**
- Flask (Python web framework)
- OpenAI GPT-4o Vision (thumbnail analysis)
- OpenAI DALL-E 3 (image generation)
- Google Gemini 2.5 Flash Image (image generation)
- CLIP (semantic search)
- Sentence Transformers (embeddings)

**Frontend:**
- Vanilla JavaScript (no frameworks)
- Modern CSS with Roboto font
- Responsive design

**Deployment:**
- Railway.app (recommended)
- Gunicorn (production server)
- Persistent volumes for storage

---

## 📁 Project Structure

```
thumbnail_tookit/
├── web_app.py                 # Flask application
├── image_generator.py         # AI image generation logic
├── thumbnail_analyzer.py      # GPT-4o Vision analysis
├── thumbnail_finder.py        # CLIP search & indexing
├── templates/
│   └── index.html            # Main web interface
├── static/
│   ├── css/style.css         # Styles
│   └── js/app.js             # Frontend logic
├── thumbnails/               # Your thumbnail collection
│   ├── Movies/
│   ├── Podcast/
│   └── ...
├── generated_thumbnails/     # AI-generated results
├── requirements.txt          # Python dependencies
├── railway.json             # Railway configuration
└── RAILWAY_DEPLOYMENT.md    # Deployment guide
```

---

## 🔑 Required API Keys

### OpenAI API Key
- Get from: https://platform.openai.com/api-keys
- Used for: GPT-4o Vision analysis & DALL-E 3 generation
- Cost: ~$0.01-0.05 per generation

### Google AI Studio API Key
- Get from: https://aistudio.google.com/app/apikey
- Used for: Gemini 2.5 Flash Image (Nano Banana) generation
- Cost: Free tier available

---

## 💡 Tips for Best Results

### For Analysis:
- ✅ Use high-quality reference thumbnails
- ✅ Select thumbnails with clear faces and text
- ✅ Avoid blurry or low-resolution images

### For Generation:
- ✅ **Gemini 2.5 Flash Image**: Best for quick, high-quality results
- ✅ **DALL-E 3**: Best for creative redesigns and style variations
- ✅ Be specific in prompts about colors, layout, emotions
- ✅ Mention what to keep vs. what to change

---

## 📊 Cost Estimates

**Development (testing):**
- 10 analyses: ~$0.10
- 10 generations: ~$0.50
- **Total: ~$0.60/day**

**Production (active use):**
- 50 analyses: ~$0.50
- 50 generations: ~$2.50
- **Total: ~$3/day**

**Railway Hosting:**
- $5/month (includes $5 credit)
- Sufficient for moderate usage

---

## 🐛 Troubleshooting

### "No thumbnails found"
- Check that thumbnails are in subdirectories
- Ensure files are `.jpg` or `.png`
- Delete `thumbnail_index.json` and restart

### "API key not valid"
- Verify keys in `.env` file (local) or Railway Variables (production)
- Check for extra spaces or quotes
- Ensure keys are active

### "Generation timeout"
- Normal for DALL-E (30-60 seconds)
- Gemini is usually faster (10-20 seconds)
- Check server logs for errors

### "Module not found"
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

---

## 🔐 Security Notes

- ⚠️ Never commit `.env` to Git (already in `.gitignore`)
- ⚠️ Use environment variables for API keys in production
- ⚠️ Consider making GitHub repo private
- ⚠️ Rotate API keys regularly

---

## 🤝 Contributing

This is a personal project, but suggestions welcome!

---

## 📝 License

MIT License - feel free to use and modify!

---

## 🆘 Support

**Issues or Questions?**
- Check [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for deployment help
- Railway Discord: https://discord.gg/railway
- OpenAI Docs: https://platform.openai.com/docs

---

## 🎉 Credits

Built with ❤️ using:
- OpenAI GPT-4o & DALL-E 3
- Google Gemini 2.5 Flash Image
- OpenAI CLIP
- Flask & Python

---

**Ready to generate amazing thumbnails? Let's go! 🚀**

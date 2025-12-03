#!/usr/bin/env python3
"""
Pre-deployment checker for Thumbnail Buddy
Verifies everything is ready for Railway deployment
"""

import os
import sys
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    print("\n" + "="*70)
    print("📋 Checking Required Files...")
    print("="*70)
    
    required_files = [
        'web_app.py',
        'image_generator.py',
        'thumbnail_analyzer.py',
        'thumbnail_finder.py',
        'requirements.txt',
        'railway.json',
        'Procfile',
        'runtime.txt',
        '.gitignore',
        'templates/index.html',
        'static/js/app.js',
        'static/css/style.css'
    ]
    
    all_exist = True
    for file in required_files:
        exists = Path(file).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_env_vars():
    """Check if environment variables are set"""
    print("\n" + "="*70)
    print("🔑 Checking Environment Variables...")
    print("="*70)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API (for GPT-4o & DALL-E 3)',
        'GOOGLE_API_KEY': 'Google AI Studio (for Gemini 2.5 Flash)'
    }
    
    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {var}: {masked}")
            print(f"   └─ {description}")
        else:
            print(f"❌ {var}: NOT SET")
            print(f"   └─ {description}")
            all_set = False
    
    return all_set

def check_thumbnails():
    """Check thumbnail directory structure"""
    print("\n" + "="*70)
    print("🖼️  Checking Thumbnails...")
    print("="*70)
    
    thumbnails_dir = Path('thumbnails')
    
    if not thumbnails_dir.exists():
        print("❌ thumbnails/ directory not found")
        return False
    
    # Count subdirectories (categories)
    categories = [d for d in thumbnails_dir.iterdir() if d.is_dir()]
    
    if not categories:
        print("⚠️  No category subdirectories found")
        print("   Create subdirectories like: thumbnails/Movies/, thumbnails/Podcast/")
        return False
    
    print(f"✅ Found {len(categories)} categories:")
    
    total_images = 0
    for category in categories:
        images = list(category.glob('*.jpg')) + list(category.glob('*.png')) + list(category.glob('*.jpeg'))
        total_images += len(images)
        print(f"   └─ {category.name}: {len(images)} images")
    
    print(f"\n📊 Total thumbnails: {total_images}")
    
    if total_images == 0:
        print("⚠️  No images found in categories")
        return False
    
    return True

def check_git():
    """Check git status"""
    print("\n" + "="*70)
    print("🔧 Checking Git Status...")
    print("="*70)
    
    if not Path('.git').exists():
        print("❌ Not a git repository")
        print("   Run: git init")
        return False
    
    print("✅ Git repository initialized")
    
    # Check if there are uncommitted changes
    import subprocess
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️  Uncommitted changes found:")
            lines = result.stdout.strip().split('\n')[:5]  # Show first 5
            for line in lines:
                print(f"   {line}")
            if len(result.stdout.strip().split('\n')) > 5:
                print(f"   ... and {len(result.stdout.strip().split('\n')) - 5} more")
            print("\n   Run: git add . && git commit -m 'Prepare for deployment'")
        else:
            print("✅ No uncommitted changes")
    except subprocess.CalledProcessError:
        print("⚠️  Could not check git status")
    
    # Check if remote is set
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("✅ Git remote configured")
            for line in result.stdout.strip().split('\n')[:2]:  # Show first 2
                print(f"   {line}")
        else:
            print("⚠️  No git remote configured")
            print("   Add remote: git remote add origin <your-github-repo-url>")
    except subprocess.CalledProcessError:
        print("⚠️  Could not check git remote")
    
    return True

def check_dependencies():
    """Check if all dependencies are installable"""
    print("\n" + "="*70)
    print("📦 Checking Dependencies...")
    print("="*70)
    
    try:
        import openai
        print("✅ openai installed")
    except ImportError:
        print("❌ openai not installed")
        return False
    
    try:
        import google.generativeai
        print("✅ google-generativeai installed")
    except ImportError:
        print("❌ google-generativeai not installed")
        return False
    
    try:
        import flask
        print("✅ flask installed")
    except ImportError:
        print("❌ flask not installed")
        return False
    
    try:
        import gunicorn
        print("✅ gunicorn installed")
    except ImportError:
        print("❌ gunicorn not installed")
        return False
    
    print("\n✅ All major dependencies installed")
    return True

def main():
    """Run all checks"""
    print("\n" + "="*70)
    print("🚂 RAILWAY DEPLOYMENT PRE-FLIGHT CHECK")
    print("="*70)
    
    checks = [
        ("Files", check_files),
        ("Environment Variables", check_env_vars),
        ("Thumbnails", check_thumbnails),
        ("Dependencies", check_dependencies),
        ("Git", check_git)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Error checking {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Ready for Railway deployment!")
        print("="*70)
        print("\nNext steps:")
        print("1. Push to GitHub: git push origin main")
        print("2. Go to Railway.app and connect your repo")
        print("3. Add environment variables in Railway dashboard")
        print("4. Deploy and enjoy!")
        print("\nSee RAILWAY_DEPLOYMENT.md for detailed instructions")
    else:
        print("⚠️  SOME CHECKS FAILED - Please fix issues before deploying")
        print("="*70)
        print("\nFix the issues above and run this script again")
    
    print()
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())


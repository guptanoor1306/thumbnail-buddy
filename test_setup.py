#!/usr/bin/env python3
"""
Test script to verify the thumbnail tool setup
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("1. Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\n2. Checking dependencies...")
    required = [
        'openai',
        'google.generativeai',
        'PIL',
        'sentence_transformers',
        'numpy',
        'torch',
        'requests',
        'dotenv'
    ]
    
    missing = []
    for package in required:
        try:
            if package == 'PIL':
                import PIL
                print(f"   ✓ PIL (Pillow)")
            elif package == 'dotenv':
                import dotenv
                print(f"   ✓ dotenv")
            elif package == 'google.generativeai':
                import google.generativeai
                print(f"   ✓ google-generativeai")
            elif package == 'openai':
                import openai
                print(f"   ✓ openai")
            else:
                __import__(package)
                print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n   Install missing packages with: pip install -r requirements.txt")
        return False
    return True


def check_directories():
    """Check if required directories exist"""
    print("\n3. Checking directories...")
    dirs = ['thumbnails', 'generated_thumbnails']
    
    all_exist = True
    for dir_name in dirs:
        if Path(dir_name).exists():
            print(f"   ✓ {dir_name}/")
        else:
            print(f"   ✗ {dir_name}/ (missing)")
            all_exist = False
    
    return all_exist


def check_thumbnails():
    """Check if thumbnails are present"""
    print("\n4. Checking thumbnails...")
    thumbnails_dir = Path('thumbnails')
    
    if not thumbnails_dir.exists():
        print(f"   ✗ thumbnails/ directory doesn't exist")
        return False
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    images = [f for f in thumbnails_dir.iterdir() if f.suffix.lower() in image_extensions]
    
    count = len(images)
    if count == 0:
        print(f"   ✗ No images found in thumbnails/")
        print(f"   → Add 20 thumbnail images to the thumbnails/ folder")
        return False
    elif count < 20:
        print(f"   ⚠️  Found {count} images (recommended: 20)")
        return True
    else:
        print(f"   ✓ Found {count} images")
        return True


def check_env_file():
    """Check if .env file exists and has keys"""
    print("\n5. Checking environment configuration...")
    
    if not Path('.env').exists():
        print(f"   ✗ .env file not found")
        print(f"   → Copy env.example to .env and add your API keys")
        return False
    
    print(f"   ✓ .env file exists")
    
    # Load and check keys
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check OpenAI API Key (required for analysis)
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key != 'your_openai_key_here':
        print(f"   ✓ OPENAI_API_KEY is set (for GPT-4 Vision analysis)")
    else:
        print(f"   ✗ OPENAI_API_KEY not set (REQUIRED)")
        print(f"   → Get your key from: https://platform.openai.com/api-keys")
        return False
    
    # Check image generation services (at least one recommended)
    services_found = []
    
    google_key = os.getenv('GOOGLE_API_KEY')
    if google_key and google_key != 'your_google_gemini_key_here':
        services_found.append('Google Gemini')
    
    replicate_key = os.getenv('REPLICATE_API_TOKEN')
    if replicate_key and replicate_key != 'your_replicate_token_here':
        services_found.append('Replicate')
    
    if services_found:
        print(f"   ✓ Image generation: {', '.join(services_found)} (+ DALL-E via OpenAI)")
    else:
        print(f"   ℹ️  Image generation: DALL-E 3 (via OpenAI key)")
    
    return True


def main():
    print("="*70)
    print("THUMBNAIL TOOL - SETUP VERIFICATION")
    print("="*70)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_directories(),
        check_thumbnails(),
        check_env_file()
    ]
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"\n✓ All checks passed ({passed}/{total})")
        print("\nYou're ready to run the tool!")
        print("Run: python main.py")
    else:
        print(f"\n⚠️  Some checks failed ({passed}/{total} passed)")
        print("\nPlease fix the issues above and run this test again.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


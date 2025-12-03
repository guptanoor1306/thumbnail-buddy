#!/usr/bin/env python3
"""Quick test to verify OpenAI API key works"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Force reload environment
load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")

print("="*70)
print("OPENAI API KEY TEST")
print("="*70)

if not api_key:
    print("❌ No API key found in environment")
    exit(1)

# Check key format
if api_key.startswith("your_"):
    print("❌ API key not updated - still has placeholder value")
    print("Please edit .env file and add your real OpenAI API key")
    exit(1)

print(f"✓ API key found: {api_key[:15]}...{api_key[-10:]}")
print(f"✓ Key length: {len(api_key)} characters")

if len(api_key) < 100:
    print("⚠️  Warning: Key seems short for a modern OpenAI key")

print("\n🧪 Testing API connection...")

try:
    client = OpenAI(api_key=api_key)
    
    # Simple test call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'Hello'"}],
        max_tokens=10
    )
    
    print("✅ API KEY WORKS!")
    print(f"   Response: {response.choices[0].message.content}")
    print("\n🎉 Your OpenAI setup is ready!")
    
except Exception as e:
    print(f"❌ API Error: {e}")
    print("\nThis usually means:")
    print("  1. API key is invalid or expired")
    print("  2. No credits/quota remaining")
    print("  3. Key doesn't have required permissions")
    exit(1)


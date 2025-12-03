#!/usr/bin/env python3
"""
Demo script to test the thumbnail tool workflow
"""

import os
import sys
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

from thumbnail_finder import ThumbnailFinder, display_results
from thumbnail_analyzer import ThumbnailAnalyzer

def demo_workflow():
    """Run a demonstration of the complete workflow"""
    
    print("="*70)
    print("THUMBNAIL TOOL - DEMO RUN")
    print("="*70)
    
    # Initialize
    print("\n1. Initializing Thumbnail Finder...")
    finder = ThumbnailFinder("thumbnails")
    print(f"   ✓ Loaded index with {finder.get_thumbnail_count()} thumbnails")
    
    # Demo topic
    topic = "AI Technology and Innovation"
    pov = "Tech Enthusiast"
    
    print(f"\n2. Searching for topic: '{topic}'")
    print(f"   Point of view: '{pov}'")
    
    # Find similar thumbnails
    results = finder.find_similar(topic, pov, top_k=3)
    display_results(results)
    
    # Select first result for demo
    selected = results[0]
    print(f"\n3. Selected thumbnail: {selected['filename']}")
    print(f"   Similarity score: {selected['similarity_score']:.3f}")
    
    # Analyze with Gemini
    print("\n4. Analyzing with Google Gemini Vision...")
    print("   (This may take 5-10 seconds...)")
    
    try:
        analyzer = ThumbnailAnalyzer()
        analysis = analyzer.analyze_thumbnail(selected['path'], topic, pov)
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE!")
        print("="*70)
        
        analyzer.display_analysis(analysis)
        
        print("\n" + "="*70)
        print("DEMO COMPLETE!")
        print("="*70)
        print("\nThe tool successfully:")
        print("  ✓ Loaded 32 thumbnails")
        print("  ✓ Found similar thumbnails using CLIP")
        print("  ✓ Analyzed with Gemini Vision")
        print("  ✓ Generated modification suggestions")
        print("\nTo generate an image, run: python main.py")
        print("And follow the interactive prompts!")
        
    except Exception as e:
        print(f"\n✗ Error during analysis: {e}")
        print("\nThis might be due to:")
        print("  - API key not valid")
        print("  - Network connection issues")
        print("  - API quota exceeded")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(demo_workflow())
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


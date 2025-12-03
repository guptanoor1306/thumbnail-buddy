#!/usr/bin/env python3
"""
Complete demo - runs full workflow including image generation
"""

import os
import sys
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

from thumbnail_finder import ThumbnailFinder, display_results
from thumbnail_analyzer import ThumbnailAnalyzer
from image_generator import ImageGenerator

def full_demo():
    """Run complete workflow with image generation"""
    
    print("="*70)
    print("COMPLETE THUMBNAIL GENERATION DEMO")
    print("="*70)
    
    # Demo parameters
    topic = "Cryptocurrency Trading for Beginners"
    pov = "Complete Beginner Friendly"
    
    print(f"\n🎯 Topic: {topic}")
    print(f"👁️  Point of View: {pov}")
    
    # Step 1: Initialize and search
    print("\n" + "="*70)
    print("STEP 1: FINDING SIMILAR THUMBNAILS")
    print("="*70)
    
    finder = ThumbnailFinder("thumbnails")
    print(f"✓ Loaded {finder.get_thumbnail_count()} thumbnails")
    
    results = finder.find_similar(topic, pov, top_k=3)
    display_results(results)
    
    # Step 2: Select first result
    selected = results[0]
    print("\n" + "="*70)
    print("STEP 2: SELECTED THUMBNAIL")
    print("="*70)
    print(f"✓ Selected: {selected['filename']}")
    print(f"✓ Similarity score: {selected['similarity_score']:.3f}")
    
    # Step 3: Analyze with GPT-4 Vision
    print("\n" + "="*70)
    print("STEP 3: AI ANALYSIS WITH GPT-4 VISION")
    print("="*70)
    print("Analyzing thumbnail... (this may take 10-15 seconds)")
    
    try:
        analyzer = ThumbnailAnalyzer()
        analysis = analyzer.analyze_thumbnail(selected['path'], topic, pov)
        
        print("\n✓ Analysis complete!")
        analyzer.display_analysis(analysis)
        
        # Step 4: Generate image
        print("\n" + "="*70)
        print("STEP 4: GENERATING NEW THUMBNAIL")
        print("="*70)
        print("Using DALL-E 3 (OpenAI)...")
        print("This will take 20-40 seconds...")
        
        generator = ImageGenerator(service='dalle')
        output_filename = f"generated_{topic.replace(' ', '_').lower()}.png"
        output_path = f"generated_thumbnails/{output_filename}"
        
        generation_prompt = analysis.get('generation_prompt', '')
        generated_path = generator.generate(generation_prompt, output_path)
        
        print("\n" + "="*70)
        print("🎉 SUCCESS! THUMBNAIL GENERATED!")
        print("="*70)
        print(f"\n✓ Your new thumbnail has been saved to:")
        print(f"  {generated_path}")
        print(f"\n✓ Topic: {topic}")
        print(f"✓ Based on: {selected['filename']}")
        print(f"✓ AI Analysis: GPT-4 Vision")
        print(f"✓ Generation: DALL-E 3")
        
        print("\n" + "="*70)
        print("WORKFLOW COMPLETE!")
        print("="*70)
        print("\nThe complete workflow took:")
        print("  ✓ Similarity search: <2 seconds")
        print("  ✓ GPT-4 Vision analysis: ~10 seconds")
        print("  ✓ DALL-E 3 generation: ~30 seconds")
        print("  ✓ Total: ~45 seconds")
        
        print(f"\n📁 View your thumbnail:")
        print(f"   open {generated_path}")
        
        print("\n🎨 To create more thumbnails, run: python main.py")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    try:
        sys.exit(full_demo())
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


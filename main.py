#!/usr/bin/env python3
"""
Thumbnail Wireframe Tool - Main CLI Interface
"""

import os
import sys
from pathlib import Path
from thumbnail_finder import ThumbnailFinder, display_results
from thumbnail_analyzer import ThumbnailAnalyzer
from image_generator import ImageGenerator


def setup_directories():
    """Create necessary directories"""
    dirs = ["thumbnails", "generated_thumbnails"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    return dirs


def get_input(prompt: str, required: bool = True) -> str:
    """Get user input with validation"""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("This field is required. Please try again.")


def main():
    print("="*70)
    print("YOUTUBE THUMBNAIL WIREFRAME TOOL")
    print("="*70)
    
    # Setup
    setup_directories()
    
    # Check if thumbnails directory has images
    thumbnails_dir = "thumbnails"
    if not any(Path(thumbnails_dir).iterdir()):
        print(f"\n⚠️  No thumbnails found in '{thumbnails_dir}' directory")
        print("Please add your 20 thumbnail images to the 'thumbnails' folder and run again.")
        return
    
    # Initialize components
    print("\nInitializing...")
    finder = ThumbnailFinder(thumbnails_dir)
    
    # Index thumbnails if needed
    if finder.get_thumbnail_count() == 0:
        print("\nNo index found. Indexing thumbnails...")
        finder.index_thumbnails()
    else:
        print(f"Found existing index with {finder.get_thumbnail_count()} thumbnails")
        reindex = input("\nRe-index thumbnails? (y/n): ").lower().strip()
        if reindex == 'y':
            finder.index_thumbnails()
    
    print("\n" + "="*70)
    print("STEP 1: FIND SIMILAR THUMBNAILS")
    print("="*70)
    
    # Get topic and POV
    topic = get_input("\nEnter your topic: ", required=True)
    pov = get_input("Enter point of view (optional, press Enter to skip): ", required=False)
    
    # Find similar thumbnails
    results = finder.find_similar(topic, pov, top_k=3)
    display_results(results)
    
    # User selects thumbnail
    print("\n" + "="*70)
    print("STEP 2: SELECT THUMBNAIL")
    print("="*70)
    
    while True:
        try:
            selection = int(get_input("\nSelect thumbnail number (1-3): "))
            if 1 <= selection <= len(results):
                selected = results[selection - 1]
                break
            print("Invalid selection. Please choose 1, 2, or 3.")
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"\n✓ Selected: {selected['filename']}")
    
    # Analyze and suggest modifications
    print("\n" + "="*70)
    print("STEP 3: ANALYZE & SUGGEST MODIFICATIONS")
    print("="*70)
    print("\nAnalyzing thumbnail with AI...")
    
    analyzer = ThumbnailAnalyzer()
    analysis = analyzer.analyze_thumbnail(selected['path'], topic, pov)
    analyzer.display_analysis(analysis)
    
    # Get approval
    print("\n" + "="*70)
    print("STEP 4: GENERATE NEW THUMBNAIL")
    print("="*70)
    
    approve = input("\nDo you approve these modifications? (y/n): ").lower().strip()
    
    if approve != 'y':
        print("\nModifications not approved. Exiting...")
        return
    
    # Choose generation service
    print("\nAvailable image generation services:")
    print("1. DALL-E 3 (OpenAI) - recommended")
    print("2. Replicate (FLUX model)")
    print("3. Google Gemini/Imagen")
    
    service_map = {
        '1': 'dalle',
        '2': 'replicate',
        '3': 'gemini'
    }
    
    while True:
        service_choice = input("\nSelect service (1-3): ").strip()
        if service_choice in service_map:
            service = service_map[service_choice]
            break
        print("Invalid choice. Please select 1, 2, or 3.")
    
    # Generate image
    try:
        generator = ImageGenerator(service=service)
        
        # Create output filename
        output_filename = f"generated_{topic.replace(' ', '_')}.png"
        output_path = Path("generated_thumbnails") / output_filename
        
        generation_prompt = analysis.get("generation_prompt", "")
        generated_path = generator.generate(generation_prompt, str(output_path))
        
        print("\n" + "="*70)
        print("✓ GENERATION COMPLETE!")
        print("="*70)
        print(f"\nYour new thumbnail has been saved to:")
        print(f"  {generated_path}")
        print("\nYou can now review and use this thumbnail!")
        
    except Exception as e:
        print(f"\n✗ Error generating image: {e}")
        print("\nPlease check your API key and try again.")
        print("Make sure you have the appropriate API key set in .env file")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


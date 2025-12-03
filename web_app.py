#!/usr/bin/env python3
"""
Flask Web Server for Thumbnail Generator
Beautiful custom HTML/CSS/JS interface
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from pathlib import Path
import os
import json
import uuid
from dotenv import load_dotenv
from PIL import Image

load_dotenv(override=True)

from thumbnail_finder import ThumbnailFinder
from thumbnail_analyzer import ThumbnailAnalyzer
from image_generator import ImageGenerator

app = Flask(__name__)
CORS(app)

# Ensure required directories exist (important for Railway deployment)
Path('thumbnails').mkdir(exist_ok=True)
Path('generated_thumbnails').mkdir(exist_ok=True)
Path('temp_uploads').mkdir(exist_ok=True)

# Initialize finder globally
finder = None

def init_finder():
    global finder
    if finder is None:
        finder = ThumbnailFinder("thumbnails")
        # Force index if empty
        if finder.get_thumbnail_count() == 0:
            print("📸 No thumbnails in index, indexing now...")
            finder.index_thumbnails()
    return finder

@app.route('/')
def index():
    """Serve main HTML page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'thumbnails_dir': Path('thumbnails').exists(),
        'version': '1.0.0'
    })

@app.route('/api/stats')
def get_stats():
    """Get statistics"""
    finder = init_finder()
    thumbnail_count = finder.get_thumbnail_count()
    categories = finder.get_categories()
    
    generated_dir = Path("generated_thumbnails")
    generated_count = 0
    if generated_dir.exists():
        generated_count = len(list(generated_dir.glob("*.png")))
    
    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    return jsonify({
        'thumbnail_count': thumbnail_count,
        'generated_count': generated_count,
        'categories': categories,
        'category_count': len(categories),
        'openai_configured': bool(openai_key and not openai_key.startswith('your_')),
        'google_configured': bool(google_key and not google_key.startswith('your_'))
    })

@app.route('/api/all-thumbnails')
def get_all_thumbnails():
    """Get list of all thumbnails in toolkit (organized by category)"""
    finder = init_finder()
    thumbnails_data = finder.index_data.get("thumbnails", [])
    categories = finder.get_categories()
    
    # Organize thumbnails by category
    categorized = {}
    uncategorized = []
    
    for thumb in thumbnails_data:
        category = thumb.get('category')
        
        # Generate proper URL path
        thumb_path = Path(thumb['path'])
        try:
            # Try to get relative path from thumbnails directory
            rel_path = thumb_path.relative_to(Path('thumbnails').resolve())
            url = f'/thumbnails/{rel_path}'
        except ValueError:
            # Fallback: if path contains "thumbnails/", extract from there
            path_str = str(thumb_path)
            if 'thumbnails/' in path_str:
                rel_part = path_str.split('thumbnails/', 1)[1]
                url = f'/thumbnails/{rel_part}'
            else:
                # Last resort: just use filename
                url = f'/thumbnails/{thumb["filename"]}'
        
        thumbnail_obj = {
            'filename': thumb['filename'],
            'path': thumb['path'],
            'category': category,
            'url': url
        }
        
        if category:
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(thumbnail_obj)
        else:
            uncategorized.append(thumbnail_obj)
    
    # Sort within each category
    for category in categorized:
        categorized[category].sort(key=lambda x: x['filename'])
    uncategorized.sort(key=lambda x: x['filename'])
    
    return jsonify({
        'thumbnails': uncategorized,
        'categorized': categorized,
        'categories': categories
    })

@app.route('/api/search', methods=['POST'])
def search_thumbnails():
    """Search for similar thumbnails"""
    data = request.json
    topic = data.get('topic', '')
    pov = data.get('pov', '')
    
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    
    try:
        finder = init_finder()
        results = finder.find_similar(topic, pov if pov else None, top_k=3)
        
        # Add thumbnail URLs
        for result in results:
            thumb_path = Path(result['path'])
            try:
                # Try to get relative path from thumbnails directory
                rel_path = thumb_path.relative_to(Path('thumbnails').resolve())
                result['url'] = f'/thumbnails/{rel_path}'
            except ValueError:
                # Fallback: if path contains "thumbnails/", extract from there
                path_str = str(thumb_path)
                if 'thumbnails/' in path_str:
                    rel_part = path_str.split('thumbnails/', 1)[1]
                    result['url'] = f'/thumbnails/{rel_part}'
                else:
                    # Last resort: just use filename
                    result['url'] = f'/thumbnails/{thumb_path.name}'
        
        return jsonify({'results': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_thumbnail():
    """Analyze selected thumbnail"""
    data = request.json
    thumbnail_path = data.get('thumbnail_path', '')
    topic = data.get('topic', '')
    pov = data.get('pov', '')
    
    if not thumbnail_path or not topic:
        return jsonify({'error': 'Thumbnail path and topic are required'}), 400
    
    try:
        print(f"Analyzing: {thumbnail_path} for topic: {topic}")
        
        analyzer = ThumbnailAnalyzer()
        analysis = analyzer.analyze_thumbnail(
            thumbnail_path,
            topic,
            pov if pov else None
        )
        
        # Validate analysis structure
        if not analysis or not isinstance(analysis, dict):
            raise ValueError("Invalid analysis response from analyzer")
        
        # Ensure required keys exist
        if 'current_analysis' not in analysis:
            analysis['current_analysis'] = {}
        if 'suggested_modifications' not in analysis:
            analysis['suggested_modifications'] = {}
        if 'generation_prompt' not in analysis:
            analysis['generation_prompt'] = ''
        
        print(f"Analysis completed successfully")
        return jsonify({'analysis': analysis})
    
    except Exception as e:
        print(f"Error analyzing thumbnail: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-reference', methods=['POST'])
def upload_reference():
    """Upload manually selected reference image"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save to temp directory
        import uuid
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
        filename = f"manual_ref_{uuid.uuid4().hex[:8]}.{ext}"
        filepath = temp_dir / filename
        
        file.save(str(filepath))
        
        return jsonify({
            'success': True,
            'path': str(filepath)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-thumbnails', methods=['POST'])
def upload_thumbnails():
    """Upload new thumbnails to a specific category"""
    try:
        if 'thumbnails' not in request.files:
            return jsonify({'error': 'No thumbnail files provided'}), 400
        
        category = request.form.get('category')
        if not category:
            return jsonify({'error': 'No category specified'}), 400
        
        # Create category directory if it doesn't exist
        category_dir = Path("thumbnails") / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        files = request.files.getlist('thumbnails')
        uploaded = 0
        errors = []
        
        for file in files:
            if file.filename == '':
                continue
            
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                errors.append(f"{file.filename}: Invalid file type")
                continue
            
            # Generate unique filename
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
            if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                errors.append(f"{file.filename}: Unsupported extension")
                continue
            
            # Use original filename or generate unique one if exists
            original_name = file.filename.rsplit('.', 1)[0]
            filename = f"{original_name}.{ext}"
            filepath = category_dir / filename
            
            # If file exists, add UUID to make it unique
            if filepath.exists():
                filename = f"{original_name}_{uuid.uuid4().hex[:6]}.{ext}"
                filepath = category_dir / filename
            
            # Save file
            try:
                file.save(str(filepath))
                uploaded += 1
                print(f"✅ Uploaded: {filename}")
            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")
                print(f"⚠️ Failed to save: {file.filename} - {e}")
                continue
        
        if uploaded == 0:
            error_msg = 'No valid images were uploaded'
            if errors:
                error_msg += f". Errors: {'; '.join(errors[:3])}"
            return jsonify({'error': error_msg}), 400
        
        # Don't rebuild index immediately - too slow
        # The index will rebuild on next app restart or /api/all-thumbnails call
        
        response = {
            'success': True,
            'uploaded': uploaded,
            'category': category,
            'message': f'Successfully uploaded {uploaded} thumbnail(s) to {category}'
        }
        if errors:
            response['warnings'] = errors
        
        return jsonify(response), 200
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Upload error: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Upload failed: {error_msg}',
            'details': traceback.format_exc()
        }), 500

@app.route('/api/generate', methods=['POST'])
def generate_thumbnail():
    """Generate new thumbnail"""
    data = request.json
    prompt = data.get('prompt', '')
    service = data.get('service', 'dalle')
    topic = data.get('topic', 'thumbnail')
    reference_image = data.get('reference_image')  # Path to original thumbnail
    
    if not prompt:
        return jsonify({'error': 'Generation prompt is required'}), 400
    
    try:
        # Ensure generated_thumbnails directory exists
        Path('generated_thumbnails').mkdir(exist_ok=True)
        
        generator = ImageGenerator(service=service)
        
        # Create output filename
        output_filename = f"generated_{topic.replace(' ', '_').lower()}.png"
        output_path = f"generated_thumbnails/{output_filename}"
        
        print(f"Generating to: {output_path}")
        print(f"Reference image: {reference_image}")
        print(f"Service: {service}")
        
        # Validate and pass reference image
        if reference_image and isinstance(reference_image, str) and len(reference_image) > 0:
            # Check if file exists
            if Path(reference_image).exists():
                print(f"Using reference image: {reference_image}")
                generated_path = generator.generate(prompt, output_path, reference_image_path=reference_image)
            else:
                print(f"Warning: Reference image not found: {reference_image}, generating without it")
                generated_path = generator.generate(prompt, output_path)
        else:
            print("No reference image provided, generating from text only")
            generated_path = generator.generate(prompt, output_path)
        
        print(f"Generated path: {generated_path}")
        
        # Check if generation returned a valid path
        if generated_path is None:
            raise Exception("Image generation failed - no path returned from generator")
        
        if not isinstance(generated_path, str) or len(generated_path) == 0:
            raise Exception(f"Invalid path returned from generator: {generated_path}")
        
        # Verify file exists
        if not Path(generated_path).exists():
            raise Exception(f"File was not created at {generated_path}")
        
        return jsonify({
            'success': True,
            'path': generated_path,
            'url': f'/generated/{output_filename}'
        })
    
    except Exception as e:
        print(f"Error generating: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/gallery')
def get_gallery():
    """Get all generated thumbnails"""
    generated_dir = Path("generated_thumbnails")
    
    if not generated_dir.exists():
        return jsonify({'thumbnails': []})
    
    thumbnails = []
    for img_file in sorted(generated_dir.glob("*.png"), key=os.path.getmtime, reverse=True):
        thumbnails.append({
            'filename': img_file.name,
            'path': str(img_file),
            'url': f'/generated/{img_file.name}',
            'size': img_file.stat().st_size
        })
    
    return jsonify({'thumbnails': thumbnails})

@app.route('/thumbnails/<path:filepath>')
def serve_thumbnail(filepath):
    """Serve thumbnail images (supports subdirectories for categories)"""
    thumbnails_dir = Path('thumbnails')
    full_path = thumbnails_dir / filepath
    
    # Security check: ensure path is within thumbnails directory
    try:
        full_path.resolve().relative_to(thumbnails_dir.resolve())
    except ValueError:
        return jsonify({'error': 'Invalid path'}), 403
    
    if not full_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_from_directory(full_path.parent, full_path.name)

@app.route('/generated/<filename>')
def serve_generated(filename):
    """Serve generated images"""
    try:
        file_path = Path('generated_thumbnails') / filename
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
        
        print(f"Serving file: {file_path}")
        return send_from_directory('generated_thumbnails', filename)
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated thumbnail"""
    from pathlib import Path
    file_path = Path('generated_thumbnails') / filename
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    return send_file(
        str(file_path),
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    # Create directories if they don't exist
    Path('thumbnails').mkdir(exist_ok=True)
    Path('generated_thumbnails').mkdir(exist_ok=True)
    Path('templates').mkdir(exist_ok=True)
    Path('static').mkdir(exist_ok=True)
    
    print("\n" + "="*70)
    print("🎨 AI THUMBNAIL GENERATOR - WEB INTERFACE")
    print("="*70)
    print("\n🌐 Starting server...")
    
    # Use PORT from environment (for Railway/Heroku) or default to 5001
    port = int(os.environ.get('PORT', 5001))
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    if is_production:
        print(f"\n📍 Production mode - listening on port {port}")
    else:
        print(f"\n📍 Access your app at: http://localhost:{port}")
        print("\n💡 Press Ctrl+C to stop the server")
    
    print("="*70 + "\n")
    
    app.run(debug=not is_production, host='0.0.0.0', port=port)


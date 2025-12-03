"""
Image Generator - Generate thumbnails using various AI services
Primary: Google Imagen via Gemini API
"""

import os
import requests
import time
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


class ImageGenerator:
    """Generate images using different AI services"""
    
    def __init__(self, service: str = "freepik"):
        """
        Initialize image generator
        
        Args:
            service: Which service to use ('freepik', 'dalle', 'replicate', 'gemini', 'fal')
        """
        self.service = service.lower()
        
        if self.service == "freepik":
            self.api_key = os.getenv("FREEPIK_API_KEY")
            self.webhook_secret = os.getenv("FREEPIK_WEBHOOK_SECRET")
            if not self.api_key:
                raise ValueError("FREEPIK_API_KEY not found in environment")
            if not self.webhook_secret:
                print("Warning: FREEPIK_WEBHOOK_SECRET not set (optional for webhooks)")
        elif self.service == "dalle":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
        elif self.service == "gemini":
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment")
            genai.configure(api_key=self.api_key)
        elif self.service == "replicate":
            self.api_key = os.getenv("REPLICATE_API_TOKEN")
            if not self.api_key:
                raise ValueError("REPLICATE_API_TOKEN not found in environment")
        elif self.service == "fal":
            self.api_key = os.getenv("FAL_KEY")
            if not self.api_key:
                raise ValueError("FAL_KEY not found in environment")
        else:
            raise ValueError(f"Unsupported service: {service}")
    
    def generate_gemini(self, prompt: str, output_path: str, reference_image_path: str = None) -> str:
        """
        Generate image using Google's Gemini 2.5 Flash Image (Nano Banana)
        Requires GOOGLE_API_KEY from Google AI Studio
        """
        import requests
        import base64
        import google.generativeai as genai
        import os
        
        # CRITICAL: Validate reference_image_path at the very start
        if reference_image_path:
            # Check if it's a valid string
            if not isinstance(reference_image_path, str) or len(reference_image_path.strip()) == 0:
                print(f"⚠️  Invalid reference_image_path type: {type(reference_image_path)}, resetting to None")
                reference_image_path = None
            # Check if file exists
            elif not os.path.exists(reference_image_path):
                print(f"⚠️  Reference image file not found: {reference_image_path}, resetting to None")
                reference_image_path = None
        
        # Enhanced prompt for thumbnail format
        enhanced_prompt = f"""Create a professional YouTube thumbnail (16:9 aspect ratio): {prompt}

Style requirements:
- High quality, professional design
- Eye-catching and engaging
- Clear, bold visual elements
- Suitable for YouTube platform
- 16:9 landscape format
- Modern and polished aesthetic

Avoid: podcast microphones, headphones, podcast studio setup"""

        print(f"\n{'='*70}")
        print(f"🍌 GENERATING WITH GEMINI 2.0 FLASH PRO (Nano Banana Pro)")
        print(f"{'='*70}")
        if reference_image_path:
            print(f"   Reference: {reference_image_path}")
        else:
            print(f"   Reference: None (text-to-image mode)")
        print(f"   Prompt: {enhanced_prompt[:100]}...")
        print(f"{'='*70}\n")
        
        # Try multiple models in order of preference
        models_to_try = [
            'gemini-2.5-flash-image',
            'gemini-2.5-flash-image-preview',
            'gemini-2.0-flash-preview-image-generation',
        ]
        
        for model_name in models_to_try:
            try:
                # Configure Gemini with API key
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(model_name)
                
                print(f"📡 Trying {model_name} model...")
                
                # Generate image
                if reference_image_path and isinstance(reference_image_path, str) and len(reference_image_path.strip()) > 0:
                    # With reference image for editing
                    print(f"   Editing mode with reference image...")
                    from PIL import Image as PILImage
                    import os
                    
                    # Verify file exists before trying to open
                    if not os.path.exists(reference_image_path):
                        print(f"   Warning: Reference image not found: {reference_image_path}")
                        print(f"   Falling back to text-to-image mode...")
                        response = model.generate_content(enhanced_prompt)
                    else:
                        try:
                            ref_image = PILImage.open(reference_image_path)
                            
                            # Create editing prompt
                            edit_prompt = f"Edit this image to: {enhanced_prompt}"
                            
                            response = model.generate_content([edit_prompt, ref_image])
                        except Exception as img_error:
                            print(f"   Error loading reference image: {img_error}")
                            print(f"   Falling back to text-to-image mode...")
                            response = model.generate_content(enhanced_prompt)
                else:
                    # Text-to-image generation
                    print(f"   Text-to-image mode...")
                    response = model.generate_content(enhanced_prompt)
                
                # Save the generated image
                if hasattr(response, 'image') and response.image:
                    response.image.save(output_path)
                    print(f"\n✅ SUCCESS with Gemini 2.0 Flash Pro ({model_name})!")
                    print(f"✓ Image saved: {output_path}")
                    return output_path
                elif hasattr(response, 'parts') and len(response.parts) > 0:
                    # Extract image from parts
                    for part in response.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            img_data = part.inline_data.data
                            with open(output_path, 'wb') as f:
                                f.write(img_data)
                            print(f"\n✅ SUCCESS with Gemini 2.0 Flash Pro ({model_name})!")
                            print(f"✓ Image saved: {output_path}")
                            return output_path
                    # If we get here, parts existed but had no image data
                    print(f"   ⚠️  {model_name} returned response without image data, trying next model...")
                    continue
                else:
                    print(f"   ⚠️  {model_name} returned no image, trying next model...")
                    continue
                    
            except Exception as e:
                print(f"\n❌ {model_name} failed: {str(e)}")
                if model_name == models_to_try[-1]:
                    # Last model failed, continue to REST API fallback
                    print(f"   All SDK models failed, trying REST API...")
                else:
                    continue  # Try next model
        
        # If we're here, all SDK models failed - try REST API
        print(f"\n🔄 All SDK models failed, trying REST API fallback...")
        
        # Try multiple working models
        endpoints_to_try = [
                {
                    "name": "Gemini 2.5 Flash Image",
                    "model": "gemini-2.5-flash-image"
                },
                {
                    "name": "Gemini 2.5 Flash Image Preview",
                    "model": "gemini-2.5-flash-image-preview"
                },
                {
                    "name": "Gemini 2.0 Flash Image Generation",
                    "model": "gemini-2.0-flash-preview-image-generation"
                },
                {
                    "name": "Gemini Exp 1206",
                    "model": "gemini-exp-1206"
                }
        ]
        
        last_error = None
        
        for endpoint_config in endpoints_to_try:
            try:
                print(f"\n📡 Trying {endpoint_config['name']}...")
                
                # Prepare payload for Gemini REST API
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{endpoint_config['model']}:generateContent?key={self.api_key}"
                
                # Build content parts
                content_parts = []
                
                # Validate reference image path before using
                use_reference = False
                if reference_image_path and isinstance(reference_image_path, str) and len(reference_image_path.strip()) > 0:
                    import os
                    if os.path.exists(reference_image_path):
                        use_reference = True
                    else:
                        print(f"   Warning: Reference image not found: {reference_image_path}")
                
                if use_reference:
                    try:
                        # Add reference image
                        with open(reference_image_path, 'rb') as f:
                            img_base64 = base64.b64encode(f.read()).decode('utf-8')
                        
                        content_parts.append({
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_base64
                            }
                        })
                        content_parts.append({
                            "text": f"Edit this image to: {enhanced_prompt}"
                        })
                        print(f"   Using reference image in REST API call")
                    except Exception as ref_error:
                        print(f"   Error reading reference image: {ref_error}")
                        # Fall back to text-only
                        content_parts.append({
                            "text": enhanced_prompt
                        })
                else:
                    # Text-only
                    print(f"   Text-only mode (no reference)")
                    content_parts.append({
                        "text": enhanced_prompt
                    })
                
                payload = {
                    "contents": [{
                        "parts": content_parts
                    }]
                }
                
                headers = {
                    "Content-Type": "application/json",
                }
                
                # Make request
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                
                print(f"   Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Parse Gemini response format
                    image_data = None
                    
                    # Gemini format: candidates -> content -> parts -> inline_data
                    if "candidates" in result and len(result["candidates"]) > 0:
                        candidate = result["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            parts = candidate["content"]["parts"]
                            for part in parts:
                                if "inline_data" in part:
                                    image_data = part["inline_data"]["data"]
                                    break
                    
                    if image_data:
                        # Decode and save
                        try:
                            img_bytes = base64.b64decode(image_data)
                            with open(output_path, "wb") as f:
                                f.write(img_bytes)
                            
                            print(f"\n✅ SUCCESS with Gemini 2.0 Flash Pro ({endpoint_config['name']})!")
                            print(f"✓ Image saved: {output_path}")
                            return output_path
                        except Exception as decode_error:
                            print(f"   ❌ Error decoding image: {decode_error}")
                            last_error = f"Failed to decode image: {decode_error}"
                    else:
                        print(f"   ⚠️  No image in response")
                        print(f"   Response keys: {list(result.keys())}")
                        if "candidates" in result and len(result["candidates"]) > 0:
                            print(f"   Candidate keys: {list(result['candidates'][0].keys())}")
                        last_error = f"No image data in response"
                
                elif response.status_code == 404:
                    print(f"   ⚠️  Endpoint not available (404)")
                    last_error = f"{endpoint_config['name']} not available"
                    continue
                
                elif response.status_code == 403:
                    error_text = response.text
                    print(f"   ❌ Permission denied (403)")
                    print(f"   Error: {error_text}")
                    
                    if "API key not valid" in error_text:
                        raise Exception(f"❌ GOOGLE_API_KEY is invalid. Please check your API key in .env file")
                    elif "Imagen" in error_text or "image generation" in error_text.lower():
                        print(f"\n   💡 Imagen API might not be enabled for your API key")
                        last_error = "Imagen API not enabled"
                        continue
                    else:
                        raise Exception(f"Permission denied: {error_text}")
                
                else:
                    error_text = response.text
                    print(f"   ❌ Error {response.status_code}: {error_text[:200]}")
                    last_error = f"{endpoint_config['name']} failed: {error_text[:100]}"
                    continue
                    
            except requests.exceptions.Timeout:
                print(f"   ⏱️  Request timed out")
                last_error = f"{endpoint_config['name']} timed out"
                continue
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                last_error = str(e)
                continue
            
        # All endpoints failed - try without reference image if we had one
        if reference_image_path:
            print(f"\n{'='*70}")
            print(f"⚠️  GEMINI IMAGE GENERATION - IMG2IMG FAILED WITH ALL MODELS")
            print(f"{'='*70}")
            print(f"Error: {last_error}")
            print(f"\n🔄 RETRYING WITHOUT REFERENCE IMAGE (text-to-image mode)...")
            print(f"{'='*70}\n")
            
            # Retry without reference image
            return self.generate_gemini(enhanced_prompt, output_path, reference_image_path=None)
        else:
            # Complete failure
            print(f"\n{'='*70}")
            print(f"❌ GEMINI IMAGE GENERATION COMPLETELY FAILED")
            print(f"{'='*70}")
            print(f"Models tried: {', '.join(models_to_try)}")
            print(f"Last error: {last_error}")
            print(f"\n💡 SOLUTIONS:")
            print(f"   1. Try DALL-E 3 - it uses GPT-4o Vision for image-to-image")
            print(f"   2. Check your Google API key has Imagen/Image Generation enabled")
            print(f"   3. Verify you haven't hit quota limits in Google Cloud Console")
            print(f"{'='*70}\n")
            
            raise Exception(f"Gemini image generation failed with all models. Last error: {last_error}. Try DALL-E 3 or check your API key permissions.")
    
    def generate_freepik(self, prompt: str, output_path: str, reference_image_path: str = None) -> str:
        """Generate image using Freepik API with or without reference image"""
        import os
        
        # CRITICAL: Validate reference_image_path
        if reference_image_path:
            if not isinstance(reference_image_path, str) or len(reference_image_path.strip()) == 0:
                print(f"⚠️  Invalid reference_image_path, resetting to None")
                reference_image_path = None
            elif not os.path.exists(reference_image_path):
                print(f"⚠️  Reference image not found: {reference_image_path}, resetting to None")
                reference_image_path = None
        
        # If reference image provided, try Freepik's reimagine or use enhanced text-to-image
        if reference_image_path:
            print(f"\n{'='*70}")
            print(f"🎨 FREEPIK WITH REFERENCE IMAGE")
            print(f"{'='*70}")
            print(f"   Reference: {reference_image_path}")
            print(f"   Prompt: {prompt}")
            print(f"{'='*70}\n")
            
            # Try Freepik reimagine endpoint first
            try:
                result = self._freepik_with_reference(prompt, output_path, reference_image_path)
                print(f"\n✅ SUCCESS: Freepik used reference image!")
                return result
            except Exception as e:
                print(f"\n{'='*70}")
                print(f"❌ FREEPIK REFERENCE GENERATION FAILED")
                print(f"{'='*70}")
                print(f"Error: {str(e)}")
                print(f"{'='*70}\n")
                
                # DO NOT fall back - raise the error so user knows Freepik can't handle reference images
                raise Exception(f"Freepik cannot process reference images: {str(e)}. Please use DALL-E or Replicate instead.")
        
        # Use Freepik text-to-image
        url = "https://api.freepik.com/v1/ai/text-to-image"
        
        headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # For text-to-image (no reference), create a new thumbnail from scratch
        enhanced_prompt = f"Create a professional YouTube thumbnail (16:9 landscape format, 1920x1080): {prompt}. High quality, eye-catching design. Bold colors, modern aesthetic, engaging visual elements. Professional YouTube thumbnail style."
        
        # Freepik API payload
        payload = {
            "prompt": enhanced_prompt,
            "negative_prompt": "blurry, low quality, distorted, ugly, bad anatomy, podcast microphone, headphones",
            "guidance_scale": 7.5,
            "num_images": 1,
            "image": {
                "size": "landscape_16_9"  # 1920x1080
            },
            "styling": {
                "style": "photo",  # Can be: photo, digital-art, 3d, painting, etc.
                "color": "vibrant",
                "lightning": "dramatic"
            }
        }
        
        print(f"\nGenerating image with Freepik AI...")
        print(f"Prompt: {enhanced_prompt}")
        
        try:
            # Create generation request
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # Freepik returns the image data or a job ID
            if "data" in result:
                image_data = result["data"]
                
                # Check if it's immediate response with image
                if isinstance(image_data, list) and len(image_data) > 0:
                    image_info = image_data[0]
                    
                    # Could be base64 or URL
                    if "base64" in image_info:
                        import base64
                        img_data = base64.b64decode(image_info["base64"])
                        with open(output_path, "wb") as f:
                            f.write(img_data)
                        print(f"✓ Image generated successfully: {output_path}")
                        return output_path
                    
                    elif "url" in image_info:
                        # Download from URL
                        img_response = requests.get(image_info["url"])
                        img_response.raise_for_status()
                        with open(output_path, "wb") as f:
                            f.write(img_response.content)
                        print(f"✓ Image generated successfully: {output_path}")
                        return output_path
                
                # If it's a job ID, poll for completion
                elif "id" in image_data or "job_id" in image_data:
                    job_id = image_data.get("id") or image_data.get("job_id")
                    return self._poll_freepik_job(job_id, output_path, headers)
            
            # Try alternative API response format
            if "id" in result or "job_id" in result:
                job_id = result.get("id") or result.get("job_id")
                return self._poll_freepik_job(job_id, output_path, headers)
            
            raise Exception(f"Unexpected API response format: {result}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error generating image with Freepik: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    def _poll_freepik_job(self, job_id: str, output_path: str, headers: dict) -> str:
        """Poll Freepik job status until completion"""
        status_url = f"https://api.freepik.com/v1/ai/text-to-image/{job_id}"
        
        print(f"Polling job {job_id}...")
        
        max_attempts = 60
        for attempt in range(max_attempts):
            try:
                response = requests.get(status_url, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                status = result.get("status", "").lower()
                
                if status == "completed" or status == "success":
                    # Extract image URL or data
                    if "data" in result and isinstance(result["data"], list):
                        image_info = result["data"][0]
                        
                        if "url" in image_info:
                            img_response = requests.get(image_info["url"])
                            img_response.raise_for_status()
                            with open(output_path, "wb") as f:
                                f.write(img_response.content)
                            print(f"✓ Image generated successfully: {output_path}")
                            return output_path
                        
                        elif "base64" in image_info:
                            import base64
                            img_data = base64.b64decode(image_info["base64"])
                            with open(output_path, "wb") as f:
                                f.write(img_data)
                            print(f"✓ Image generated successfully: {output_path}")
                            return output_path
                    
                    raise Exception("Image URL not found in completed job")
                
                elif status == "failed" or status == "error":
                    error_msg = result.get("error", result.get("message", "Unknown error"))
                    raise Exception(f"Generation failed: {error_msg}")
                
                if attempt % 5 == 0:
                    print(f"  Generating... ({attempt + 1}/{max_attempts})")
                
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2)
        
        raise Exception("Generation timed out")
    
    def _freepik_with_reference(self, prompt: str, output_path: str, reference_image_path: str) -> str:
        """Try Freepik with reference image using various endpoints"""
        import base64
        
        # Read and encode the reference image
        with open(reference_image_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Enhanced prompt that emphasizes modifying the attached image
        enhanced_prompt = f"Modify the attached image and create a YouTube thumbnail by making these changes: {prompt}. Keep the same layout and composition, only change the specified elements. Maintain professional YouTube thumbnail quality at 16:9 aspect ratio."
        
        # Try different Freepik endpoints in order
        endpoints = [
            {
                "name": "Reimagine",
                "url": "https://api.freepik.com/v1/ai/reimagine",
                "payload": {
                    "image": image_base64,
                    "prompt": enhanced_prompt,
                    "num_images": 1
                }
            },
            {
                "name": "Image Variations",
                "url": "https://api.freepik.com/v1/ai/image-variations",
                "payload": {
                    "image": image_base64,
                    "prompt": enhanced_prompt,
                    "num_variations": 1
                }
            }
        ]
        
        for endpoint in endpoints:
            try:
                print(f"\n   📡 Trying Freepik {endpoint['name']}...", flush=True)
                print(f"   URL: {endpoint['url']}", flush=True)
                print(f"   Payload keys: {list(endpoint['payload'].keys())}", flush=True)
                print(f"   Image size: {len(endpoint['payload']['image'])} bytes (base64)", flush=True)
                
                response = requests.post(
                    endpoint["url"],
                    json=endpoint["payload"],
                    headers=headers,
                    timeout=30
                )
                
                print(f"   Response Status: {response.status_code}", flush=True)
                print(f"   Response Headers: {dict(response.headers)}", flush=True)
                print(f"   Response Body: {response.text[:500]}", flush=True)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ {endpoint['name']} SUCCESS!", flush=True)
                    return self._extract_freepik_image(result, output_path)
                elif response.status_code in [404, 501]:
                    print(f"   ⚠️  {endpoint['name']} not available (status {response.status_code})", flush=True)
                    continue
                else:
                    print(f"   ❌ {endpoint['name']} returned {response.status_code}", flush=True)
                    print(f"   Error: {response.text}", flush=True)
                    continue
                    
            except Exception as e:
                print(f"   ❌ {endpoint['name']} exception: {str(e)}", flush=True)
                import traceback
                traceback.print_exc()
                continue
        
        # All endpoints failed
        raise Exception("All Freepik reference-based endpoints failed. Using text-to-image instead.")
    
    def _generate_freepik_style_transfer(self, prompt: str, output_path: str, reference_image_path: str) -> str:
        """Use Freepik Reimagine to modify existing thumbnail"""
        import base64
        
        print(f"\n🎨 Generating with Freepik Reimagine (fallback to text-to-image with context)...")
        print(f"   Reference image: {reference_image_path}")
        print(f"   Modifications: {prompt}")
        
        # Freepik's image-style-transfer endpoint may not be available
        # Try reimagine endpoint or fallback to text-to-image with detailed prompt
        
        # Read and encode the reference image
        with open(reference_image_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Try reimagine endpoint first
        url = "https://api.freepik.com/v1/ai/reimagine"
        
        headers = {
            "x-freepik-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Enhanced prompt for modifications  
        modification_prompt = f"{prompt}. Keep similar layout and composition to the reference image."
        
        payload = {
            "image": image_base64,
            "prompt": modification_prompt,
            "negative_prompt": "blurry, low quality, distorted, completely different, podcast microphone, headphones",
            "num_images": 1
        }
        
        try:
            # Submit request
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # Get task_id
            task_id = result.get('task_id') or result.get('id')
            
            if not task_id:
                # Try immediate response format
                if "data" in result or "output" in result:
                    return self._extract_freepik_image(result, output_path)
                raise Exception(f"No task_id in response: {result}")
            
            print(f"   Task ID: {task_id}")
            print(f"   Polling for completion...")
            
            # Poll for completion
            return self._poll_freepik_task(task_id, output_path, headers)
            
        except requests.exceptions.RequestException as e:
            print(f"Error with Freepik Style Transfer: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    def _poll_freepik_task(self, task_id: str, output_path: str, headers: dict) -> str:
        """Poll Freepik task until completion"""
        status_url = f"https://api.freepik.com/v1/ai/image-style-transfer/{task_id}"
        
        max_attempts = 60
        for attempt in range(max_attempts):
            try:
                response = requests.get(status_url, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                status = result.get("status", "").lower()
                
                if status == "completed" or status == "success":
                    return self._extract_freepik_image(result, output_path)
                
                elif status == "failed" or status == "error":
                    error_msg = result.get("error", result.get("message", "Unknown error"))
                    raise Exception(f"Generation failed: {error_msg}")
                
                if attempt % 5 == 0:
                    print(f"   Processing... ({attempt + 1}/{max_attempts})")
                
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2)
        
        raise Exception("Generation timed out")
    
    def _extract_freepik_image(self, result: dict, output_path: str) -> str:
        """Extract and download image from Freepik response"""
        import base64
        
        # Try different response formats
        image_data = result.get("data") or result.get("output") or result.get("result")
        
        if isinstance(image_data, list) and len(image_data) > 0:
            image_info = image_data[0]
        elif isinstance(image_data, dict):
            image_info = image_data
        else:
            raise Exception(f"Unexpected response format: {result}")
        
        # Check for URL
        if "url" in image_info:
            img_response = requests.get(image_info["url"])
            img_response.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(img_response.content)
            print(f"✓ Image generated successfully: {output_path}")
            return output_path
        
        # Check for base64
        elif "base64" in image_info:
            img_data = base64.b64decode(image_info["base64"])
            with open(output_path, "wb") as f:
                f.write(img_data)
            print(f"✓ Image generated successfully: {output_path}")
            return output_path
        
        raise Exception(f"No image URL or base64 found in response: {image_info}")
    
    def generate_replicate(self, prompt: str, output_path: str, reference_image_path: str = None) -> str:
        """Generate image using Replicate (FLUX Pro or SDXL) with optional img2img"""
        import base64
        import os
        
        # CRITICAL: Validate reference_image_path
        if reference_image_path:
            if not isinstance(reference_image_path, str) or len(reference_image_path.strip()) == 0:
                print(f"⚠️  Invalid reference_image_path, resetting to None")
                reference_image_path = None
            elif not os.path.exists(reference_image_path):
                print(f"⚠️  Reference image not found: {reference_image_path}, resetting to None")
                reference_image_path = None
        
        url = "https://api.replicate.com/v1/predictions"
        
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        
        enhanced_prompt = f"YouTube thumbnail style, 16:9 landscape format: {prompt}. Professional, high quality, eye-catching design. Bold text, vibrant colors, modern aesthetic"
        
        # Prepare image input if reference provided
        image_input = None
        if reference_image_path:
            print(f"   Using image-to-image with reference: {reference_image_path}")
            with open(reference_image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
                image_input = f"data:image/jpeg;base64,{image_data}"
        
        # Use FLUX Dev (supports img2img better) or SDXL with img2img support
        # Try FLUX first, fallback to SDXL if needed
        models = [
            {
                "name": "FLUX Dev" + (" (img2img)" if image_input else ""),
                "version": "black-forest-labs/flux-dev",
                "input": {
                    "prompt": enhanced_prompt,
                    "aspect_ratio": "16:9",
                    "num_outputs": 1,
                    "output_format": "png",
                    "output_quality": 90,
                    **({"image": image_input, "prompt_strength": 0.75} if image_input else {})
                }
            },
            {
                "name": "SDXL" + (" (img2img)" if image_input else ""),
                "version": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                "input": {
                    "prompt": enhanced_prompt,
                    "width": 1280,
                    "height": 720,
                    "num_outputs": 1,
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5,
                    "scheduler": "K_EULER",
                    **({"image": image_input, "prompt_strength": 0.8} if image_input else {})
                }
            }
        ]
        
        last_error = None
        
        for model_config in models:
            try:
                print(f"\nGenerating image with Replicate ({model_config['name']})...")
                print(f"Prompt: {enhanced_prompt}")
                
                payload = {
                    "version": model_config["version"],
                    "input": model_config["input"]
                }
                
                # Create prediction
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                prediction_id = result["id"]
                get_url = f"{url}/{prediction_id}"
                
                # Poll for completion
                max_attempts = 60
                for attempt in range(max_attempts):
                    response = requests.get(get_url, headers=headers)
                    response.raise_for_status()
                    result = response.json()
                    
                    status = result["status"]
                    if status == "succeeded":
                        output_data = result.get("output")
                        
                        # Handle different output formats
                        if isinstance(output_data, list):
                            output_url = output_data[0]
                        elif isinstance(output_data, str):
                            output_url = output_data
                        else:
                            raise Exception(f"Unexpected output format: {output_data}")
                        
                        # Download image
                        img_response = requests.get(output_url)
                        img_response.raise_for_status()
                        
                        with open(output_path, "wb") as f:
                            f.write(img_response.content)
                        
                        print(f"✓ Image generated successfully with {model_config['name']}: {output_path}")
                        return output_path
                    elif status == "failed":
                        error_msg = result.get('error', 'Unknown error')
                        print(f"✗ {model_config['name']} failed: {error_msg}")
                        raise Exception(f"Generation failed: {error_msg}")
                    
                    if attempt % 5 == 0:
                        print(f"  Generating... ({attempt + 1}/{max_attempts})")
                    time.sleep(2)
                
                raise Exception("Generation timed out")
                
            except Exception as e:
                last_error = e
                print(f"✗ Failed with {model_config['name']}: {str(e)}")
                if model_config == models[-1]:
                    # Last model, re-raise error
                    if hasattr(e, 'response') and e.response:
                        print(f"Response: {e.response.text}")
                    raise
                else:
                    print(f"Trying next model...")
                    continue
        
        raise last_error
    
    def generate_dalle(self, prompt: str, output_path: str, reference_image_path: str = None) -> str:
        """Generate image using OpenAI DALL-E 3 with image context"""
        from openai import OpenAI
        from PIL import Image
        import io
        import os
        
        client = OpenAI(api_key=self.api_key)
        
        # CRITICAL: Validate reference_image_path at the very start
        if reference_image_path:
            # Check if it's a valid string
            if not isinstance(reference_image_path, str) or len(reference_image_path.strip()) == 0:
                print(f"⚠️  Invalid reference_image_path type: {type(reference_image_path)}, resetting to None")
                reference_image_path = None
            # Check if file exists
            elif not os.path.exists(reference_image_path):
                print(f"⚠️  Reference image file not found: {reference_image_path}, resetting to None")
                reference_image_path = None
        
        # Now proceed with validated reference_image_path (will be None if invalid)
        if reference_image_path:
            print(f"\n🎨 Analyzing original thumbnail with GPT-4 Vision for context...")
            print(f"   Reference: {reference_image_path}")
            
            try:
                import base64
                with open(reference_image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                
                # Get detailed description of original using GPT-4o (better vision)
                vision_response = client.chat.completions.create(
                    model="gpt-4o",  # Better vision model
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this YouTube thumbnail in extreme detail:
1. Overall layout and composition (what's on left/right/center/top/bottom)
2. All visual elements and their exact positions
3. Text content, font styles, and placement
4. Color scheme and gradients
5. Background elements and style
6. Any people, objects, or graphics
7. Overall aesthetic and design style

Be extremely specific about spatial positions and visual hierarchy."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}",
                                    "detail": "high"  # High detail analysis
                                }
                            }
                        ]
                    }],
                    max_tokens=800
                )
                
                original_description = vision_response.choices[0].message.content
                print(f"   Original thumbnail analyzed in detail ✓")
                
                # Enhance prompt with original context
                enhanced_prompt = f"""Create a YouTube thumbnail (16:9, 1792x1024) by RECREATING this exact layout with modifications:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ORIGINAL DESIGN TO REPLICATE:
{original_description}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SPECIFIC CHANGES TO MAKE:
{prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL INSTRUCTIONS:
- KEEP the exact same layout structure and composition
- KEEP the same spatial arrangement (left/right/top/bottom positions)
- KEEP the same text placement and font styles
- ONLY change the elements specifically mentioned above
- Maintain professional YouTube thumbnail quality
- DO NOT create a completely new design
- RECREATE the original layout with ONLY the specified modifications"""
                
            except Exception as e:
                print(f"   Warning: Could not analyze original image: {e}")
                print(f"   Falling back to text-only generation")
                enhanced_prompt = f"YouTube thumbnail style, 16:9 aspect ratio: {prompt}. Professional, high quality, eye-catching, modern design"
        else:
            enhanced_prompt = f"YouTube thumbnail style, 16:9 aspect ratio: {prompt}. Professional, high quality, eye-catching, modern design"
        
        print(f"\nGenerating image with DALL-E 3...")
        print(f"Prompt length: {len(enhanced_prompt)} characters")
        
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt[:4000],  # DALL-E 3 has prompt length limit
                size="1792x1024",  # Close to 16:9
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
            # Download image
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            with open(output_path, "wb") as f:
                f.write(img_response.content)
            
            print(f"✓ Image generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating image: {e}")
            raise
    
    def generate_fal(self, prompt: str, output_path: str, reference_image_path: str = None) -> str:
        """
        Generate image using FAL.AI FLUX Pro (Best img2img quality)
        https://fal.ai/models/fal-ai/flux-pro/v1.1-ultra
        """
        import base64
        import os
        
        # CRITICAL: Validate reference_image_path
        if reference_image_path:
            if not isinstance(reference_image_path, str) or len(reference_image_path.strip()) == 0:
                print(f"⚠️  Invalid reference_image_path, resetting to None")
                reference_image_path = None
            elif not os.path.exists(reference_image_path):
                print(f"⚠️  Reference image not found: {reference_image_path}, resetting to None")
                reference_image_path = None
        
        enhanced_prompt = f"YouTube thumbnail style, 16:9 landscape format: {prompt}. Professional, high quality, eye-catching design. Bold elements, vibrant colors, modern aesthetic"
        
        print(f"\n{'='*70}")
        print(f"🚀 GENERATING WITH FAL.AI FLUX PRO")
        print(f"{'='*70}")
        if reference_image_path:
            print(f"   Reference: {reference_image_path}")
            print(f"   Mode: Image-to-Image modification")
        print(f"   Prompt: {enhanced_prompt[:100]}...")
        print(f"{'='*70}\n")
        
        try:
            import fal_client
            
            # Prepare arguments
            arguments = {
                "prompt": enhanced_prompt,
                "image_size": "landscape_16_9",
                "num_inference_steps": 40,
                "guidance_scale": 3.5,
                "num_images": 1,
                "enable_safety_checker": False,
                "output_format": "png"
            }
            
            # Add reference image if provided (img2img)
            if reference_image_path:
                # Upload reference image to FAL
                print("   Uploading reference image to FAL...")
                with open(reference_image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                    image_url = f"data:image/jpeg;base64,{image_data}"
                
                arguments["image_url"] = image_url
                arguments["strength"] = 0.75  # How much to modify (0-1, higher = more change)
                print("   ✓ Reference uploaded")
            
            print("   Generating with FLUX Pro...")
            
            # Submit to FAL
            result = fal_client.subscribe(
                "fal-ai/flux-pro/v1.1-ultra",
                arguments=arguments,
                with_logs=True,
                on_queue_update=lambda update: print(f"   Queue position: {update.get('position', 'N/A')}") if 'position' in update else None,
            )
            
            # Get image URL from result
            if result and "images" in result and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                
                # Download image
                print(f"   Downloading generated image...")
                img_response = requests.get(image_url)
                img_response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(img_response.content)
                
                print(f"\n✅ SUCCESS with FAL.AI FLUX Pro!")
                print(f"✓ Image saved: {output_path}")
                return output_path
            else:
                raise Exception(f"Unexpected result format: {result}")
                
        except ImportError:
            print(f"\n❌ FAL Python client not installed!")
            print(f"   Install with: pip install fal-client")
            raise Exception("fal-client not installed. Run: pip install fal-client")
        except Exception as e:
            print(f"\n❌ FAL.AI generation failed: {e}")
            raise
    
    def generate(self, prompt: str, output_path: str, reference_image_path: str = None) -> str:
        """Generate image using configured service"""
        if self.service == "freepik":
            return self.generate_freepik(prompt, output_path, reference_image_path)
        elif self.service == "dalle":
            return self.generate_dalle(prompt, output_path, reference_image_path)
        elif self.service == "gemini":
            return self.generate_gemini(prompt, output_path, reference_image_path)
        elif self.service == "replicate":
            return self.generate_replicate(prompt, output_path, reference_image_path)
        elif self.service == "fal":
            return self.generate_fal(prompt, output_path, reference_image_path)
        else:
            raise ValueError(f"Unsupported service: {self.service}")

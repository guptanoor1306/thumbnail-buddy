"""
Thumbnail Analyzer - AI-powered visual analysis and modification suggestions
Uses OpenAI GPT-4 Vision for analysis
"""

import os
import base64
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ThumbnailAnalyzer:
    """Analyzes thumbnails and suggests modifications using GPT-4 Vision"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = OpenAI(api_key=api_key)
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_thumbnail(
        self, 
        image_path: str, 
        new_topic: str,
        new_pov: Optional[str] = None
    ) -> Dict:
        """
        Analyze thumbnail and suggest modifications for new topic
        
        Args:
            image_path: Path to the selected thumbnail
            new_topic: The new topic for the thumbnail
            new_pov: Optional point of view for the new thumbnail
            
        Returns:
            Dictionary with analysis and modification suggestions
        """
        base64_image = self._encode_image(image_path)
        
        # Create prompt
        pov_context = f" from {new_pov} perspective" if new_pov else ""
        
        prompt = f"""You are a YouTube thumbnail strategist. Your goal is to analyze this outlier thumbnail and suggest visual modifications that maximize curiosity and CTR (Click-Through Rate) for a new topic.

🎯 NEW TOPIC: {new_topic}{pov_context}

📋 CRITICAL RULES:
1. ✅ MUST include a human face (expressive, emotional, relatable)
2. ❌ NO podcast elements (microphones, headphones, podcast setups)
3. ❌ NOT a simple poster - must have depth, emotion, and intrigue
4. ✅ Focus on psychological triggers: curiosity, emotion, surprise, relatability
5. ✅ Think YouTube success, not graphic design perfection

🔍 ANALYSIS FRAMEWORK:
Analyze the current thumbnail considering:
- Face prominence and emotional expression
- Background and setting relevance
- Color psychology and contrast
- Text readability and curiosity gap
- Visual symbols that create intrigue
- Overall composition and flow

💡 MODIFICATION STRATEGY:
For the new topic "{new_topic}", suggest changes that:
- Maintain the successful elements of the original
- Adapt the emotional tone to match the new topic
- Use visual metaphors and symbols specific to the topic
- Create a curiosity gap that makes viewers NEED to click
- Ensure the face conveys the right emotion for the topic

Provide your analysis in this EXACT JSON format:

{{
  "current_analysis": {{
    "face_presence": "Describe if there's a face, its expression, and prominence",
    "background": "What's the setting/background and its effectiveness",
    "color_psychology": "Colors used and the emotions they evoke",
    "text_strategy": "Text content, style, and how it creates curiosity",
    "visual_symbols": "Key symbols, props, or elements that add meaning",
    "overall_effectiveness": "What makes this thumbnail successful"
  }},
  "suggested_modifications": {{
    "face_expression": "What facial expression and emotion to show for '{new_topic}'",
    "background_change": "Specific background setting that matches the new topic (be detailed: lighting, environment, props)",
    "color_tone_shift": "Exact color palette changes and WHY they work for this topic",
    "text_update": "New text that creates curiosity - be specific about wording and placement",
    "symbolic_additions": "Specific visual symbols, props, or overlays that reinforce the topic's theme",
    "layout_adjustments": "Changes to composition, face size, element positioning for maximum impact"
  }},
  "psychological_reasoning": {{
    "curiosity_trigger": "How these changes create a curiosity gap",
    "emotional_resonance": "What emotion viewers will feel and why they'll click",
    "relatability_factor": "How this makes viewers think 'this is about me'"
  }},
  "generation_prompt": "Create a YouTube thumbnail by MODIFYING the existing design. FOR TOPIC: '{new_topic}'. CRITICAL: Include an expressive human face showing [emotion from face_expression]. Background: [detailed background from background_change]. Colors: [specific palette from color_tone_shift]. Text: [exact text from text_update]. Add these symbols: [items from symbolic_additions]. Layout: [adjustments from layout_adjustments]. The thumbnail must look like a successful YouTube thumbnail - emotional, intriguing, NOT a poster. Maintain the energy and composition style of the original while completely adapting the content for the new topic. NO microphones, NO podcast elements."
}}

Provide ONLY the JSON response, no additional text."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # GPT-4 with vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            
            # Extract JSON from response
            import json
            content = response.choices[0].message.content
            
            # Try to parse JSON (handle potential markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            raise
    
    def display_analysis(self, analysis: Dict) -> None:
        """Display analysis results in a readable format"""
        print("\n" + "="*70)
        print("CURRENT THUMBNAIL ANALYSIS")
        print("="*70)
        
        current = analysis.get("current_analysis", {})
        for key, value in current.items():
            print(f"\n{key.upper().replace('_', ' ')}:")
            print(f"  {value}")
        
        print("\n" + "="*70)
        print("SUGGESTED MODIFICATIONS")
        print("="*70)
        
        suggested = analysis.get("suggested_modifications", {})
        for key, value in suggested.items():
            print(f"\n{key.upper().replace('_', ' ')}:")
            print(f"  {value}")
        
        print("\n" + "="*70)
        print("GENERATION PROMPT")
        print("="*70)
        print(f"\n{analysis.get('generation_prompt', 'N/A')}")
        print("\n" + "="*70)

#!/usr/bin/env python3
"""
Thumbnail Wireframe Tool - Web Interface
Beautiful Streamlit UI for generating AI-powered thumbnails
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import time

# Load environment
load_dotenv(override=True)

from thumbnail_finder import ThumbnailFinder
from thumbnail_analyzer import ThumbnailAnalyzer
from image_generator import ImageGenerator

# Page config
st.set_page_config(
    page_title="AI Thumbnail Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.1rem;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'finder' not in st.session_state:
    st.session_state.finder = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'selected_thumbnail' not in st.session_state:
    st.session_state.selected_thumbnail = None
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None

# Header
st.markdown('<div class="main-header">🎨 AI Thumbnail Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Create professional YouTube thumbnails with AI in seconds</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    if openai_key and not openai_key.startswith("your_"):
        st.success("✅ OpenAI API Key")
    else:
        st.error("❌ OpenAI API Key Missing")
    
    if google_key and not google_key.startswith("your_"):
        st.success("✅ Google API Key")
    else:
        st.warning("⚠️ Google API Key Missing")
    
    st.divider()
    
    # Generation service selector
    st.subheader("Image Generation")
    generation_service = st.selectbox(
        "Choose Service",
        ["DALL-E 3 (OpenAI)", "Google Gemini/Imagen", "Replicate (FLUX)"],
        help="Select which AI service to use for generating images"
    )
    
    service_map = {
        "DALL-E 3 (OpenAI)": "dalle",
        "Google Gemini/Imagen": "gemini",
        "Replicate (FLUX)": "replicate"
    }
    
    st.divider()
    
    # Stats
    st.subheader("📊 Statistics")
    thumbnails_dir = Path("thumbnails")
    if thumbnails_dir.exists():
        count = len([f for f in thumbnails_dir.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']])
        st.metric("Thumbnails Indexed", count)
    
    generated_dir = Path("generated_thumbnails")
    if generated_dir.exists():
        gen_count = len(list(generated_dir.glob("*.png")))
        st.metric("Generated", gen_count)

# Main content
tab1, tab2, tab3 = st.tabs(["🔍 Find & Generate", "📚 Gallery", "ℹ️ How It Works"])

with tab1:
    # Step 1: Input
    st.header("Step 1: Enter Your Topic")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "What's your thumbnail about?",
            placeholder="e.g., AI Technology Explained",
            help="Be specific for better results"
        )
    
    with col2:
        pov = st.text_input(
            "Point of View (Optional)",
            placeholder="e.g., Beginner Friendly",
            help="Adds context to the search"
        )
    
    if st.button("🔍 Find Similar Thumbnails", type="primary", disabled=not topic):
        with st.spinner("Searching through your thumbnail library..."):
            try:
                # Initialize finder
                if st.session_state.finder is None:
                    st.session_state.finder = ThumbnailFinder("thumbnails")
                
                # Search
                results = st.session_state.finder.find_similar(
                    topic, 
                    pov if pov else None, 
                    top_k=3
                )
                st.session_state.results = results
                st.session_state.selected_thumbnail = None
                st.session_state.analysis = None
                st.session_state.generated_image = None
                
                st.success(f"✅ Found {len(results)} similar thumbnails!")
                
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Step 2: Show results
    if st.session_state.results:
        st.divider()
        st.header("Step 2: Select a Thumbnail")
        
        cols = st.columns(3)
        
        for idx, result in enumerate(st.session_state.results):
            with cols[idx]:
                try:
                    img = Image.open(result['path'])
                    st.image(img, use_container_width=True)
                    st.write(f"**{result['filename']}**")
                    st.write(f"Match Score: {result['similarity_score']:.2%}")
                    
                    if st.button(f"Select #{idx+1}", key=f"select_{idx}"):
                        st.session_state.selected_thumbnail = result
                        st.session_state.analysis = None
                        st.session_state.generated_image = None
                        st.rerun()
                
                except Exception as e:
                    st.error(f"Error loading image: {e}")
    
    # Step 3: Analyze
    if st.session_state.selected_thumbnail and not st.session_state.analysis:
        st.divider()
        st.header("Step 3: AI Analysis")
        
        st.info(f"📌 Selected: **{st.session_state.selected_thumbnail['filename']}**")
        
        if st.button("🤖 Analyze with GPT-4 Vision", type="primary"):
            with st.spinner("Analyzing thumbnail with GPT-4 Vision... (10-15 seconds)"):
                try:
                    analyzer = ThumbnailAnalyzer()
                    analysis = analyzer.analyze_thumbnail(
                        st.session_state.selected_thumbnail['path'],
                        topic,
                        pov if pov else None
                    )
                    st.session_state.analysis = analysis
                    st.success("✅ Analysis complete!")
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error during analysis: {e}")
    
    # Step 4: Show analysis and generate
    if st.session_state.analysis:
        st.divider()
        st.header("Step 4: Review & Generate")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Current Analysis")
            current = st.session_state.analysis.get('current_analysis', {})
            for key, value in current.items():
                st.write(f"**{key.replace('_', ' ').title()}:**")
                st.write(value)
                st.write("")
        
        with col2:
            st.subheader("✨ Suggested Modifications")
            suggested = st.session_state.analysis.get('suggested_modifications', {})
            for key, value in suggested.items():
                st.write(f"**{key.replace('_', ' ').title()}:**")
                st.write(value)
                st.write("")
        
        st.subheader("🎨 Generation Prompt")
        st.info(st.session_state.analysis.get('generation_prompt', 'N/A'))
        
        if not st.session_state.generated_image:
            if st.button("🚀 Generate Thumbnail", type="primary"):
                with st.spinner(f"Generating with {generation_service}... (20-40 seconds)"):
                    try:
                        service = service_map[generation_service]
                        generator = ImageGenerator(service=service)
                        
                        output_filename = f"generated_{topic.replace(' ', '_').lower()}.png"
                        output_path = f"generated_thumbnails/{output_filename}"
                        
                        generation_prompt = st.session_state.analysis.get('generation_prompt', '')
                        generated_path = generator.generate(generation_prompt, output_path)
                        
                        st.session_state.generated_image = generated_path
                        st.success("🎉 Thumbnail generated successfully!")
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error generating image: {e}")
    
    # Step 5: Show result
    if st.session_state.generated_image:
        st.divider()
        st.header("🎉 Your Generated Thumbnail!")
        
        try:
            img = Image.open(st.session_state.generated_image)
            st.image(img, use_container_width=True)
            
            st.success(f"✅ Saved to: `{st.session_state.generated_image}`")
            
            # Download button
            with open(st.session_state.generated_image, "rb") as file:
                st.download_button(
                    label="📥 Download Thumbnail",
                    data=file,
                    file_name=Path(st.session_state.generated_image).name,
                    mime="image/png"
                )
            
            if st.button("🔄 Create Another Thumbnail"):
                st.session_state.results = None
                st.session_state.selected_thumbnail = None
                st.session_state.analysis = None
                st.session_state.generated_image = None
                st.rerun()
        
        except Exception as e:
            st.error(f"Error loading generated image: {e}")

with tab2:
    st.header("📚 Generated Thumbnails Gallery")
    
    generated_dir = Path("generated_thumbnails")
    if generated_dir.exists():
        generated_files = sorted(generated_dir.glob("*.png"), key=os.path.getmtime, reverse=True)
        
        if generated_files:
            st.write(f"**Total Generated: {len(generated_files)}**")
            
            cols = st.columns(3)
            for idx, img_path in enumerate(generated_files):
                with cols[idx % 3]:
                    try:
                        img = Image.open(img_path)
                        st.image(img, use_container_width=True)
                        st.write(f"**{img_path.name}**")
                        
                        with open(img_path, "rb") as file:
                            st.download_button(
                                label="Download",
                                data=file,
                                file_name=img_path.name,
                                mime="image/png",
                                key=f"download_{idx}"
                            )
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("No thumbnails generated yet. Go to 'Find & Generate' tab to create your first one!")
    else:
        st.info("Generated thumbnails folder not found.")

with tab3:
    st.header("ℹ️ How It Works")
    
    st.markdown("""
    ### 🎯 4-Step Process
    
    1. **Enter Topic**: Describe what your thumbnail is about
    2. **Find Similar**: AI searches your 32 thumbnails using semantic matching
    3. **AI Analysis**: GPT-4 Vision analyzes the selected thumbnail
    4. **Generate**: AI creates your new thumbnail with suggested modifications
    
    ### 🤖 Technology Stack
    
    - **CLIP**: Semantic image search (finds similar thumbnails)
    - **GPT-4 Vision**: Analyzes thumbnails and suggests modifications
    - **DALL-E 3 / Gemini**: Generates new thumbnails
    
    ### 💰 Cost
    
    - Analysis: ~$0.01 per thumbnail
    - Generation: ~$0.04 per thumbnail
    - **Total: ~$0.05 per thumbnail**
    
    ### ⚡ Speed
    
    - Search: < 2 seconds
    - Analysis: ~10 seconds
    - Generation: ~30 seconds
    - **Total: ~45 seconds**
    
    ### 🎨 Features
    
    ✅ Semantic similarity search  
    ✅ AI-powered analysis  
    ✅ Smart modification suggestions  
    ✅ Multiple generation services  
    ✅ Avoids podcast elements  
    ✅ Professional quality output  
    
    ### 📝 Tips for Best Results
    
    1. **Be Specific**: "AI for Healthcare Professionals" > "AI"
    2. **Use POV**: "Beginner Friendly" adds context
    3. **Try Different Matches**: Each gives different styles
    4. **Experiment**: Try all generation services
    """)
    
    st.divider()
    
    st.subheader("🔧 Technical Info")
    st.code(f"""
Workspace: /Users/noorgupta/Downloads/Cursor/thumbnail_tookit
Thumbnails: {len([f for f in Path('thumbnails').iterdir() if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']]) if Path('thumbnails').exists() else 0}
Python: {os.sys.version.split()[0]}
OpenAI: {'✅ Configured' if openai_key and not openai_key.startswith('your_') else '❌ Not configured'}
Google: {'✅ Configured' if google_key and not google_key.startswith('your_') else '❌ Not configured'}
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🎨 AI Thumbnail Generator | Powered by GPT-4 Vision & DALL-E 3</p>
    <p>Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)


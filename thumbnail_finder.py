"""
Thumbnail Wireframe Tool - Main Module
Finds similar thumbnails and suggests modifications for new topics
"""

import os
import json
import base64
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer, util
import torch


class ThumbnailFinder:
    """Handles thumbnail similarity search and indexing"""
    
    def __init__(self, thumbnails_dir: str, index_file: str = "thumbnail_index.json"):
        self.thumbnails_dir = Path(thumbnails_dir)
        self.index_file = index_file
        self.model = SentenceTransformer('clip-ViT-B-32')
        self.index_data = self._load_or_create_index()
        
    def _load_or_create_index(self) -> Dict:
        """Load existing index or create new one"""
        if os.path.exists(self.index_file):
            print(f"Loading existing index from {self.index_file}")
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {"thumbnails": [], "embeddings": []}
    
    def index_thumbnails(self) -> None:
        """Index all thumbnails in the directory (supports subdirectories for categories)"""
        print(f"Indexing thumbnails from {self.thumbnails_dir}...")
        
        thumbnails = []
        embeddings = []
        
        # Find all image files (including in subdirectories)
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        image_files = []
        
        # Support both flat structure and categorized subdirectories
        for path in self.thumbnails_dir.rglob('*'):
            if path.is_file() and path.suffix.lower() in image_extensions:
                image_files.append(path)
        
        if not image_files:
            print(f"Warning: No images found in {self.thumbnails_dir}")
            return
        
        print(f"Found {len(image_files)} images to index")
        
        # Track categories
        categories = set()
        
        for img_path in image_files:
            try:
                # Load image
                img = Image.open(img_path).convert('RGB')
                
                # Generate embedding
                embedding = self.model.encode(img, convert_to_tensor=True)
                
                # Determine category (parent directory name if in subdirectory)
                category = None
                if img_path.parent != self.thumbnails_dir:
                    category = img_path.parent.name
                    categories.add(category)
                
                thumbnails.append({
                    "path": str(img_path),
                    "filename": img_path.name,
                    "category": category
                })
                embeddings.append(embedding.cpu().numpy().tolist())
                
                category_label = f" [{category}]" if category else ""
                print(f"  ✓ Indexed{category_label}: {img_path.name}")
                
            except Exception as e:
                print(f"  ✗ Error indexing {img_path.name}: {e}")
        
        self.index_data = {
            "thumbnails": thumbnails,
            "embeddings": embeddings,
            "categories": sorted(list(categories))
        }
        
        # Save index
        with open(self.index_file, 'w') as f:
            json.dump(self.index_data, f, indent=2)
        
        print(f"\n✓ Indexed {len(thumbnails)} thumbnails successfully!")
        if categories:
            print(f"✓ Found {len(categories)} categories: {', '.join(sorted(categories))}")
    
    def find_similar(self, topic: str, pov: Optional[str] = None, top_k: int = 3) -> List[Dict]:
        """Find similar thumbnails based on topic and POV"""
        if not self.index_data["thumbnails"]:
            raise ValueError("No thumbnails indexed. Run index_thumbnails() first.")
        
        # Create search query
        query = f"YouTube thumbnail about {topic}"
        if pov:
            query += f" from {pov} perspective"
        
        print(f"\nSearching for: '{query}'")
        
        # Encode query (force to CPU)
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        query_embedding = query_embedding.cpu()
        
        # Convert stored embeddings to tensor (force to CPU)
        stored_embeddings = torch.tensor(self.index_data["embeddings"]).cpu()
        
        # Calculate similarities
        similarities = util.cos_sim(query_embedding, stored_embeddings)[0]
        
        # Get top K
        top_results = torch.topk(similarities, k=min(top_k, len(similarities)))
        
        results = []
        for idx, score in zip(top_results.indices, top_results.values):
            thumbnail = self.index_data["thumbnails"][idx.item()]
            results.append({
                "path": thumbnail["path"],
                "filename": thumbnail["filename"],
                "similarity_score": float(score),
                "rank": len(results) + 1
            })
        
        return results
    
    def get_thumbnail_count(self) -> int:
        """Get number of indexed thumbnails"""
        return len(self.index_data["thumbnails"])
    
    def get_categories(self) -> List[str]:
        """Get list of categories"""
        return self.index_data.get("categories", [])
    
    def get_thumbnails_by_category(self, category: Optional[str] = None) -> List[Dict]:
        """Get thumbnails filtered by category"""
        thumbnails = self.index_data.get("thumbnails", [])
        
        if category is None:
            # Return uncategorized thumbnails
            return [t for t in thumbnails if t.get("category") is None]
        
        return [t for t in thumbnails if t.get("category") == category]


def encode_image_base64(image_path: str) -> str:
    """Encode image to base64 for API calls"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def display_results(results: List[Dict]) -> None:
    """Display search results in a readable format"""
    print("\n" + "="*70)
    print("TOP MATCHING THUMBNAILS")
    print("="*70)
    
    for result in results:
        print(f"\n{result['rank']}. {result['filename']}")
        print(f"   Similarity Score: {result['similarity_score']:.3f}")
        print(f"   Path: {result['path']}")
    
    print("\n" + "="*70)


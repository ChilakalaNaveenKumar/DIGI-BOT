"""
Vector Store Manager with Embeddings
Manages docs + embeddings for efficient reranking
"""
import os
import json
import numpy as np
import time
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI

class VectorStoreManager:
    """Manages documents with embeddings for rerank-based matching"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.embed_model = "text-embedding-3-large"
        self.documents_folder = "/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services/app/services/component_matcher/documents"
        self.documents_file = os.path.join(self.documents_folder, "vector_store.json")
        
        # Create documents folder
        os.makedirs(self.documents_folder, exist_ok=True)
        
        # Load existing documents with embeddings
        if os.path.exists(self.documents_file):
            with open(self.documents_file, "r") as f:
                self.docs = json.load(f)
        else:
            self.docs = []  # [{text, embedding, meta, timestamp}]
    
    async def initialize(self):
        """Initialize vector store and load documents from files"""
        
        # Load documents from markdown files if docs are empty
        if not self.docs:
            await self._load_documents_from_files()
        
        print(f"✅ Vector store initialized with {len(self.docs)} documents")
        return len(self.docs)
    
    async def _embed(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            resp = await self.client.embeddings.create(
                model=self.embed_model,
                input=text
            )
            return resp.data[0].embedding
        except Exception as e:
            print(f"❌ Embedding failed: {e}")
            return []
    
    async def _load_documents_from_files(self):
        """Load and embed documents from markdown files"""
        
        # Load chart format documentation
        chart_files = [
            "chartjs_markdown_format_v1.md",
            "data_table_markdown_format_v1.md"
        ]
        
        for filename in chart_files:
            file_path = os.path.join(self.documents_folder, filename)
            if os.path.exists(file_path):
                print(f"📄 Loading: {filename}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split content into chunks for better matching
                chunks = self._split_document(content, filename)
                
                for chunk in chunks:
                    await self.add_document(
                        text=chunk["text"],
                        meta={
                            "source": filename,
                            "section": chunk.get("section", ""),
                            "type": "chart_format"
                        }
                    )
                
                print(f"  ✅ Added {len(chunks)} chunks from {filename}")
    
    def _split_document(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Split document into meaningful chunks"""
        
        chunks = []
        
        # Split by sections (## headers)
        sections = content.split('\n## ')
        
        for i, section in enumerate(sections):
            if i == 0:
                # First section might not have ## prefix
                section_title = "Introduction"
            else:
                # Add back the ## prefix
                section = '## ' + section
                lines = section.split('\n')
                section_title = lines[0].replace('## ', '').strip()
            
            # Further split large sections by format blocks
            if '```' in section:
                # Split by code blocks which contain chart formats
                parts = section.split('```')
                
                for j in range(0, len(parts), 2):
                    if j + 1 < len(parts):
                        # Combine description + code block
                        chunk_text = parts[j].strip()
                        if j + 1 < len(parts):
                            chunk_text += '\n```' + parts[j + 1] + '```'
                        
                        if chunk_text.strip():
                            chunks.append({
                                "text": chunk_text,
                                "section": section_title
                            })
            else:
                # Regular text section
                if section.strip():
                    chunks.append({
                        "text": section.strip(),
                        "section": section_title
                    })
        
        return chunks
    
    async def add_document(self, text: str, meta: Dict[str, Any] = None):
        """Embed and store a document chunk"""
        
        if not text.strip():
            return
        
        # Generate embedding
        embedding = await self._embed(text)
        if not embedding:
            print(f"⚠️  Failed to embed document, skipping")
            return
        
        # Add document with timestamp for expiry
        doc = {
            "text": text,
            "embedding": embedding,
            "meta": meta or {},
            "timestamp": time.time()
        }
        
        self.docs.append(doc)
        self._save()
    
    def _save(self):
        """Save documents to JSON file"""
        try:
            with open(self.documents_file, "w") as f:
                json.dump(self.docs, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save documents: {e}")
    
    async def query(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """Return top-k docs using cosine similarity"""
        
        if not self.docs:
            print("⚠️  No documents in vector store")
            return []
        
        # Clean expired documents first
        self._clean_expired_docs()
        
        # Generate query embedding
        q_emb = await self._embed(query)
        if not q_emb:
            print("❌ Failed to embed query")
            return []
        
        def cosine_similarity(a, b):
            """Calculate cosine similarity between two vectors"""
            try:
                a_np = np.array(a)
                b_np = np.array(b)
                return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))
            except Exception:
                return 0.0
        
        # Score all documents
        scored = []
        for doc in self.docs:
            if not doc.get("embedding"):
                continue
                
            similarity = cosine_similarity(q_emb, doc["embedding"])
            scored.append({
                "text": doc["text"],
                "score": similarity,
                "meta": doc["meta"]
            })
        
        # Sort by similarity and return top-k
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
    
    def _clean_expired_docs(self, expire_days: int = 2):
        """Remove documents older than expire_days"""
        
        current_time = time.time()
        expire_seconds = expire_days * 24 * 60 * 60
        
        original_count = len(self.docs)
        self.docs = [
            doc for doc in self.docs 
            if current_time - doc.get("timestamp", 0) < expire_seconds
        ]
        
        removed_count = original_count - len(self.docs)
        if removed_count > 0:
            print(f"🧹 Removed {removed_count} expired documents")
            self._save()
    
    async def add_file_content(self, file_path: str, filename: str, force: bool = False):
        """Add content from a file to the vector store"""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check if file already processed (by filename in meta)
        if not force:
            existing = [doc for doc in self.docs if doc.get("meta", {}).get("source") == filename]
            if existing:
                print(f"ℹ️  File '{filename}' already processed. Use force=True to reprocess.")
                return
        
        # Remove existing docs from this file if force=True
        if force:
            original_count = len(self.docs)
            self.docs = [doc for doc in self.docs if doc.get("meta", {}).get("source") != filename]
            removed = original_count - len(self.docs)
            if removed > 0:
                print(f"♻️  Removed {removed} existing chunks from {filename}")
        
        # Read and process file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into chunks
            chunks = self._split_document(content, filename)
            
            # Add each chunk
            for chunk in chunks:
                await self.add_document(
                    text=chunk["text"],
                    meta={
                        "source": filename,
                        "section": chunk.get("section", ""),
                        "type": "document"
                    }
                )
            
            print(f"✅ Added {len(chunks)} chunks from {filename}")
            
        except Exception as e:
            print(f"❌ Failed to process file {filename}: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        
        # Clean expired docs first
        self._clean_expired_docs()
        
        if not self.docs:
            return {"total_docs": 0, "sources": []}
        
        # Count by source
        sources = {}
        for doc in self.docs:
            source = doc.get("meta", {}).get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total_docs": len(self.docs),
            "sources": sources,
            "embedding_model": self.embed_model
        }
    
    def clear_all_docs(self):
        """Clear all documents from the vector store"""
        self.docs = []
        self._save()
        print("🧹 Cleared all documents from vector store")
    
    async def rebuild_from_files(self):
        """Rebuild vector store from markdown files"""
        
        print("🔄 Rebuilding vector store from files...")
        
        # Clear existing docs
        self.clear_all_docs()
        
        # Reload from files
        await self._load_documents_from_files()
        
        print(f"✅ Rebuilt vector store with {len(self.docs)} documents")
    
    # Legacy compatibility methods (deprecated)
    def get_documents_folder(self) -> str:
        """Get path to documents folder"""
        return self.documents_folder
    
    async def query_vector_store(self, query: str) -> str:
        """Legacy method - use query() instead"""
        
        results = await self.query(query, top_k=5)
        if not results:
            return "No relevant documents found."
        
        # Return top result text
        return results[0]["text"]

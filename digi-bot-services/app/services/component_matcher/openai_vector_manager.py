"""
OpenAI Embeddings Manager
Uses OpenAI's Embeddings API with consistent file storage
"""
import os
import json
import numpy as np
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
import structlog

logger = structlog.get_logger(__name__)

class OpenAIVectorStoreManager:
    """Manages documents using OpenAI's Embeddings API with consistent storage"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.embed_model = "text-embedding-3-large"
        
        # Document paths
        self.documents_folder = "/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services/app/services/component_matcher/documents"
        
        # File mapping with consistent names
        self.file_mapping = {
            "chartjs_markdown_format_v1.md": "digi_setu_charts_v3.md",
            "data_table_markdown_format_v1.md": "digi_setu_tables_v3.md", 
            "Examples.md": "digi_setu_examples.md",
            "PositionAnchors.md": "digi_setu_positions.md"
        }
        
        # OpenAI embeddings storage
        self.embeddings_file = os.path.join(self.documents_folder, "openai_embeddings.json")
        self.documents = []
        self._initialized = False
    
    def _load_embeddings(self):
        """Load existing embeddings from file"""
        if os.path.exists(self.embeddings_file):
            try:
                with open(self.embeddings_file, 'r') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                logger.info("Loaded existing embeddings", count=len(self.documents))
            except Exception as e:
                logger.error("Failed to load embeddings", error=str(e))
                self.documents = []
        else:
            self.documents = []
    
    def _save_embeddings(self):
        """Save embeddings to file"""
        try:
            data = {
                "version": "1.0",
                "model": self.embed_model,
                "documents": self.documents
            }
            with open(self.embeddings_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Saved embeddings", count=len(self.documents))
        except Exception as e:
            logger.error("Failed to save embeddings", error=str(e))
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        try:
            response = await self.client.embeddings.create(
                model=self.embed_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("Failed to generate embedding", error=str(e))
            raise
    
    async def initialize(self):
        """Initialize embeddings storage and process documents"""
        if self._initialized:
            return len(self.documents)
        
        try:
            # Load existing embeddings
            self._load_embeddings()
            
            # Get existing document names
            existing_docs = {doc['filename'] for doc in self.documents}
            
            # Process each markdown file
            processed_count = 0
            for local_filename in os.listdir(self.documents_folder):
                if not local_filename.endswith('.md'):
                    continue
                
                consistent_name = self.file_mapping.get(local_filename, local_filename)
                
                # Skip if already processed
                if consistent_name in existing_docs:
                    logger.info("Document already processed", filename=consistent_name)
                    continue
                
                # Read and process the file
                local_path = os.path.join(self.documents_folder, local_filename)
                try:
                    with open(local_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Generate embedding
                    logger.info("Generating embedding", filename=consistent_name)
                    embedding = await self._generate_embedding(content)
                    
                    # Store document with embedding
                    doc_entry = {
                        "filename": consistent_name,
                        "original_filename": local_filename,
                        "content": content,
                        "embedding": embedding,
                        "content_length": len(content),
                        "model": self.embed_model
                    }
                    
                    self.documents.append(doc_entry)
                    processed_count += 1
                    
                    logger.info("Processed document", 
                               filename=consistent_name,
                               content_length=len(content))
                    
                except Exception as e:
                    logger.error("Failed to process document", 
                               filename=local_filename, 
                               error=str(e))
            
            # Save updated embeddings
            if processed_count > 0:
                self._save_embeddings()
            
            self._initialized = True
            logger.info("Embeddings initialization complete", 
                       total_docs=len(self.documents),
                       new_docs=processed_count)
            
            return len(self.documents)
            
        except Exception as e:
            logger.error("Failed to initialize embeddings", error=str(e))
            raise
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            a = np.array(vec1)
            b = np.array(vec2)
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        except Exception:
            return 0.0
    
    async def query(self, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Query documents using OpenAI embeddings"""
        if not self._initialized:
            await self.initialize()
        
        if not self.documents:
            logger.warning("No documents available for query")
            return []
        
        try:
            # Generate embedding for query
            query_embedding = await self._generate_embedding(query_text)
            
            # Calculate similarities
            results = []
            for doc in self.documents:
                similarity = self._cosine_similarity(query_embedding, doc['embedding'])
                results.append({
                    "text": doc['content'],
                    "score": similarity,
                    "meta": {
                        "filename": doc['filename'],
                        "original_filename": doc['original_filename'],
                        "content_length": doc['content_length']
                    }
                })
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x['score'], reverse=True)
            top_results = results[:top_k]
            
            logger.info("Query completed", 
                       query_length=len(query_text),
                       results_count=len(top_results),
                       top_score=top_results[0]['score'] if top_results else 0)
            
            return top_results
            
        except Exception as e:
            logger.error("Query failed", error=str(e))
            return []
    
    async def clear_all_docs(self):
        """Clear all documents and embeddings"""
        try:
            self.documents = []
            self._save_embeddings()
            logger.info("Cleared all documents and embeddings")
        except Exception as e:
            logger.error("Failed to clear documents", error=str(e))
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get embeddings storage statistics"""
        try:
            if not self._initialized:
                await self.initialize()
            
            return {
                "storage_type": "openai_embeddings",
                "model": self.embed_model,
                "document_count": len(self.documents),
                "files": [doc['filename'] for doc in self.documents],
                "total_content_length": sum(doc['content_length'] for doc in self.documents),
                "status": "active"
            }
            
        except Exception as e:
            logger.error("Failed to get stats", error=str(e))
            return {"status": "error", "error": str(e)}

# Backward compatibility - alias to new class
VectorStoreManager = OpenAIVectorStoreManager
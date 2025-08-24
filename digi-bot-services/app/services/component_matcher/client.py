"""
Chart Matcher Client with Embedding-Based Retrieval
"""
import os
from typing import Dict, List, Optional, Any, AsyncGenerator, TYPE_CHECKING
from openai import AsyncOpenAI

if TYPE_CHECKING:
    from .vector_manager import VectorStoreManager

class ComponentMatcherClient:
    """
    Component matcher using embedding-based retrieval + reranking.
    
    Flow:
    1. Embed query
    2. Find top 20 similar documents via cosine similarity  
    3. Rerank and keep top 5
    4. Pass to GPT for final format matching
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = AsyncOpenAI(api_key=self.api_key)
        self._initialized = False
        self.model = "gpt-5"  # 128k context, 16k output, multimodal
        self.keep_top_k = 5    # Final docs to keep after reranking
        self.max_output_tokens = 32000  # Max for gpt-4o
    
    async def initialize(self):
        """Initialize client"""
        if self._initialized:
            return
            
        try:
            await self.client.models.list()
            self._initialized = True
            print(f"✅ Chart matcher initialized with {self.model}")
            
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            raise
    
    async def analyze(
        self,
        query: str,
        vector_manager: Optional['VectorStoreManager'] = None,
        force_docs: Optional[List[str]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream back exact format/example from documentation if query matches.
        Uses embedding-based retrieval + reranking for better accuracy.
        """
        
        if not self._initialized:
            await self.initialize()
        
        # Get relevant documents
        if force_docs:
            docs = force_docs
        else:
            if not vector_manager:
                from .vector_manager import VectorStoreManager
                vector_manager = VectorStoreManager()
                await vector_manager.initialize()
            
            # Get top candidates using embeddings
            candidates = await vector_manager.query(query, top_k=20)
            
            # Keep only top K for final matching (reranking)
            docs = [c["text"] for c in candidates[:self.keep_top_k]]
        
        if not docs:
            yield {"type": "content", "content": "NO_MATCH"}
            yield {"type": "completion", "finish_reason": "done"}
            return
        
        # Combine documentation
        doc_text = "\n\n".join(docs)
        
        prompt = f"""You are a format matcher.

- Compare the QUERY with the DOCUMENTATION below.
- If the query matches a format/example in the documentation, return the exact format block(s).
- If no format applies, return only "NO_MATCH".

QUERY:
{query}

DOCUMENTATION:
{doc_text}"""
        
        try:
            async with self.client.responses.stream(
                model=self.model,
                input=[{
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}],
                }],
                max_output_tokens=self.max_output_tokens,
            ) as stream:
                async for event in stream:
                    event_type = getattr(event, "type", "")
                    if event_type == "response.output_text.delta":
                        yield {"type": "content", "content": event.delta}
                    elif event_type == "response.error":
                        yield {"type": "error", "error": getattr(event, "error", "unknown")}
                    elif event_type == "response.completed":
                        yield {"type": "completion", "finish_reason": "done"}
                        
        except Exception as e:
            yield {"type": "error", "error": str(e)}
    
    async def quick_match(self, query: str, vector_manager: Optional['VectorStoreManager'] = None) -> str:
        """Quick non-streaming match check using embedding-based retrieval"""
        
        full_response = ""
        async for event in self.analyze(query, vector_manager):
            if event["type"] == "content":
                full_response += event["content"]
            elif event["type"] == "error":
                return f"ERROR: {event['error']}"
        
        return full_response.strip()
    
    def has_match(self, response: str) -> bool:
        """Simple helper to check if response contains a match"""
        return response.strip() != "NO_MATCH" and "NO_MATCH" not in response.upper()

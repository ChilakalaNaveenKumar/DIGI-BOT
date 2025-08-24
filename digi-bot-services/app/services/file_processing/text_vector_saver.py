# text_vector_saver.py
import os
import hashlib
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from .file_analyzer import FileAnalyzer, AnalyzeLimits

EXPIRES_ANCHOR = "last_active_at"

class TextVectorSaver:
    """
    Extract text from files and save only the text content to vector store.
    Does NOT upload the original files - only processes and stores extracted text.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.analyzer = FileAnalyzer()
    
    async def extract_and_save_text(
        self,
        file_path: str,
        vector_store_id: Optional[str] = None,
        vector_store_name: str = "Text Content Store",
        expires_days: int = 2,
        chunk_size: int = 4000,  # Split large texts into chunks
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Extract text from file and save to vector store as text documents.
        Returns info about what was saved.
        
        Args:
            file_path: Path to file to process
            vector_store_id: Existing vector store ID (optional)
            vector_store_name: Name for vector store if creating new one
            expires_days: Days until vector store expires
            chunk_size: Max characters per text chunk
            include_metadata: Whether to include file metadata in text
        
        Returns:
            Dict with extraction results and vector store info
        """
        
        # Step 1: Extract text from file
        print(f"📄 Extracting text from: {os.path.basename(file_path)}")
        result = self.analyzer.analyze_path(file_path)
        
        if not result.ok:
            return {
                "success": False,
                "error": f"Text extraction failed: {result.error}",
                "file": os.path.basename(file_path)
            }
        
        extracted_text = result.text.strip()
        if not extracted_text:
            return {
                "success": False,
                "error": "No text content extracted from file",
                "file": os.path.basename(file_path)
            }
        
        print(f"✅ Extracted {len(extracted_text)} characters")
        
        # Step 2: Ensure vector store exists
        vs_id = await self._ensure_vector_store(vector_store_id, vector_store_name, expires_days)
        
        # Step 3: Prepare text content with metadata
        content_to_save = self._prepare_content(file_path, extracted_text, result.meta, include_metadata)
        
        # Step 4: Split into chunks if needed
        chunks = self._split_into_chunks(content_to_save, chunk_size)
        print(f"📝 Split into {len(chunks)} chunks")
        
        # Step 5: Check for existing content (by content hash)
        content_hash = self._get_content_hash(extracted_text)
        if await self._content_exists_in_store(vs_id, content_hash):
            print("ℹ️  Content already exists in vector store (skipping)")
            await self._update_expiry(vs_id, expires_days)
            return {
                "success": True,
                "action": "skipped_duplicate",
                "vector_store_id": vs_id,
                "file": os.path.basename(file_path),
                "chunks": len(chunks),
                "characters": len(extracted_text)
            }
        
        # Step 6: Save text chunks to vector store
        saved_file_ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_chunk_{i+1}.txt"
            
            # Create temporary text file for this chunk
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(chunk)
                temp_path = temp_file.name
            
            try:
                # Upload text chunk to Files API
                with open(temp_path, 'rb') as f:
                    uploaded = await self.client.files.create(
                        file=f,
                        purpose="assistants"
                    )
                
                # Attach to vector store
                await self.client.vector_stores.files.create(
                    vector_store_id=vs_id,
                    file_id=uploaded.id
                )
                
                saved_file_ids.append(uploaded.id)
                print(f"  ✅ Saved chunk {i+1}/{len(chunks)}: {uploaded.id}")
                
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
        
        # Step 7: Store content hash for deduplication
        await self._store_content_hash(vs_id, content_hash, os.path.basename(file_path))
        
        # Update expiry
        await self._update_expiry(vs_id, expires_days)
        
        return {
            "success": True,
            "action": "saved_text",
            "vector_store_id": vs_id,
            "file": os.path.basename(file_path),
            "chunks": len(chunks),
            "characters": len(extracted_text),
            "file_ids": saved_file_ids,
            "content_hash": content_hash
        }
    
    def _prepare_content(self, file_path: str, text: str, metadata: Dict[str, Any], include_metadata: bool) -> str:
        """Prepare content with optional metadata header"""
        
        if not include_metadata:
            return text
        
        # Add metadata header
        header_lines = [
            f"# File: {os.path.basename(file_path)}",
            f"# Type: {metadata.get('ext', 'unknown')}",
            f"# Size: {metadata.get('bytes', 0)} bytes",
            f"# MIME: {metadata.get('mime', 'unknown')}",
        ]
        
        # Add specific metadata if available
        if 'pages' in metadata:
            header_lines.append(f"# Pages: {metadata['pages']}")
        if 'sheets' in metadata:
            header_lines.append(f"# Sheets: {metadata['sheets']}")
        if 'slides' in metadata:
            header_lines.append(f"# Slides: {metadata['slides']}")
        
        header_lines.append("")  # Empty line separator
        header_lines.append("# Content:")
        header_lines.append("")
        
        return "\n".join(header_lines) + text
    
    def _split_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks of specified size"""
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # Try to find a good break point (end of sentence, paragraph, etc.)
            end_pos = current_pos + chunk_size
            
            if end_pos >= len(text):
                # Last chunk
                chunks.append(text[current_pos:])
                break
            
            # Look for good break points in the last 200 characters
            search_start = max(current_pos, end_pos - 200)
            break_chars = ['\n\n', '\n', '. ', '! ', '? ', '; ']
            
            best_break = end_pos
            for break_char in break_chars:
                last_break = text.rfind(break_char, search_start, end_pos)
                if last_break > current_pos:
                    best_break = last_break + len(break_char)
                    break
            
            chunks.append(text[current_pos:best_break])
            current_pos = best_break
        
        return chunks
    
    def _get_content_hash(self, text: str) -> str:
        """Generate hash of content for deduplication"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
    
    async def _content_exists_in_store(self, vector_store_id: str, content_hash: str) -> bool:
        """Check if content with this hash already exists"""
        # Simple implementation: check if a file with hash in name exists
        # In production, you might want a more robust tracking system
        
        try:
            files = await self.client.vector_stores.files.list(vector_store_id=vector_store_id)
            
            # Look for files with our hash marker
            for file_info in files.data:
                try:
                    file_details = await self.client.files.retrieve(file_info.id)
                    filename = getattr(file_details, 'filename', '')
                    if content_hash in filename:
                        return True
                except:
                    continue
            
            return False
            
        except Exception:
            return False
    
    async def _store_content_hash(self, vector_store_id: str, content_hash: str, original_filename: str):
        """Store content hash for future deduplication"""
        # Create a small marker file with the hash
        hash_content = f"# Content Hash: {content_hash}\n# Original File: {original_filename}\n# Processed: {os.path.basename(__file__)}"
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(hash_content)
            temp_path = temp_file.name
        
        try:
            # Upload hash marker
            with open(temp_path, 'rb') as f:
                uploaded = await self.client.files.create(
                    file=f,
                    purpose="assistants"
                )
            
            # Rename to include hash (if possible)
            # Note: OpenAI doesn't allow renaming, so hash is in content
            
        finally:
            os.unlink(temp_path)
    
    async def _ensure_vector_store(self, vector_store_id: Optional[str], name: str, expires_days: int) -> str:
        """Ensure vector store exists with proper expiry"""
        
        if vector_store_id:
            await self._update_expiry(vector_store_id, expires_days)
            return vector_store_id
        
        # Try to find by name
        vs_id = await self._find_vector_store_by_name(name)
        if vs_id:
            await self._update_expiry(vs_id, expires_days)
            return vs_id
        
        # Create new store
        created = await self.client.vector_stores.create(
            name=name,
            expires_after={"anchor": EXPIRES_ANCHOR, "days": expires_days}
        )
        return created.id
    
    async def _find_vector_store_by_name(self, name: str) -> Optional[str]:
        """Find vector store by name"""
        after = None
        while True:
            resp = await self.client.vector_stores.list(after=after, limit=100)
            for vs in resp.data:
                if (getattr(vs, "name", None) or "").strip() == name.strip():
                    return vs.id
            if not getattr(resp, "has_more", False):
                break
            after = resp.last_id
        return None
    
    async def _update_expiry(self, vector_store_id: str, expires_days: int):
        """Update vector store expiry"""
        try:
            await self.client.vector_stores.update(
                vector_store_id=vector_store_id,
                expires_after={"anchor": EXPIRES_ANCHOR, "days": expires_days}
            )
        except Exception:
            pass  # Ignore if update not supported
    
    async def batch_extract_and_save(
        self,
        file_paths: List[str],
        vector_store_name: str = "Batch Text Content Store",
        expires_days: int = 2,
        chunk_size: int = 4000
    ) -> Dict[str, Any]:
        """Process multiple files and save extracted text to vector store"""
        
        print(f"📦 Batch processing {len(file_paths)} files...")
        
        # Ensure vector store
        vs_id = await self._ensure_vector_store(None, vector_store_name, expires_days)
        
        results = []
        total_chars = 0
        total_chunks = 0
        
        for i, file_path in enumerate(file_paths, 1):
            print(f"\n[{i}/{len(file_paths)}] Processing: {os.path.basename(file_path)}")
            
            result = await self.extract_and_save_text(
                file_path,
                vector_store_id=vs_id,
                expires_days=expires_days,
                chunk_size=chunk_size
            )
            
            results.append(result)
            
            if result["success"]:
                total_chars += result.get("characters", 0)
                total_chunks += result.get("chunks", 0)
                print(f"  ✅ Success: {result.get('chunks', 0)} chunks, {result.get('characters', 0)} chars")
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
        
        successful = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "vector_store_id": vs_id,
            "processed": len(file_paths),
            "successful": successful,
            "failed": len(file_paths) - successful,
            "total_characters": total_chars,
            "total_chunks": total_chunks,
            "results": results
        }

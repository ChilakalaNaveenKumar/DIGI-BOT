# vector_store_saver.py
import os
from typing import Optional, Tuple, List
from openai import AsyncOpenAI

# Optional: if you're using the FileAnalyzer from earlier
try:
    from .file_analyzer import FileAnalyzer, AnalyzeLimits
except Exception:
    FileAnalyzer = None

EXPIRES_ANCHOR = "last_active_at"  # Vector Store expiry uses "last_active_at" anchor

class VectorStoreSaver:
    """
    Save files into a Vector Store with a 2-day expiry.
    - Can reuse an existing store by id OR name.
    - Ensures expires_after is set/updated.
    - De-dupes by filename + size to avoid duplicate file uploads.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    async def ensure_vector_store(
        self,
        vector_store_id: Optional[str] = None,
        name: str = "Chart Documentation Store",
        expires_days: int = 2
    ) -> str:
        """
        Returns a vector_store_id. If not provided, finds/creates by name.
        Always ensures expires_after is set to <expires_days>.
        """
        if vector_store_id:
            # Ensure expiry on existing store
            await self._update_expiry(vector_store_id, expires_days)
            return vector_store_id

        # Try to find by name (list + filter)
        vs_id = await self._find_vector_store_by_name(name)
        if vs_id:
            await self._update_expiry(vs_id, expires_days)
            return vs_id

        # Create new store with expiry
        created = await self.client.vector_stores.create(
            name=name,
            expires_after={"anchor": EXPIRES_ANCHOR, "days": expires_days},
        )
        return created.id

    async def _find_vector_store_by_name(self, name: str) -> Optional[str]:
        """
        Finds a vector store by name (simple linear scan with pagination).
        """
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
        """
        Updates the store expiry to the requested number of days.
        Safe to call repeatedly.
        """
        try:
            await self.client.vector_stores.update(
                vector_store_id=vector_store_id,
                expires_after={"anchor": EXPIRES_ANCHOR, "days": expires_days},
            )
        except Exception:
            # Some SDKs may not support update fully; it's fine to ignore if already set.
            pass

    async def _list_vector_store_file_ids(self, vector_store_id: str) -> List[str]:
        """
        Returns all file_ids currently attached to the store (handles pagination).
        """
        ids: List[str] = []
        after = None
        while True:
            resp = await self.client.vector_stores.files.list(
                vector_store_id=vector_store_id, after=after, limit=100
            )
            ids += [f.id for f in resp.data]
            if not getattr(resp, "has_more", False):
                break
            after = resp.last_id
        return ids

    async def _get_file_meta(self, file_id: str) -> Tuple[str, int]:
        """
        Returns (filename, bytes) for a file by id.
        """
        f = await self.client.files.retrieve(file_id)
        # Some SDK versions expose `filename` as `filename` or `filename` on dict; guard both
        name = getattr(f, "filename", None) or getattr(f, "name", "")
        size = getattr(f, "bytes", None) or getattr(f, "size", 0)
        return str(name), int(size or 0)

    async def _file_exists_in_store(self, vector_store_id: str, local_path: str) -> bool:
        """
        Naive de-dupe: checks if a file with the same filename and size already exists.
        (Robust de-dupe by content hash would require downloading files or storing hashes externally.)
        """
        filename = os.path.basename(local_path)
        local_size = os.path.getsize(local_path)

        file_ids = await self._list_vector_store_file_ids(vector_store_id)
        if not file_ids:
            return False

        # Check first 1000 to keep calls reasonable; adjust if you expect larger stores
        for file_id in file_ids[:1000]:
            try:
                name, size = await self._get_file_meta(file_id)
            except Exception:
                continue
            if name == filename and size == local_size:
                return True
        return False

    async def upload_if_needed(
        self,
        path: str,
        vector_store_id: Optional[str] = None,
        vector_store_name: str = "Chart Documentation Store",
        expires_days: int = 2,
        validate_with_analyzer: bool = False
    ) -> str:
        """
        Ensures a vector store (2-day expiry), then uploads `path` if not present.
        Returns the vector_store_id.
        - If validate_with_analyzer=True, will run FileAnalyzer first and fail if not ok.
        """
        vs_id = await self.ensure_vector_store(vector_store_id, vector_store_name, expires_days)

        if validate_with_analyzer and FileAnalyzer is not None:
            res = FileAnalyzer().analyze_path(path)
            if not res.ok:
                raise ValueError(f"Validation failed: {res.error}")

        # De-dupe
        if await self._file_exists_in_store(vs_id, path):
            # Touch expiry (via update) on every call to keep it alive
            await self._update_expiry(vs_id, expires_days)
            return vs_id

        # Upload file to Files API
        with open(path, "rb") as f:
            uploaded = await self.client.files.create(
                file=f,
                purpose="assistants",
            )

        # Attach file to Vector Store
        await self.client.vector_stores.files.create(
            vector_store_id=vs_id,
            file_id=uploaded.id,
        )

        # Ensure expiry is set (again, idempotent)
        await self._update_expiry(vs_id, expires_days)
        return vs_id

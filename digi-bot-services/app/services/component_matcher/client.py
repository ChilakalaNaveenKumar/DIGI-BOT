"""
Generic Component Matcher Client (Embedding Retrieval + Streaming)
- Works with ANY documentation that defines response "blocks" or "formats".
- The model is instructed to ONLY emit verbatim blocks from the documentation, or "NO_MATCH".
"""

import os
from typing import Dict, List, Optional, Any, AsyncGenerator, TYPE_CHECKING
from openai import AsyncOpenAI

if TYPE_CHECKING:
    from .vector_manager import VectorStoreManager


class ComponentMatcherClient:
    """
    Generic component matcher using embedding-based retrieval + optional reranking.

    Flow:
      1) vector_manager.query(query, top_k=20)  -> candidate chunks (strings)
      2) keep top-K (self.keep_top_k)           -> doc pack
      3) ask model to emit exact block(s) that best answer query or "NO_MATCH"
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        keep_top_k: int = 5,
        max_output_tokens: int = 16000,
        liberal_match: bool = True,      # prefer semantic/pattern matches
        allow_placeholders: bool = True, # emit skeletons when data missing
        temperature: float = 0.2,
        # optional: pass your own few-shots that reflect your docs' block style
        few_shots: Optional[List[Dict[str, str]]] = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client: Optional[AsyncOpenAI] = None
        self._initialized = False

        self.model = model
        self.keep_top_k = keep_top_k
        self.max_output_tokens = max_output_tokens
        self.liberal_match = liberal_match
        self.allow_placeholders = allow_placeholders
        self.temperature = temperature
        self.few_shots = few_shots or []  # [{"user": "...", "assistant": "..."}]

    async def initialize(self):
        if self._initialized:
            return
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY.")
        self.client = AsyncOpenAI(api_key=self.api_key)
        await self.client.models.list()
        self._initialized = True
        print(f"✅ Component matcher initialized with {self.model}")

    async def analyze(
        self,
        query: str,
        vector_manager: Optional["VectorStoreManager"] = None,
        force_docs: Optional[List[str]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streams back exact block(s) from documentation if the query semantically fits.
        Otherwise streams only 'NO_MATCH'.
        """
        if not self._initialized:
            await self.initialize()

        # Gather candidate docs
        if force_docs:
            docs = force_docs
        else:
            if not vector_manager:
                from .vector_manager import VectorStoreManager
                vector_manager = VectorStoreManager()
                await vector_manager.initialize()

            candidates = await vector_manager.query(query, top_k=20)
            docs = [c["text"] for c in candidates[: self.keep_top_k]]

        if not docs:
            yield {"type": "content", "content": "NO_MATCH"}
            yield {"type": "completion", "finish_reason": "done"}
            return

        doc_text = "\n\n".join(docs)
        messages = self._build_messages(query, doc_text)

        try:
            # Chat Completions streaming (works well with gpt-4o)
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_output_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        yield {"type": "content", "content": delta.content}
                    if chunk.choices[0].finish_reason:
                        yield {"type": "completion", "finish_reason": chunk.choices[0].finish_reason}

        except Exception as e:
            yield {"type": "error", "error": str(e)}

    def _build_messages(self, query: str, doc_text: str) -> List[Dict[str, str]]:
        """Generic system prompt + optional few-shots; no chart-specific content."""
        mode = "LIBERAL" if self.liberal_match else "CONSERVATIVE"
        placeholders = "ALLOWED" if self.allow_placeholders else "DISALLOWED"

        system = f"""
You are a generic FORMAT MATCHER.

Your job:
- Read DOCUMENTATION that contains one or more canonical "blocks" or "formats" (could be code blocks, config blocks, UI components, templates, etc.).
- Decide which documented block(s) best answer the QUERY by PATTERN/INTENT, not by exact wording or entity names.
- If the QUERY clearly maps to a documented pattern but lacks some values, and placeholders are {placeholders}, output a valid skeleton using obvious placeholders (e.g. <value1>, <column_B>, <param>).
- In {mode} mode:
  • LIBERAL → prefer mapping by pattern/intent and allow reasonable substitutions.
  • CONSERVATIVE → require a closer fit to one of the documented blocks.

Hard constraints:
- Output ONLY:
  (a) one or more block(s) VERBATIM IN STRUCTURE (keys/order/shape) as they appear in the documentation, with adapted labels/values/placeholders if needed,
  OR
  (b) the single string NO_MATCH if nothing applies.

- DO NOT add commentary, prose, or explanations.
- Do NOT stop at one go, check all types of formats and check weather it matched the documentation. Go hard thinking comparing things in teh query or any kind of patterns we may expect in the answer based on question.
""".strip()

        msgs: List[Dict[str, str]] = [{"role": "system", "content": system}]

        # Optional: your own generic few-shots (non-domain-specific)
        for fs in self.few_shots:
            user = fs.get("user")
            assistant = fs.get("assistant")
            if user and assistant:
                msgs.append({"role": "user", "content": user})
                msgs.append({"role": "assistant", "content": assistant})

        # Actual user message with docs
        msgs.append({
            "role": "user",
            "content": f"""QUERY:
{query}

DOCUMENTATION:
{doc_text}"""
        })
        return msgs

    async def quick_match(
        self,
        query: str,
        vector_manager: Optional["VectorStoreManager"] = None,
        force_docs: Optional[List[str]] = None,
    ) -> str:
        """Return concatenated streamed text (exact blocks or 'NO_MATCH')."""
        out = []
        async for ev in self.analyze(query, vector_manager=vector_manager, force_docs=force_docs):
            if ev["type"] == "content":
                out.append(ev["content"])
            elif ev["type"] == "error":
                return f"ERROR: {ev['error']}"
        return "".join(out).strip()

    def has_match(self, response: str) -> bool:
        """True if the model produced anything other than 'NO_MATCH'."""
        txt = response.strip()
        return bool(txt) and txt.upper() != "NO_MATCH"
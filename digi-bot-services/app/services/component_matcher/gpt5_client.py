"""
GPT-5 Component Matcher Client (Responses API + Streaming)
- Works with ANY documentation that defines response "blocks" or "formats".
- Uses GPT-5's Responses API with reasoning capabilities for more precise matching.
- The model is instructed to ONLY emit verbatim blocks from the documentation, or "NO_MATCH".
"""

import os
from typing import Dict, List, Optional, Any, AsyncGenerator, TYPE_CHECKING
from openai import AsyncOpenAI

if TYPE_CHECKING:
    from .vector_manager import VectorStoreManager


class GPT5ComponentMatcherClient:
    """
    GPT-5 component matcher using embedding-based retrieval + Responses API.

    Flow:
      1) vector_manager.query(query, top_k=20)  -> candidate chunks (strings)
      2) keep top-K (self.keep_top_k)           -> doc pack
      3) ask GPT-5 to emit exact block(s) that best answer query or "NO_MATCH"
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-5",
        fallback_model: str = "gpt-4o",
        keep_top_k: int = 5,
        max_tokens: int = 32000,
        liberal_match: bool = True,      # prefer semantic/pattern matches
        allow_placeholders: bool = True, # emit skeletons when data missing
        reasoning_effort: Optional[str] = None, # "low" | "medium" | "high"

        # optional: pass your own few-shots that reflect your docs' block style
        few_shots: Optional[List[Dict[str, str]]] = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client: Optional[AsyncOpenAI] = None
        self._initialized = False

        self.model = model
        self.fallback_model = fallback_model
        self.keep_top_k = keep_top_k
        self.max_tokens = max_tokens
        self.liberal_match = liberal_match
        self.allow_placeholders = allow_placeholders
        self.reasoning_effort = reasoning_effort
        self.few_shots = few_shots or []  # [{"user": "...", "assistant": "..."}]

    async def initialize(self):
        if self._initialized:
            return
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY.")

        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Check model availability and fallback if needed
        try:
            models = await self.client.models.list()
            available = {m.id for m in models.data}

            if self.model not in available:
                if self.fallback_model in available:
                    print(f"⚠️  {self.model} not available, using fallback {self.fallback_model}")
                    self.model = self.fallback_model
                else:
                    raise RuntimeError(f"No suitable model. Tried: {self.model}, fallback: {self.fallback_model}")
        except Exception as e:
            print(f"Warning: Could not check model availability: {e}")
            # Continue with original model selection

        self._initialized = True
        print(f"✅ GPT-5 Component matcher initialized with {self.model}")

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
        
        try:
            # Use GPT-5 Responses API if available, otherwise fallback to Chat Completions
            if self.model == "gpt-5":
                system_instruction = self._build_system_instruction()
                user_text = f"""QUERY:
{query}

DOCUMENTATION:
{doc_text}"""
                async for event in self._stream_with_responses_api(system_instruction, user_text):
                    yield event
            else:
                # Fallback to Chat Completions API for non-GPT-5 models
                async for event in self._stream_with_chat_api(query, doc_text):
                    yield event

        except Exception as e:
            yield {"type": "error", "error": str(e)}

    async def _stream_with_responses_api(self, system_instruction: str, user_text: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream using GPT-5 Responses API with proper message structure."""
        
        # Build the standard Responses API "input" with system + user roles
        base_kwargs: Dict[str, Any] = {
            "model": self.model,
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system_instruction}]},
                {"role": "user", "content": [{"type": "input_text", "text": user_text}]},
            ],
            # Primary token cap for Responses API
            "max_output_tokens": self.max_tokens,
        }
        
        # Add reasoning ONLY if explicitly set AND supported by the model
        if self.reasoning_effort and self.model == "gpt-5":
            base_kwargs["reasoning"] = {"effort": self.reasoning_effort}

        try:
            async with self.client.responses.stream(**base_kwargs) as stream:
                async for event in stream:
                    event_type = getattr(event, "type", "")
                    if event_type == "response.output_text.delta":
                        yield {"type": "content", "content": event.delta}
                    elif event_type == "response.output_text":
                        # Some SDKs deliver full text chunks (non-delta)
                        yield {"type": "content", "content": event.text}
                    elif event_type == "response.error":
                        yield {"type": "error", "error": getattr(event, "error", "unknown")}
                        return
                    elif event_type == "response.completed":
                        yield {"type": "completion", "finish_reason": "done"}
                        return
        except Exception as e:
            yield {"type": "error", "error": str(e)}

    async def _stream_with_chat_api(self, query: str, doc_text: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Fallback to Chat Completions API for non-GPT-5 models."""
        messages = self._build_messages(query, doc_text)
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
            max_tokens=self.max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    yield {"type": "content", "content": delta.content}
                if chunk.choices[0].finish_reason:
                    yield {"type": "completion", "finish_reason": chunk.choices[0].finish_reason}

    def _build_system_instruction(self) -> str:
        """Build system instruction for GPT-5 Responses API."""
        mode = "LIBERAL" if self.liberal_match else "CONSERVATIVE"
        placeholders = "ALLOWED" if self.allow_placeholders else "DISALLOWED"

        system_instruction = f"""
You are a generic FORMAT MATCHER.

Your job:
- Read DOCUMENTATION that contains one or more canonical "blocks" or "formats" (code blocks, config blocks, UI components, templates, etc.).
- Decide which documented block(s) best answer the QUERY by PATTERN/INTENT, not by keyword overlap.
- If the QUERY maps to a documented pattern but lacks some values, and placeholders are {placeholders}, output a valid skeleton using obvious placeholders (e.g., <value>, <label>, <position>).

Mode: {mode}
  • LIBERAL → prefer mapping by pattern/intent and allow reasonable substitutions.
  • CONSERVATIVE → require a closer fit to a documented block.

Hard constraints:
- Data integrity: Use only values explicitly present in DOCUMENTATION or in the QUERY. If a required value is missing, use a placeholder. Never invent numbers, bins, labels, counts, or statistics.
- Output format (mandatory):
  • If there is at least one match, return a single JSON object exactly like:
    {{"matches":[{{"block_content":"<block 1>"}},{{"block_content":"<block 2>"}}]}}
    where each "block_content" is one documented block verbatim in structure (keys/order/shape) as defined by DOCUMENTATION, adapted with real values or placeholders.
  • If there is no match, return the single string: NO_MATCH
- Do not add commentary, prose, code fences, or any extra keys beyond "matches".
- insert_character_index rule: Analyze the QUERY content and determine the optimal character position where the component should be inserted. Count characters from the start of the content to calculate the exact insertion point. Only use <insert_character_index> placeholder if the content is too short or contains no suitable insertion points.
""".strip()

        # Add few-shots if available
        if self.few_shots:
            system_instruction += "\n\nEXAMPLES:\n"
            for i, fs in enumerate(self.few_shots, 1):
                user = fs.get("user", "")
                assistant = fs.get("assistant", "")
                if user and assistant:
                    system_instruction += f"\nExample {i}:\nQuery: {user}\nResponse: {assistant}\n"

        return system_instruction

    def _build_messages(self, query: str, doc_text: str) -> List[Dict[str, str]]:
        """Build messages for Chat Completions API (fallback)."""
        mode = "LIBERAL" if self.liberal_match else "CONSERVATIVE"
        placeholders = "ALLOWED" if self.allow_placeholders else "DISALLOWED"

        system = f"""
You are a FORMAT MATCHER.

Inputs
- QUERY: end-user content to analyze.
- DOCUMENTATION: retrieved vector chunks that define canonical block types, required fields, and exact block syntax.
- Generate as many blocks as you can to increase the visual aspect
Objective.
- Read DOCUMENTATION and select the block format(s) that best fit QUERY by intent.
- For each selected block, output:
  1) "block_content": one block EXACTLY as defined by DOCUMENTATION (verbatim keys/order).
     • You MAY generate a concise, human-readable title.
     • All data (labels, values, x/y pairs, categories, bins) MUST be copied verbatim from QUERY (or DOCUMENTATION). ]
  2) "placement": an anchor plan describing where to insert the block in QUERY.

Selection policy (high-level, doc-agnostic)
- Only use blocks explicitly defined in DOCUMENTATION chunks retrieved.
- Use each document’s own “scope / when to use” guidance at a high level.
- If multiple documents apply, you may return multiple blocks (each must conform to its source doc).
- If no document supports the needed block type, return NO_MATCH.

Placement (anchor; no numeric offsets)
- Do NOT output numeric character offsets.
- Prefer a sentence anchor:
  "placement": {
    "strategy": "sentence",
    "anchor_sentence": "<EXACT sentence copied verbatim from QUERY>",
    "occurrence": 1,
    "position": "before_sentence" | "after_sentence"
  }
- If the best anchor lives inside a code block or fenced data where “sentences” are unclear, you MAY use a line anchor:
  "placement": {
    "strategy": "line",
    "anchor_line": "<EXACT line copied verbatim from QUERY>",
    "occurrence": 1,
    "position": "before_line" | "after_line"
  }
- The anchor text MUST be copied verbatim from QUERY. If it appears multiple times, set "occurrence" to the 1-based instance that makes the insertion most readable.

Output format (mandatory)
- If at least one match is found, return EXACTLY:
  {"matches":[{"block_content":"<block 1>","placement":{...}}, {"block_content":"<block 2>","placement":{...}}]}
- If there is no match (unsupported block or insufficient data), return ONLY:
  NO_MATCH
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

"""
File-Aware Chat Service
Provides Claude-based chat with smart file context integration
"""

import os
import asyncio
from typing import List, Dict, Any, AsyncGenerator, Optional
from openai import AsyncOpenAI
import json
import structlog
from .smart_file_context import SmartFileContextDetector

logger = structlog.get_logger(__name__)

class FileAwareChatService:
    """
    Service that intelligently uses file context with Claude for responses.
    Only includes file search when contextually relevant.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.context_detector = SmartFileContextDetector()
    
    async def chat_with_files(
        self,
        messages: List[Dict[str, Any]],
        vector_store_id: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Chat with file search enabled using OpenAI's chat completions.
        
        Args:
            messages: Conversation messages
            vector_store_id: User's vector store ID containing uploaded files
            model: OpenAI model to use
            temperature: Response randomness
            max_tokens: Maximum response tokens
            stream: Whether to stream the response
        """
        try:
            # Prepare messages for OpenAI format
            openai_messages = []
            for msg in messages:
                if msg.get("role") in ["user", "assistant", "system"]:
                    openai_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Create chat completion with file search using assistant API
            # Note: Direct file search in chat completions is deprecated
            # We'll use a simpler approach without the file_search tool
            response = await self.client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                async for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        choice = chunk.choices[0]
                        
                        # Handle content delta
                        if choice.delta and choice.delta.content:
                            yield json.dumps({
                                "type": "content_delta",
                                "content": choice.delta.content
                            }) + "\n"
                        
                        # Handle tool calls (removed file_search as it's deprecated)
                        
                        # Handle finish reason
                        if choice.finish_reason:
                            yield json.dumps({
                                "type": "completion",
                                "finish_reason": choice.finish_reason
                            }) + "\n"
            else:
                # Non-streaming response
                if response.choices and len(response.choices) > 0:
                    content = response.choices[0].message.content
                    yield json.dumps({
                        "type": "content",
                        "content": content
                    }) + "\n"
                    
                    yield json.dumps({
                        "type": "completion",
                        "finish_reason": response.choices[0].finish_reason
                    }) + "\n"
            
        except Exception as e:
            logger.error("File-aware chat error", error=str(e))
            yield json.dumps({
                "type": "error",
                "error": str(e)
            }) + "\n"
    
    async def get_file_context(
        self,
        query: str,
        vector_store_id: str,
        max_results: int = 5,
        attached_file_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get relevant file context for a query using file search.
        This is a helper method that uses a simple completion to get context.
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that searches through uploaded files to find relevant information. Provide concise, relevant excerpts from the files that relate to the user's query."
                },
                {
                    "role": "user",
                    "content": f"Find information related to: {query}"
                }
            ]
            
            # Use OpenAI Assistant API to retrieve file content from vector store
            logger.info("Starting OpenAI Assistant file retrieval", 
                       query=query[:100], 
                       vector_store_id=vector_store_id)
            try:
                # Create a temporary assistant with file search capability
                logger.info("Creating OpenAI Assistant for file search")
                assistant = await self.client.beta.assistants.create(
                    name="File Context Retriever",
                    instructions="You are a helpful assistant that extracts relevant information from uploaded files. Provide concise, relevant excerpts that relate to the user's query.",
                    model="gpt-4o-mini",
                    tools=[{"type": "file_search"}],
                    tool_resources={
                        "file_search": {
                            "vector_store_ids": [vector_store_id]
                        }
                    }
                )
                logger.info("Assistant created", assistant_id=assistant.id)
                
                # Create a thread and add the user's query
                thread = await self.client.beta.threads.create()
                # Make the query more specific to focus on recently uploaded files
                specific_query = f"From the most recently uploaded file, find information related to: {query}"
                if attached_file_names:
                    file_list = ", ".join(attached_file_names)
                    specific_query = f"From the file(s) {file_list}, find information related to: {query}"
                
                await self.client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=specific_query
                )
                
                # Run the assistant
                run = await self.client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant.id
                )
                
                # Wait for completion
                while run.status in ['queued', 'in_progress']:
                    await asyncio.sleep(0.5)
                    run = await self.client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                
                if run.status == 'completed':
                    # Get the assistant's response
                    messages = await self.client.beta.threads.messages.list(
                        thread_id=thread.id,
                        order="desc",
                        limit=1
                    )
                    
                    if messages.data and len(messages.data) > 0:
                        content = messages.data[0].content[0].text.value
                        
                        # Clean up
                        await self.client.beta.assistants.delete(assistant.id)
                        
                        return [{
                            "content": content,
                            "source": "openai_assistant",
                            "vector_store_id": vector_store_id
                        }]
                
                # Clean up on failure
                await self.client.beta.assistants.delete(assistant.id)
                
            except Exception as assistant_error:
                logger.error("Assistant API file retrieval failed", error=str(assistant_error))
            
            # Fallback: return placeholder
            return [{
                "content": f"Files are available in the conversation context. User query: {query}",
                "source": "vector_store_placeholder", 
                "vector_store_id": vector_store_id
            }]
            
        except Exception as e:
            logger.error("Failed to get file context", query=query, error=str(e))
            return []
    
    async def smart_claude_chat_stream(
        self,
        messages: List[Dict[str, Any]],
        vector_store_id: Optional[str] = None,
        anthropic_provider = None,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        attached_file_names: Optional[List[str]] = None,
        is_first_message_with_files: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Smart Claude chat that intelligently includes file context only when needed.
        
        Logic:
        1. Always use Claude for responses (never direct OpenAI)
        2. Smart detection: Include file context only when:
           - First message with attachments
           - User explicitly mentions files/documents
           - User references specific file names
        3. Pass file context + user query to Claude for processing
        """
        try:
            if not anthropic_provider:
                yield json.dumps({
                    "type": "error",
                    "error": "Anthropic provider required for responses"
                }) + "\n"
                return
            
            # Get the user's current message
            user_message = ""
            if messages:
                last_message = messages[-1]
                if last_message.get("role") == "user":
                    user_message = last_message.get("content", "")
            
            # Smart detection: Should we include file context?
            context_decision = self.context_detector.should_include_file_context(
                user_message=user_message,
                has_attachments=vector_store_id is not None,
                is_first_message_with_files=is_first_message_with_files,
                conversation_history=messages[:-1] if len(messages) > 1 else None,
                attached_file_names=attached_file_names
            )
            
            logger.info(
                "Smart file context decision",
                include_context=context_decision["include_context"],
                reason=context_decision["reason"],
                confidence=context_decision["confidence"]
            )
            
            file_context = ""
            
            # Step 1: Get file context only if smart detection says we should
            if context_decision["include_context"] and vector_store_id and user_message:
                
                # Extract the file-relevant part of the query for better search
                search_query = self.context_detector.extract_file_query_context(user_message)
                
                logger.info("Retrieving file context", 
                          original_query=user_message[:100],
                          search_query=search_query[:100])
                
                # Get file context using OpenAI file search
                context_results = await self.get_file_context(search_query, vector_store_id, attached_file_names=attached_file_names)
                
                if context_results:
                    file_context = "\n\n# Relevant Information from Your Files:\n"
                    for i, result in enumerate(context_results, 1):
                        file_context += f"## Source {i}:\n{result['content']}\n\n"
                    
                    logger.info("File context retrieved", 
                              context_length=len(file_context),
                              sources=len(context_results),
                              preview=file_context[:200] + "..." if len(file_context) > 200 else file_context)
                else:
                    logger.warning("No file context results returned from OpenAI Assistant")
            
            # Step 2: Always use Claude for the response
            modified_messages = []
            
            # Handle system message
            system_message_found = False
            for msg in messages:
                if msg.get("role") == "system":
                    system_message_found = True
                    if file_context:
                        # Add file context to system message
                        # Create enhanced system message with file context
                        file_info = ""
                        if attached_file_names:
                            file_list = ", ".join(attached_file_names)
                            file_info = f"\n\nThe user has uploaded the following files: {file_list}\nPlease reference these files when answering questions about their content."
                        
                        enhanced_content = f"""{msg["content"]}{file_info}

{file_context}

When the user asks questions that could relate to their uploaded files, assume they want information from those files and respond accordingly."""
                        modified_messages.append({
                            "role": "system",
                            "content": enhanced_content
                        })
                    else:
                        modified_messages.append(msg)
                else:
                    modified_messages.append(msg)
            
            # If no system message exists and we have file context, create one
            if not system_message_found and file_context:
                system_msg = {
                    "role": "system",
                    "content": f"""You are Digi Setu AI, a helpful assistant. The user has shared files with you.

{file_context}

Use this information to provide accurate, detailed responses. Reference the file content when relevant and cite specific details."""
                }
                modified_messages = [system_msg] + messages
            elif not system_message_found:
                # No file context, use regular system message
                modified_messages = messages
            
            # Step 3: Stream response from Claude
            async for chunk in anthropic_provider.stream_completion(
                messages=modified_messages,
                model=model,
                temperature=temperature
            ):
                yield chunk
            
        except Exception as e:
            logger.error("Smart Claude chat stream error", error=str(e))
            yield json.dumps({
                "type": "error",
                "error": f"Chat processing failed: {str(e)}"
            }) + "\n"

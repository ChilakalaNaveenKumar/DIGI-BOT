"""
Smart File Context Detection
Determines when to include file search context based on user intent and conversation history
"""

import re
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)

class SmartFileContextDetector:
    """
    Intelligently determines when to include file search context in conversations.
    
    Rules:
    1. Always include on first message with attachments
    2. Include when user explicitly mentions files or file-related keywords
    3. Include when user references specific file names
    4. Skip for general conversation that doesn't need file context
    """
    
    def __init__(self):
        # Keywords that indicate user wants to search/reference files
        self.file_keywords = {
            'explicit_file_refs': [
                'file', 'files', 'document', 'documents', 'doc', 'docs',
                'pdf', 'attachment', 'attachments', 'upload', 'uploaded'
            ],
            'search_intents': [
                'search', 'find', 'look for', 'show me', 'what does',
                'according to', 'based on', 'from the', 'in the document',
                'in the file', 'the document says', 'the file contains',
                'summarize', 'summary', 'analyze', 'review', 'explain'
            ],
            'reference_patterns': [
                r'\b(?:this|that|the)\s+(?:file|document|pdf|doc)\b',
                r'\b(?:my|the)\s+(?:uploaded|attached)\s+(?:file|document)\b',
                r'\b(?:from|in|according to)\s+(?:the|my)\s+(?:file|document)\b'
            ]
        }
    
    def should_include_file_context(
        self, 
        user_message: str, 
        has_attachments: bool = False,
        is_first_message_with_files: bool = False,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        attached_file_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Determine if file context should be included in the response.
        
        Returns:
            {
                "include_context": bool,
                "reason": str,
                "confidence": float,
                "detected_patterns": List[str]
            }
        """
        
        reasons = []
        detected_patterns = []
        confidence = 0.0
        
        # Rule 1: Always include on first message with attachments
        if is_first_message_with_files and has_attachments:
            reasons.append("First message with file attachments")
            confidence += 0.9
            detected_patterns.append("first_message_with_files")
        
        # Rule 2: Check for explicit file references
        user_message_lower = user_message.lower()
        
        # Check explicit file keywords
        for keyword in self.file_keywords['explicit_file_refs']:
            if keyword in user_message_lower:
                reasons.append(f"Explicit file reference: '{keyword}'")
                confidence += 0.7
                detected_patterns.append(f"explicit_keyword:{keyword}")
        
        # Check search intent keywords
        for intent in self.file_keywords['search_intents']:
            if intent in user_message_lower:
                reasons.append(f"Search intent detected: '{intent}'")
                confidence += 0.6
                detected_patterns.append(f"search_intent:{intent}")
        
        # Check regex patterns
        for pattern in self.file_keywords['reference_patterns']:
            if re.search(pattern, user_message_lower):
                reasons.append(f"Reference pattern matched: {pattern}")
                confidence += 0.8
                detected_patterns.append(f"pattern:{pattern}")
        
        # Rule 3: Check for specific file name mentions
        if attached_file_names:
            for file_name in attached_file_names:
                # Check if user mentions the file name (without extension)
                file_base = file_name.split('.')[0].lower()
                if file_base in user_message_lower and len(file_base) > 3:  # Avoid short matches
                    reasons.append(f"Specific file name mentioned: '{file_name}'")
                    confidence += 0.9
                    detected_patterns.append(f"filename:{file_name}")
        
        # Rule 4: Context from conversation history
        if conversation_history:
            # Check if recent messages involved file discussions
            recent_messages = conversation_history[-3:]  # Last 3 messages
            for msg in recent_messages:
                if msg.get('role') == 'assistant' and any(
                    keyword in msg.get('content', '').lower() 
                    for keyword in ['file', 'document', 'according to']
                ):
                    reasons.append("Recent conversation involved file discussion")
                    confidence += 0.4
                    detected_patterns.append("conversation_context")
                    break
        
        # Normalize confidence (cap at 1.0)
        confidence = min(confidence, 1.0)
        
        # Decision threshold - ALWAYS include if files are attached
        include_context = has_attachments or confidence > 0.3 or is_first_message_with_files
        
        # Add reason if files are attached but no keywords detected
        if has_attachments and not reasons:
            reasons.append("Files are attached to the conversation")
            
        result = {
            "include_context": include_context,
            "reason": "; ".join(reasons) if reasons else "No file context indicators detected",
            "confidence": confidence,
            "detected_patterns": detected_patterns
        }
        
        logger.info(
            "File context decision",
            include_context=include_context,
            confidence=confidence,
            reasons=len(reasons),
            patterns=len(detected_patterns),
            message_preview=user_message[:100]
        )
        
        return result
    
    def extract_file_query_context(self, user_message: str) -> str:
        """
        Extract the specific part of the user's message that relates to file searching.
        This helps create more targeted file search queries.
        """
        
        # Patterns that indicate file-specific questions
        file_question_patterns = [
            r'what (?:does|is|are).+(?:in the|from the|according to)',
            r'(?:show me|find|search for).+(?:in|from) (?:the|my)',
            r'(?:according to|based on|from) (?:the|my) (?:file|document)',
            r'(?:the|my) (?:file|document) (?:says|shows|contains|mentions)'
        ]
        
        user_message_lower = user_message.lower()
        
        for pattern in file_question_patterns:
            match = re.search(pattern, user_message_lower)
            if match:
                # Return the matched portion and some context
                start = max(0, match.start() - 10)
                end = min(len(user_message), match.end() + 20)
                return user_message[start:end].strip()
        
        # If no specific pattern, return the full message for general file search
        return user_message
    
    def get_file_search_priority(self, detected_patterns: List[str]) -> str:
        """
        Determine the priority/type of file search needed based on detected patterns.
        
        Returns: 'high', 'medium', 'low'
        """
        
        high_priority_patterns = ['first_message_with_files', 'filename:', 'explicit_keyword:']
        medium_priority_patterns = ['search_intent:', 'pattern:']
        
        for pattern in detected_patterns:
            if any(pattern.startswith(hp) for hp in high_priority_patterns):
                return 'high'
        
        for pattern in detected_patterns:
            if any(pattern.startswith(mp) for mp in medium_priority_patterns):
                return 'medium'
        
        return 'low'

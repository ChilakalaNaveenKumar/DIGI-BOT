"""
Analysis Logger - Comprehensive logging for debugging API calls and component generation
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger(__name__)

class AnalysisLogger:
    """Comprehensive logger for analysis debugging."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create separate log files
        self.api_counts_file = self.log_dir / "api_counts.log"
        self.component_results_file = self.log_dir / "component_results.log"
        self.checkpoint_analysis_file = self.log_dir / "checkpoint_analysis.log"
        
        # Initialize counters
        self.session_start = time.time()
        self.api_call_count = 0
        self.component_count = 0
        self.checkpoint_count = 0
        
        logger.info("AnalysisLogger initialized", log_dir=str(self.log_dir))
    
    def log_api_call(self, provider: str, model: str, endpoint: str, tokens_used: int = 0):
        """Log API call with metrics."""
        self.api_call_count += 1
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "session_time": time.time() - self.session_start,
            "call_number": self.api_call_count,
            "provider": provider,
            "model": model,
            "endpoint": endpoint,
            "tokens_used": tokens_used
        }
        
        with open(self.api_counts_file, "a") as f:
            f.write(f"{json.dumps(entry)}\n")
    
    def log_component_generated(self, component: Dict[str, Any], block_info: Dict[str, Any]):
        """Log each component that gets generated."""
        self.component_count += 1
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "session_time": time.time() - self.session_start,
            "component_number": self.component_count,
            "component_type": component.get("component_type", "unknown"),
            "confidence": component.get("confidence", 0.0),
            "markdown_length": len(component.get("markdown", "")),
            "injection_position": component.get("injection_position", 0),
            "block_start": block_info.get("start_position", 0),
            "block_end": block_info.get("end_position", 0),
            "block_content_preview": block_info.get("content", "")[:100] + "..." if len(block_info.get("content", "")) > 100 else block_info.get("content", ""),
            "full_component": component
        }
        
        with open(self.component_results_file, "a") as f:
            f.write(f"{json.dumps(entry)}\n")
    
    def log_checkpoint_analysis(self, checkpoint_info: Dict[str, Any], blocks_found: int, components_generated: int, passed_filters: List[Dict[str, Any]]):
        """Log checkpoint analysis results."""
        self.checkpoint_count += 1
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "session_time": time.time() - self.session_start,
            "checkpoint_number": self.checkpoint_count,
            "token_count": checkpoint_info.get("token_count", 0),
            "content_length": len(checkpoint_info.get("content_chunk", "")),
            "blocks_found": blocks_found,
            "components_generated": components_generated,
            "components_passed_filters": len(passed_filters),
            "passed_components": [
                {
                    "type": comp.get("component_type", "unknown"),
                    "confidence": comp.get("confidence", 0.0)
                }
                for comp in passed_filters
            ],
            "content_preview": checkpoint_info.get("content_chunk", "")[:200] + "..." if len(checkpoint_info.get("content_chunk", "")) > 200 else checkpoint_info.get("content_chunk", "")
        }
        
        with open(self.checkpoint_analysis_file, "a") as f:
            f.write(f"{json.dumps(entry)}\n")
    
    def log_session_summary(self):
        """Log session summary to all files."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "session_duration": time.time() - self.session_start,
            "total_api_calls": self.api_call_count,
            "total_components": self.component_count,
            "total_checkpoints": self.checkpoint_count,
            "session_type": "SUMMARY"
        }
        
        # Write to all log files
        for log_file in [self.api_counts_file, self.component_results_file, self.checkpoint_analysis_file]:
            with open(log_file, "a") as f:
                f.write(f"SESSION_SUMMARY: {json.dumps(summary)}\n")
        
        logger.info("Session summary logged", **summary)

# Global logger instance
analysis_logger = AnalysisLogger()

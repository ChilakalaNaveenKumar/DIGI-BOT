"""
Logging Configuration - Reduce terminal noise while keeping file logs
"""

import logging
import sys

def configure_logging():
    """Configure logging to reduce terminal noise."""
    
    # Suppress HTTP request logs from httpx and other libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    
    # Keep our application logs at INFO level for important events only
    logging.getLogger("app").setLevel(logging.INFO)
    
    # Reduce uvicorn access logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Configure root logger to be less verbose
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Only show warnings and errors from third-party libraries
    for logger_name in ["urllib3", "requests", "aiohttp", "asyncio"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

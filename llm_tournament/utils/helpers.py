"""
Helper functions for the LLM Tournament application.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime


def ensure_directory_exists(path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
    """
    os.makedirs(path, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string for use as a filename.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters with underscores
    return re.sub(r'[\\/*?:"<>|]', "_", filename)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_time_delta(seconds: float) -> str:
    """
    Format a time delta as a human-readable string.
    
    Args:
        seconds: Number of seconds
        
    Returns:
        Formatted time string (e.g., "2h 30m 15s")
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def json_serializer(obj: Any) -> Union[str, Dict[str, Any]]:
    """
    JSON serializer for objects not serializable by default json code.
    
    Args:
        obj: Object to serialize
        
    Returns:
        Serialized object
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def save_json(data: Any, file_path: str, indent: int = 2) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: File path
        indent: JSON indentation level
    """
    ensure_directory_exists(os.path.dirname(file_path))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, default=json_serializer)


def load_json(file_path: str) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path: File path
        
    Returns:
        Loaded data
        
    Raises:
        FileNotFoundError: If file not found
        json.JSONDecodeError: If JSON is invalid
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_progress_bar(progress: float, width: int = 30, fill_char: str = '#', empty_char: str = '-') -> str:
    """
    Create a text-based progress bar.
    
    Args:
        progress: Progress percentage (0-100)
        width: Width of the bar in characters
        fill_char: Character for filled portion
        empty_char: Character for empty portion
        
    Returns:
        Progress bar string
    """
    filled_width = int(width * progress / 100)
    bar = fill_char * filled_width + empty_char * (width - filled_width)
    return f"[{bar}] {progress:.1f}%"


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from text that may contain markdown, code blocks, etc.
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        Extracted JSON data or None if extraction fails
    """
    # Try to extract JSON from markdown code blocks
    json_matches = re.findall(r'```(?:json)?\s*([\s\S]*?)```', text)
    if json_matches:
        for json_text in json_matches:
            try:
                return json.loads(json_text.strip())
            except:
                continue
    
    # Look for parts that might be JSON (between curly braces)
    json_matches = re.findall(r'{[\s\S]*}', text)
    if json_matches:
        for json_text in json_matches:
            try:
                return json.loads(json_text.strip())
            except:
                continue
    
    # Try the whole text
    try:
        return json.loads(text.strip())
    except:
        return None

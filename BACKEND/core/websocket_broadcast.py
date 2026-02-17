"""
WebSocket broadcast utilities for real-time attack monitoring
"""

from typing import Dict, Any
import json
import os
from pathlib import Path

# Global reference to ConnectionManager - will be set by api_server
_manager = None

# Log file path
LOG_FILE = Path(__file__).parent.parent / "chat_log.json"


def set_manager(manager):
    """Set the global ConnectionManager instance"""
    global _manager
    _manager = manager


async def broadcast_attack_log(message: Dict[str, Any]):
    """
    Broadcast attack log message to all connected WebSocket clients
    
    Args:
        message: Dictionary containing type and data fields
    """
    global _manager
    if _manager is not None:
        await _manager.broadcast(message)
    # If manager not set, silently ignore (allows orchestrators to work standalone)
    
    # Log turn_completed messages to file
    if message.get("type") == "turn_completed" and "data" in message:
        log_chat_data(message["data"])


def log_chat_data(data: Dict[str, Any]):
    """
    Log chat data to JSON file
    
    Args:
        data: The data from turn_completed message
    """
    try:
        # Prepare the log entry
        log_entry = {
            "request": data.get("prompt", ""),
            "response": data.get("response", ""),
            "attack_type": data.get("category", ""),
            "risk_category": data.get("risk_display", ""),
            "attack_category": data.get("category", ""),
            "run": data.get("run", 0),
            "turn": data.get("turn", 0),
            "timestamp": data.get("timestamp", "")
        }
        
        # Load existing data or create new list
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = []
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []
        
        # Append new entry
        existing_data.append(log_entry)
        
        # Write back to file
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error logging chat data: {e}")

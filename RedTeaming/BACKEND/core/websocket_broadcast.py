"""
WebSocket broadcast utilities for real-time attack monitoring
"""

from typing import Dict, Any

# Global reference to ConnectionManager - will be set by api_server
_manager = None


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

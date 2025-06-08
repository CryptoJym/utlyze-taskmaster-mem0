"""
Mem0 Cloud Client Integration
Handles all interactions with Mem0 cloud memory service
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from mem0 import MemoryClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UtlyzeMem0Client:
    """Centralized Mem0 client for Utlyze project memory management"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MEM0_API_KEY")
        if not self.api_key:
            raise ValueError("MEM0_API_KEY not found in environment")
        
        self.client = MemoryClient(api_key=self.api_key)
        self.user_id = "utlyze"
        logger.info("Mem0 client initialized for Utlyze")
    
    def add_task_update(self, task_data: Dict[str, Any]) -> str:
        """Add a task update to memory"""
        memory_content = f"""
        Task: {task_data.get('name', 'Unknown')}
        Status: {task_data.get('status', 'Unknown')}
        Progress: {task_data.get('progress', 0)}%
        Description: {task_data.get('description', '')}
        Assigned Agent: {task_data.get('agent', 'Unassigned')}
        Files: {', '.join(task_data.get('affected_files', []))}
        Last Updated: {datetime.now().isoformat()}
        """
        
        metadata = {
            "type": "task_update",
            "task_id": task_data.get('id'),
            "project": "utlyze",
            "timestamp": datetime.now().isoformat(),
            "agent": task_data.get('agent'),
            "status": task_data.get('status')
        }
        
        result = self.client.add(memory_content, user_id=self.user_id, metadata=metadata)
        logger.info(f"Task update stored: {task_data.get('name')}")
        return result
    
    def add_terminal_activity(self, activity_data: Dict[str, Any]) -> str:
        """Log terminal activity"""
        memory_content = f"""
        Terminal Activity:
        Directory: {activity_data.get('cwd', 'Unknown')}
        Branch: {activity_data.get('git_branch', 'No git')}
        Command: {activity_data.get('last_command', '')}
        Time: {datetime.now().isoformat()}
        """
        
        metadata = {
            "type": "terminal_activity",
            "cwd": activity_data.get('cwd'),
            "timestamp": datetime.now().isoformat()
        }
        
        result = self.client.add(memory_content, user_id=self.user_id, metadata=metadata)
        return result
    
    def get_current_context(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get current project context"""
        # Search for recent memories
        recent_memories = self.client.search(
            "utlyze project",
            user_id=self.user_id,
            limit=limit
        )
        
        # Format for easy consumption
        context = []
        for memory in recent_memories:
            context.append({
                "content": memory.get("memory", ""),
                "metadata": memory.get("metadata", {}),
                "created_at": memory.get("created_at", "")
            })
        
        return context
    
    def get_task_context(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all memories related to a specific task"""
        task_memories = self.client.search(
            f"task_id: {task_id}",
            user_id=self.user_id
        )
        return task_memories
    
    def sync_with_taskmaster(self, taskmaster_state: Dict[str, Any]) -> Dict[str, Any]:
        """Sync current Taskmaster state to memory"""
        sync_result = {
            "synced_tasks": 0,
            "errors": []
        }
        
        # Sync all active tasks
        for task in taskmaster_state.get("tasks", []):
            try:
                self.add_task_update(task)
                sync_result["synced_tasks"] += 1
            except Exception as e:
                sync_result["errors"].append(f"Error syncing task {task.get('id')}: {str(e)}")
        
        # Add sync summary
        summary = f"""
        Taskmaster Sync Complete:
        Total Tasks: {len(taskmaster_state.get('tasks', []))}
        Active Tasks: {len([t for t in taskmaster_state.get('tasks', []) if t.get('status') != 'completed'])}
        Sync Time: {datetime.now().isoformat()}
        """
        
        self.client.add(
            summary,
            user_id=self.user_id,
            metadata={"type": "sync_summary", "timestamp": datetime.now().isoformat()}
        )
        
        return sync_result
    
    def cleanup_old_memories(self, days: int = 30) -> int:
        """Clean up old memories (optional utility)"""
        # Note: Mem0 cloud handles retention, but this is here if needed
        # Would need to implement based on Mem0's deletion API
        logger.info(f"Cleanup requested for memories older than {days} days")
        return 0


if __name__ == "__main__":
    # Test the client
    client = UtlyzeMem0Client()
    
    # Test adding a task update
    test_task = {
        "id": "test-001",
        "name": "Setup Mem0 Integration",
        "status": "in_progress",
        "progress": 75,
        "description": "Integrating Mem0 with Taskmaster",
        "agent": "setup-agent",
        "affected_files": ["src/mem0_client.py", "README.md"]
    }
    
    result = client.add_task_update(test_task)
    print(f"Test task added: {result}")
    
    # Get current context
    context = client.get_current_context()
    print(f"\nCurrent context ({len(context)} memories):")
    for memory in context:
        print(f"- {memory['content'][:100]}...")
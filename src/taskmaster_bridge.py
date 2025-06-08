"""
Taskmaster Bridge - Webhook handler for Taskmaster updates
Receives task updates and syncs them to Mem0 cloud
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from mem0_client import UtlyzeMem0Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Utlyze Taskmaster-Mem0 Bridge")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Mem0 client
mem0_client = UtlyzeMem0Client()


class TaskUpdate(BaseModel):
    """Task update model from Taskmaster"""
    id: str
    name: str
    status: str
    progress: int
    description: Optional[str] = ""
    agent: Optional[str] = "unassigned"
    affected_files: Optional[list] = []
    metadata: Optional[Dict[str, Any]] = {}


class TaskmasterSync(BaseModel):
    """Full Taskmaster state sync"""
    tasks: list
    timestamp: Optional[str] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Utlyze Taskmaster-Mem0 Bridge",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/webhook/task-update")
async def handle_task_update(task: TaskUpdate, background_tasks: BackgroundTasks):
    """Handle individual task updates from Taskmaster"""
    try:
        # Log the update
        logger.info(f"Received task update: {task.name} ({task.status})")
        
        # Add to background tasks to not block the response
        background_tasks.add_task(
            process_task_update,
            task.dict()
        )
        
        return {
            "status": "accepted",
            "task_id": task.id,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error handling task update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/sync")
async def handle_full_sync(sync_data: TaskmasterSync):
    """Handle full Taskmaster state sync"""
    try:
        logger.info(f"Received full sync with {len(sync_data.tasks)} tasks")
        
        # Perform sync
        result = mem0_client.sync_with_taskmaster(sync_data.dict())
        
        return {
            "status": "synced",
            "synced_tasks": result["synced_tasks"],
            "errors": result["errors"],
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error during sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/context")
async def get_current_context(limit: int = 10):
    """Get current project context from Mem0"""
    try:
        context = mem0_client.get_current_context(limit=limit)
        return {
            "context": context,
            "count": len(context),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/task/{task_id}/history")
async def get_task_history(task_id: str):
    """Get all memories related to a specific task"""
    try:
        memories = mem0_client.get_task_context(task_id)
        return {
            "task_id": task_id,
            "memories": memories,
            "count": len(memories),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting task history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_task_update(task_data: Dict[str, Any]):
    """Process task update in background"""
    try:
        # Add to Mem0
        mem0_client.add_task_update(task_data)
        
        # If task is completed, trigger additional actions
        if task_data.get("status") == "completed":
            await handle_task_completion(task_data)
        
        # If task mentions specific files, add file context
        if task_data.get("affected_files"):
            await add_file_context(task_data)
            
    except Exception as e:
        logger.error(f"Error processing task update: {str(e)}")


async def handle_task_completion(task_data: Dict[str, Any]):
    """Special handling for completed tasks"""
    completion_memory = f"""
    Task Completed: {task_data['name']}
    Total Progress Time: {task_data.get('metadata', {}).get('duration', 'Unknown')}
    Files Modified: {', '.join(task_data.get('affected_files', []))}
    Completion Time: {datetime.now().isoformat()}
    
    This task is now complete and can be referenced for future similar tasks.
    """
    
    mem0_client.client.add(
        completion_memory,
        user_id="utlyze",
        metadata={
            "type": "task_completion",
            "task_id": task_data['id'],
            "timestamp": datetime.now().isoformat()
        }
    )


async def add_file_context(task_data: Dict[str, Any]):
    """Add context about files mentioned in the task"""
    for file_path in task_data.get("affected_files", []):
        file_memory = f"""
        File Activity: {file_path}
        Related Task: {task_data['name']}
        Task Status: {task_data['status']}
        Last Modified: {datetime.now().isoformat()}
        """
        
        mem0_client.client.add(
            file_memory,
            user_id="utlyze",
            metadata={
                "type": "file_activity",
                "file_path": file_path,
                "task_id": task_data['id'],
                "timestamp": datetime.now().isoformat()
            }
        )


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default
    port = int(os.getenv("TASKMASTER_BRIDGE_PORT", "8080"))
    
    logger.info(f"Starting Taskmaster-Mem0 Bridge on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
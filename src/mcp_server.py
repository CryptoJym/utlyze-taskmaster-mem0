"""
MCP Server for Utlyze Mem0 Integration
Provides memory access to Cursor, VSCode, and other MCP-compatible tools
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mem0_client import UtlyzeMem0Client
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UtlyzeMem0MCPServer:
    """MCP Server providing Mem0 memory access"""
    
    def __init__(self):
        self.server = Server("utlyze-mem0")
        self.mem0_client = UtlyzeMem0Client()
        self._setup_tools()
        
    def _setup_tools(self):
        """Register available tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="get_context",
                    description="Get current Utlyze project context from memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Number of memories to retrieve",
                                "default": 10
                            }
                        }
                    }
                ),
                Tool(
                    name="search_memory",
                    description="Search Utlyze memories for specific content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Max results",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="add_memory",
                    description="Add a new memory to Utlyze project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Memory content to add"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata",
                                "default": {}
                            }
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="get_task_history",
                    description="Get history for a specific task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to get history for"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="log_activity",
                    description="Log current development activity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "activity": {
                                "type": "string",
                                "description": "Description of current activity"
                            },
                            "files": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Files being worked on",
                                "default": []
                            }
                        },
                        "required": ["activity"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "get_context":
                    limit = arguments.get("limit", 10)
                    context = self.mem0_client.get_current_context(limit=limit)
                    
                    if not context:
                        return [TextContent(
                            type="text",
                            text="No memories found in current context."
                        )]
                    
                    # Format context for display
                    formatted = "🧠 Current Utlyze Context:\n\n"
                    for i, memory in enumerate(context):
                        formatted += f"{i+1}. {memory['content'].strip()}\n"
                        if memory.get('metadata'):
                            formatted += f"   Type: {memory['metadata'].get('type', 'unknown')}\n"
                            formatted += f"   Time: {memory['metadata'].get('timestamp', 'unknown')}\n"
                        formatted += "\n"
                    
                    return [TextContent(type="text", text=formatted)]
                
                elif name == "search_memory":
                    query = arguments["query"]
                    limit = arguments.get("limit", 10)
                    
                    results = self.mem0_client.client.search(
                        query,
                        user_id="utlyze",
                        limit=limit
                    )
                    
                    if not results:
                        return [TextContent(
                            type="text",
                            text=f"No memories found matching: {query}"
                        )]
                    
                    formatted = f"🔍 Search Results for '{query}':\n\n"
                    for i, result in enumerate(results):
                        formatted += f"{i+1}. {result.get('memory', '').strip()}\n"
                        formatted += f"   Score: {result.get('score', 0):.2f}\n\n"
                    
                    return [TextContent(type="text", text=formatted)]
                
                elif name == "add_memory":
                    content = arguments["content"]
                    metadata = arguments.get("metadata", {})
                    metadata["source"] = "mcp_cursor"
                    metadata["timestamp"] = datetime.now().isoformat()
                    
                    # Use messages format for mem0 API
                    messages = [{"role": "user", "content": content}]
                    result = self.mem0_client.client.add(
                        messages,
                        user_id="utlyze",
                        metadata=metadata
                    )
                    
                    return [TextContent(
                        type="text",
                        text=f"✅ Memory added successfully: {result}"
                    )]
                
                elif name == "get_task_history":
                    task_id = arguments["task_id"]
                    memories = self.mem0_client.get_task_context(task_id)
                    
                    if not memories:
                        return [TextContent(
                            type="text",
                            text=f"No history found for task: {task_id}"
                        )]
                    
                    formatted = f"📋 Task History for {task_id}:\n\n"
                    for memory in memories:
                        formatted += f"- {memory.get('memory', '').strip()}\n"
                        if memory.get('created_at'):
                            formatted += f"  Time: {memory['created_at']}\n"
                        formatted += "\n"
                    
                    return [TextContent(type="text", text=formatted)]
                
                elif name == "log_activity":
                    activity = arguments["activity"]
                    files = arguments.get("files", [])
                    
                    memory_content = f"""
                    Development Activity:
                    {activity}
                    Files: {', '.join(files) if files else 'None specified'}
                    Time: {datetime.now().isoformat()}
                    Source: Cursor/VSCode
                    """
                    
                    # Use messages format for mem0 API
                    messages = [{"role": "user", "content": memory_content}]
                    result = self.mem0_client.client.add(
                        messages,
                        user_id="utlyze",
                        metadata={
                            "type": "development_activity",
                            "source": "mcp_cursor",
                            "files": files,
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    
                    return [TextContent(
                        type="text",
                        text=f"✅ Activity logged: {activity}"
                    )]
                
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Utlyze Mem0 MCP Server started")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    server = UtlyzeMem0MCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
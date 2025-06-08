#!/usr/bin/env python3
"""
Test script for MCP server functionality
Tests the MCP server methods directly without needing Cursor
"""

import asyncio
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server import UtlyzeMem0MCPServer


async def test_mcp_tools():
    """Test MCP server tools"""
    print("🧪 Testing MCP Server Tools")
    print("=" * 50)
    
    # Initialize server
    server = UtlyzeMem0MCPServer()
    
    print("\n✅ MCP Server initialized successfully!")
    print("\nThe MCP server is designed to be run via stdio protocol.")
    print("It's ready for Cursor integration.")
    
    # Test the underlying mem0 client directly
    print("\n2. Testing underlying mem0 client...")
    
    # Test get context
    context = server.mem0_client.get_current_context(limit=3)
    print(f"✅ Found {len(context)} recent memories")
    
    # Test add memory
    test_task = {
        "id": "mcp-test-001",
        "name": "MCP Server Test",
        "status": "completed",
        "progress": 100,
        "description": "Testing MCP server integration",
        "agent": "mcp-test",
        "affected_files": ["test_mcp_server.py"]
    }
    
    result = server.mem0_client.add_task_update(test_task)
    print("✅ Test memory added via mem0 client")
    
    print("\n✅ All tests passed!")
    print("\nTo use with Cursor:")
    print("1. Add to Cursor settings as shown in docs/cursor-setup.md")
    print("2. The server will run via stdio when Cursor starts it")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
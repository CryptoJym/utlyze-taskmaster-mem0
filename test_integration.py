#!/usr/bin/env python3
"""
Quick integration test for Utlyze Taskmaster-Mem0
Run this to verify your setup is working correctly
"""

import os
import sys
import asyncio
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mem0_client import UtlyzeMem0Client


async def test_integration():
    """Test the Mem0 integration"""
    print("🧪 Testing Utlyze Taskmaster-Mem0 Integration")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("MEM0_API_KEY"):
        print("❌ MEM0_API_KEY not set!")
        print("   Set it with: export MEM0_API_KEY='your-api-key'")
        return False
    
    try:
        # Initialize client
        print("\n1. Initializing Mem0 client...")
        client = UtlyzeMem0Client()
        print("✅ Client initialized")
        
        # Add a test memory
        print("\n2. Adding test memory...")
        test_task = {
            "id": f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "name": "Integration Test Task",
            "status": "completed",
            "progress": 100,
            "description": "Testing Utlyze Taskmaster-Mem0 integration",
            "agent": "test-agent",
            "affected_files": ["test_integration.py"]
        }
        
        result = client.add_task_update(test_task)
        print(f"✅ Memory added: {result}")
        
        # Retrieve context
        print("\n3. Retrieving current context...")
        context = client.get_current_context(limit=5)
        print(f"✅ Found {len(context)} memories")
        
        if context:
            print("\nRecent memories:")
            for i, memory in enumerate(context[:3]):
                content = memory['content'].strip().replace('\n', ' ')[:80]
                print(f"  {i+1}. {content}...")
        
        # Test terminal activity
        print("\n4. Logging terminal activity...")
        activity = {
            "cwd": os.getcwd(),
            "git_branch": "main",
            "last_command": "python test_integration.py"
        }
        client.add_terminal_activity(activity)
        print("✅ Activity logged")
        
        print("\n✅ All tests passed! Your integration is working correctly.")
        print("\nNext steps:")
        print("1. Run ./quickstart.sh for full setup")
        print("2. Configure Cursor using docs/cursor-setup.md")
        print("3. Start the Taskmaster bridge: python src/taskmaster_bridge.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your MEM0_API_KEY is valid")
        print("2. Ensure you have internet connection")
        print("3. Verify mem0ai package is installed: pip install mem0ai")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_integration())
    sys.exit(0 if success else 1)
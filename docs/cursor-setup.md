# Cursor IDE Setup Guide for Utlyze Mem0 Integration

This guide will help you configure Cursor IDE to automatically connect to the Utlyze Mem0 memory system.

## Prerequisites

1. Mem0 Cloud API key (from your $250/month subscription)
2. Python 3.8+ installed
3. Utlyze-Taskmaster-Mem0 repository cloned

## Step 1: Install Dependencies

```bash
cd /path/to/utlyze-taskmaster-mem0
pip install -r requirements.txt
```

## Step 2: Set Environment Variables

Add to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
export MEM0_API_KEY="your-mem0-cloud-api-key"
export UTLYZE_MEM0_DIR="/path/to/utlyze-taskmaster-mem0"
```

## Step 3: Configure Cursor MCP Settings

1. Open Cursor Settings (Cmd+, on Mac, Ctrl+, on Windows/Linux)
2. Search for "MCP" or "Model Context Protocol"
3. Add the following configuration:

```json
{
  "mcpServers": {
    "utlyze-mem0": {
      "command": "python",
      "args": ["${env:UTLYZE_MEM0_DIR}/src/mcp_server.py"],
      "env": {
        "MEM0_API_KEY": "${env:MEM0_API_KEY}",
        "PYTHONPATH": "${env:UTLYZE_MEM0_DIR}/src"
      }
    }
  }
}
```

## Step 4: Test the Connection

1. Restart Cursor
2. Open the AI chat (Cmd+K)
3. Type: `/utlyze-mem0 get_context`

You should see your current Utlyze project context loaded from Mem0.

## Step 5: Available Commands

In Cursor AI chat, you can use these commands:

### Get Current Context
```
/utlyze-mem0 get_context limit=10
```

### Search Memories
```
/utlyze-mem0 search_memory query="API development" limit=5
```

### Add Memory
```
/utlyze-mem0 add_memory content="Working on authentication system" metadata={"type": "note"}
```

### Get Task History
```
/utlyze-mem0 get_task_history task_id="TASK-001"
```

### Log Activity
```
/utlyze-mem0 log_activity activity="Implementing user login" files=["auth.py", "login.vue"]
```

## Step 6: Automatic Context Loading

To have Cursor automatically load context when opening a project:

1. Create `.cursor/startup.mcp` in your project root:

```json
{
  "onStartup": [
    {
      "server": "utlyze-mem0",
      "tool": "get_context",
      "arguments": {"limit": 5}
    }
  ]
}
```

## Troubleshooting

### MCP Server Not Found
- Ensure Python path is correct in the configuration
- Check that all dependencies are installed
- Verify MEM0_API_KEY is set

### No Memories Loading
- Check your Mem0 API key is valid
- Ensure you have memories stored for the "utlyze" user
- Try running the MCP server manually to see errors:
  ```bash
  python /path/to/utlyze-taskmaster-mem0/src/mcp_server.py
  ```

### Connection Timeouts
- The first connection might take a moment as it initializes
- Check your internet connection for Mem0 cloud access

## Advanced Configuration

### Custom Memory Filters
You can modify the MCP server to add custom filtering:

```python
# In mcp_server.py, add custom tool
Tool(
    name="get_today_tasks",
    description="Get only today's task updates",
    # ... implementation
)
```

### Integration with Taskmaster
Ensure your Taskmaster webhook is configured to send updates to:
```
http://localhost:8080/webhook/task-update
```

## Best Practices

1. **Regular Syncing**: The system passively collects data, but you can manually sync with `/utlyze-mem0 add_memory` for important milestones

2. **Meaningful Metadata**: When adding memories, include relevant metadata for better search

3. **Task Association**: Always include task IDs when relevant for better context tracking

4. **Privacy**: Remember that all data is stored in your private Mem0 cloud instance

## Support

For issues specific to:
- Mem0 integration: Check `/path/to/utlyze-taskmaster-mem0/logs/`
- Cursor MCP: Check Cursor's developer console (Cmd+Shift+P > "Developer: Toggle Developer Tools")
- Taskmaster: Ensure the bridge service is running (`python src/taskmaster_bridge.py`)
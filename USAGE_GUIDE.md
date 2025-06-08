# Utlyze Taskmaster-Mem0 Usage Guide

## Overview
This guide explains how to use the Utlyze Taskmaster-Mem0 integration for seamless context awareness across your development environment.

## Quick Start

### 1. Environment Setup
```bash
# Set your Mem0 API key
export MEM0_API_KEY="your-mem0-cloud-api-key"

# Optional: Enable auto-monitoring
export UTLYZE_AUTO_MONITOR=1

# Source the initialization script
source /path/to/utlyze-taskmaster-mem0/shell/init.sh
```

### 2. Basic Commands

#### Show Current Context
```bash
utx  # or utlyze_context
```
Shows your last 10 memories from Mem0, including:
- Recent task updates
- Development activities
- Terminal sessions
- File modifications

#### Activity Monitor
```bash
# Start background monitoring
utlyze_monitor start

# Check status
utlyze_monitor status

# Stop monitoring
utlyze_monitor stop

# One-time sync
utlyze_monitor once
```

## Features

### 1. Automatic Context Loading
Every time you open a new terminal:
- Loads your last 5 memories
- Shows current project context
- Logs the new session start

### 2. Passive Activity Collection
The activity monitor tracks:
- Current working directory
- Git branch and status
- Recently modified files
- Project type (Python/Node.js)
- Virtual environment status

### 3. Taskmaster Integration
When using Taskmaster:
- Every task update syncs to Mem0
- Task completions are specially marked
- File associations are tracked
- Progress history is maintained

### 4. Cursor IDE Integration
In Cursor, you can:
```
/utlyze-mem0 get_context
/utlyze-mem0 search_memory query="authentication"
/utlyze-mem0 add_memory content="Important note about API"
```

## Common Workflows

### Starting Your Day
```bash
# 1. Open terminal - context loads automatically
# 2. Check your current context
utx

# 3. Start activity monitoring
utlyze_monitor start
```

### Working on a Task
```bash
# The system automatically tracks:
# - Which files you're modifying
# - Your git commits
# - Task progress from Taskmaster
# - Time spent in different directories
```

### Switching Projects
```bash
# Context switches automatically when you:
cd /path/to/another/project

# Manual sync if needed
utlyze_monitor once
```

### Finding Past Work
```python
# In Python or through MCP
from mem0_client import UtlyzeMem0Client
client = UtlyzeMem0Client()

# Search for specific work
results = client.search_memories("authentication API")

# Get task history
history = client.get_task_history("TASK-001")
```

## Advanced Usage

### Custom Memory Types
Add specialized memories:
```python
client.client.add(
    [{"role": "user", "content": "Design decision: Using JWT for auth"}],
    user_id="utlyze",
    metadata={
        "type": "architecture_decision",
        "project": "backend-api",
        "tags": ["security", "authentication"]
    }
)
```

### Filtering Memories
Get specific types of memories:
```python
# Get only task completions
completions = client.search_memories("", metadata={"type": "task_completion"})

# Get activity from specific project
project_activity = client.search_memories("", metadata={"project": "utlyze-backend"})
```

### Integration with AI Tools
The memory system works with:
- Claude (via MCP)
- Cursor IDE
- Any tool that supports MCP protocol
- Custom scripts and automation

## Tips & Best Practices

### 1. Memory Hygiene
- Let the system collect passively
- Add explicit memories for important decisions
- Use meaningful task descriptions in Taskmaster

### 2. Performance
- Activity monitor runs every 60 seconds by default
- Adjust with `--interval` flag if needed
- One-time syncs are instant

### 3. Privacy
- All data stored in your private Mem0 cloud
- No data leaves your control
- Can be self-hosted if preferred

### 4. Troubleshooting

#### Monitor Not Starting
```bash
# Check if API key is set
echo $MEM0_API_KEY

# Check Python path
which python3

# Run manually to see errors
python3 /path/to/activity_monitor.py --interval 30
```

#### No Memories Loading
```bash
# Test connection
python3 test_integration.py

# Check Mem0 service
curl -H "Authorization: Bearer $MEM0_API_KEY" https://api.mem0.ai/v1/memories/
```

## Architecture Benefits

### Why This Design?
1. **Passive Collection**: No manual logging required
2. **Universal Access**: Same context everywhere
3. **AI-Ready**: Instant context for AI assistants
4. **Git-Aware**: Tracks project state automatically
5. **Task-Centric**: Everything linked to Taskmaster tasks

### The Experience
- Open terminal → See what you were doing
- Ask AI assistant → It knows your context
- Switch projects → Context switches too
- Complete task → Achievement recorded forever

## Next Steps

1. **Enable Auto-Monitor**: Set `UTLYZE_AUTO_MONITOR=1`
2. **Configure Cursor**: Follow `docs/cursor-setup.md`
3. **Start Taskmaster Bridge**: For full integration
4. **Customize**: Add your own memory types and filters

Remember: The system is designed to be invisible. Just work normally, and your context follows you everywhere.
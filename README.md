# Utlyze Taskmaster-Mem0 Integration

A powerful development environment that integrates Taskmaster with Mem0 cloud memory to create a context-aware, self-synchronizing workspace across all terminals, Cursor IDE, and AI agents.

## Overview

This system automatically:
- Initializes mem0 cloud connection on every new terminal/Cursor window
- Passively collects project progress information
- Syncs context across all development environments
- Updates memory every time Taskmaster updates a task
- Provides instant context to AI agents about current work

## Features

- 🧠 **Persistent Memory**: Uses Mem0 cloud ($250/month unlimited plan) for centralized memory
- 📝 **Taskmaster Integration**: Every task update triggers memory synchronization
- 🚀 **Auto-initialization**: Shell scripts ensure memory loads on terminal start
- 🔄 **Passive Collection**: Background processes track development activity
- 🤖 **AI-Ready**: MCP server provides memory access to Cursor and other AI tools

## Quick Start

1. Set your Mem0 API key:
   ```bash
   export MEM0_API_KEY="your-mem0-cloud-api-key"
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add to your shell config (~/.bashrc or ~/.zshrc):
   ```bash
   source /path/to/utlyze-taskmaster-mem0/shell/init.sh
   ```

4. Start the MCP server:
   ```bash
   python src/mcp_server.py
   ```

5. Configure Cursor/VSCode to use the MCP server (see docs/cursor-setup.md)

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Terminal 1    │────▶│              │◀────│  Cursor IDE │
└─────────────────┘     │              │     └─────────────┘
                        │  Mem0 Cloud  │
┌─────────────────┐     │   (Central   │     ┌─────────────┐
│   Terminal 2    │────▶│   Memory)    │◀────│  AI Agents  │
└─────────────────┘     │              │     └─────────────┘
                        └──────────────┘
                               ▲
                               │
                        ┌──────────────┐
                        │  Taskmaster  │
                        │   Updates    │
                        └──────────────┘
```

## Project Structure

```
utlyze-taskmaster-mem0/
├── src/
│   ├── taskmaster_bridge.py    # Taskmaster webhook handler
│   ├── mcp_server.py           # MCP server for Cursor/VSCode
│   ├── mem0_client.py          # Mem0 cloud integration
│   └── activity_monitor.py     # Passive activity collection
├── shell/
│   ├── init.sh                 # Shell initialization script
│   └── functions.sh            # Utility functions
├── config/
│   └── settings.json           # Configuration
├── docs/
│   ├── cursor-setup.md         # Cursor IDE setup guide
│   └── architecture.md         # Detailed architecture
└── tests/
    └── test_integration.py     # Integration tests
```

## License

MIT
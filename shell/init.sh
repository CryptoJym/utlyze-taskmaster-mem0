#!/bin/bash
# Utlyze Taskmaster-Mem0 Shell Initialization Script
# Source this file in your ~/.bashrc or ~/.zshrc

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if MEM0_API_KEY is set
if [ -z "$MEM0_API_KEY" ]; then
    echo -e "${RED}Warning: MEM0_API_KEY not set${NC}"
    echo "Please set it with: export MEM0_API_KEY='your-api-key'"
else
    # Get the directory where this script is located
    UTLYZE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
    
    # Initialize Mem0 connection and load context on shell start
    if command -v python3 &> /dev/null; then
        # Run initialization in background to not slow down shell startup
        (
            python3 -c "
import sys
sys.path.append('$UTLYZE_DIR/src')
from mem0_client import UtlyzeMem0Client
import os

try:
    client = UtlyzeMem0Client()
    context = client.get_current_context(limit=5)
    if context:
        print('\n🧠 Utlyze Memory Loaded:')
        for i, memory in enumerate(context[:3]):
            content = memory['content'].strip().replace('\n', ' ')[:80]
            print(f'  {i+1}. {content}...')
        if len(context) > 3:
            print(f'  ... and {len(context)-3} more memories')
    
    # Log that we've started a new session
    client.add_terminal_activity({
        'cwd': os.getcwd(),
        'git_branch': os.popen('git branch --show-current 2>/dev/null').read().strip() or 'no-git',
        'last_command': 'shell_init'
    })
except Exception as e:
    print(f'⚠️  Mem0 initialization failed: {str(e)}')
" 2>/dev/null &
        ) &
    fi
fi

# Function to manually sync with Taskmaster
utlyze_sync() {
    echo -e "${BLUE}🔄 Syncing with Taskmaster...${NC}"
    if [ -z "$MEM0_API_KEY" ]; then
        echo -e "${RED}Error: MEM0_API_KEY not set${NC}"
        return 1
    fi
    
    # Add your Taskmaster sync logic here
    echo -e "${GREEN}✓ Sync complete${NC}"
}

# Function to show current context
utlyze_context() {
    if [ -z "$MEM0_API_KEY" ]; then
        echo -e "${RED}Error: MEM0_API_KEY not set${NC}"
        return 1
    fi
    
    python3 -c "
import sys
sys.path.append('$UTLYZE_DIR/src')
from mem0_client import UtlyzeMem0Client

client = UtlyzeMem0Client()
context = client.get_current_context(limit=10)

print('\n🧠 Current Utlyze Context:')
print('=' * 50)
for i, memory in enumerate(context):
    print(f'\n{i+1}. {memory[\"content\"].strip()}')
    if memory.get('metadata'):
        print(f'   Type: {memory[\"metadata\"].get(\"type\", \"unknown\")}')
        print(f'   Time: {memory[\"metadata\"].get(\"timestamp\", \"unknown\")}')
"
}

# Function to log current activity (called automatically)
_utlyze_log_activity() {
    if [ -z "$MEM0_API_KEY" ] || [ -z "$UTLYZE_ACTIVITY_LOGGING" ]; then
        return
    fi
    
    # Don't log if we're in a git directory that's not Utlyze-related
    if [[ ! "$PWD" =~ "utlyze" ]] && [ -d .git ]; then
        return
    fi
    
    # Log activity in background
    (
        python3 -c "
import sys
import os
sys.path.append('$UTLYZE_DIR/src')
from mem0_client import UtlyzeMem0Client

client = UtlyzeMem0Client()
client.add_terminal_activity({
    'cwd': os.getcwd(),
    'git_branch': os.popen('git branch --show-current 2>/dev/null').read().strip() or 'no-git',
    'last_command': '$1'
})
" 2>/dev/null
    ) &
}

# Enable activity logging (disabled by default to avoid noise)
# Uncomment the next line to enable passive activity logging
# export UTLYZE_ACTIVITY_LOGGING=1

# Hook into the prompt command to log activity (bash)
if [ -n "$BASH_VERSION" ]; then
    # Store the original PROMPT_COMMAND
    _ORIGINAL_PROMPT_COMMAND="$PROMPT_COMMAND"
    
    PROMPT_COMMAND='
    _utlyze_log_activity "$_"
    '$_ORIGINAL_PROMPT_COMMAND
fi

# For zsh users
if [ -n "$ZSH_VERSION" ]; then
    # Add to precmd hook
    precmd_functions+=(_utlyze_log_activity)
fi

# Aliases for quick access
alias utx="utlyze_context"
alias uts="utlyze_sync"

# Export the Utlyze directory for other scripts
export UTLYZE_MEM0_DIR="$UTLYZE_DIR"

# Function to start activity monitor
utlyze_monitor() {
    if [ -z "$MEM0_API_KEY" ]; then
        echo -e "${RED}Error: MEM0_API_KEY not set${NC}"
        return 1
    fi
    
    local cmd="${1:-start}"
    
    case "$cmd" in
        start)
            echo -e "${BLUE}Starting activity monitor...${NC}"
            python3 "$UTLYZE_DIR/src/activity_monitor.py" --daemon
            ;;
        stop)
            echo -e "${YELLOW}Stopping activity monitor...${NC}"
            pkill -f "activity_monitor.py"
            ;;
        status)
            if pgrep -f "activity_monitor.py" > /dev/null; then
                echo -e "${GREEN}Activity monitor is running${NC}"
            else
                echo -e "${YELLOW}Activity monitor is not running${NC}"
            fi
            ;;
        once)
            echo -e "${BLUE}Running one-time activity sync...${NC}"
            python3 "$UTLYZE_DIR/src/activity_monitor.py" --once
            ;;
        *)
            echo "Usage: utlyze_monitor [start|stop|status|once]"
            ;;
    esac
}

# Auto-start activity monitor on shell init (if enabled)
if [ -n "$UTLYZE_AUTO_MONITOR" ]; then
    # Check if monitor is already running
    if ! pgrep -f "activity_monitor.py" > /dev/null; then
        utlyze_monitor start 2>/dev/null
    fi
fi

# Show initialization message (only if interactive shell)
if [[ $- == *i* ]]; then
    echo -e "${GREEN}✓ Utlyze Mem0 Integration Active${NC}"
    echo -e "  Commands: ${BLUE}utx${NC} (show context), ${BLUE}uts${NC} (sync), ${BLUE}utlyze_monitor${NC} (activity monitor)"
fi
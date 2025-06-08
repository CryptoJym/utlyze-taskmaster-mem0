#!/bin/bash
# Start Utlyze Taskmaster-Mem0 Services

echo "🚀 Starting Utlyze Taskmaster-Mem0 Services..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if MEM0_API_KEY is set
if [ -z "$MEM0_API_KEY" ]; then
    export MEM0_API_KEY='m0-HKjU23jTDZyUmsZqQBsIPW1AdcgwC4vkWT7O4dLt'
fi

# Check if Taskmaster bridge is already running
if pgrep -f "taskmaster_bridge.py" > /dev/null; then
    echo "✅ Taskmaster bridge already running"
else
    echo "Starting Taskmaster bridge on port 8081..."
    cd "$SCRIPT_DIR"
    source venv/bin/activate
    export TASKMASTER_BRIDGE_PORT=8081
    nohup python src/taskmaster_bridge.py > logs/taskmaster_bridge.log 2>&1 &
    echo "✅ Taskmaster bridge started (PID: $!)"
fi

echo ""
echo "Services Status:"
echo "- Taskmaster Bridge: http://localhost:8081"
echo "- Logs: $SCRIPT_DIR/logs/taskmaster_bridge.log"
echo ""
echo "Shell commands available:"
echo "- utx: Show current context"
echo "- uts: Sync with Taskmaster"
echo ""
echo "To stop services: pkill -f taskmaster_bridge.py"
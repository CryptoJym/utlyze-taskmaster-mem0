#!/bin/bash
# Utlyze Taskmaster-Mem0 Quick Start Script

echo "🚀 Utlyze Taskmaster-Mem0 Integration Quick Start"
echo "================================================"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

# Check for MEM0_API_KEY
if [ -z "$MEM0_API_KEY" ]; then
    echo "⚠️  MEM0_API_KEY not found in environment"
    echo ""
    echo "Please set your Mem0 Cloud API key:"
    echo "  export MEM0_API_KEY='your-api-key'"
    echo ""
    read -p "Enter your MEM0_API_KEY: " api_key
    export MEM0_API_KEY="$api_key"
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Test Mem0 connection
echo ""
echo "🧪 Testing Mem0 connection..."
python3 -c "
from src.mem0_client import UtlyzeMem0Client
try:
    client = UtlyzeMem0Client()
    print('✅ Mem0 connection successful!')
except Exception as e:
    print(f'❌ Mem0 connection failed: {e}')
    exit(1)
"

# Add shell integration
echo ""
echo "🐚 Setting up shell integration..."
SHELL_RC=""
if [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

if [ -n "$SHELL_RC" ]; then
    echo ""
    echo "Add this line to your $SHELL_RC:"
    echo "  source $PWD/shell/init.sh"
    echo ""
    read -p "Add automatically? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "" >> "$SHELL_RC"
        echo "# Utlyze Taskmaster-Mem0 Integration" >> "$SHELL_RC"
        echo "export MEM0_API_KEY='$MEM0_API_KEY'" >> "$SHELL_RC"
        echo "source $PWD/shell/init.sh" >> "$SHELL_RC"
        echo "✅ Added to $SHELL_RC"
    fi
fi

# Start services
echo ""
echo "🎯 Starting services..."
echo ""
echo "1. Start Taskmaster Bridge (in a new terminal):"
echo "   python src/taskmaster_bridge.py"
echo ""
echo "2. For Cursor integration, add to settings:"
echo "   See docs/cursor-setup.md"
echo ""
echo "✅ Setup complete!"
echo ""
echo "Available commands:"
echo "  utx - Show current context"
echo "  uts - Sync with Taskmaster"
echo ""
echo "Restart your shell or run: source $SHELL_RC"
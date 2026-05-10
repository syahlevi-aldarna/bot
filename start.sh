#!/bin/bash

# Autonomous Coding Agent - Startup Script
# Starts all required services and the bot

set -e

echo "🚀 Starting Autonomous Coding Agent..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm found${NC}"

echo ""

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p .claude-flow/logs
mkdir -p .backups
echo -e "${GREEN}✓ Directories created${NC}"

echo ""

# Check .env file
echo -e "${YELLOW}Checking configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please create .env file with:"
    echo "  TELEGRAM_BOT_TOKEN=your_token_here"
    echo "  MCP_SERVER_PORT=3000"
    exit 1
fi
echo -e "${GREEN}✓ .env file found${NC}"

echo ""

# Install dependencies if needed
echo -e "${YELLOW}Checking dependencies...${NC}"

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi
echo -e "${GREEN}✓ Node dependencies ready${NC}"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
echo -e "${GREEN}✓ Python dependencies ready${NC}"

echo ""

# Start MCP server in background
echo -e "${YELLOW}Starting MCP server...${NC}"
npx ruflo@latest mcp start &
MCP_PID=$!
echo -e "${GREEN}✓ MCP server started (PID: $MCP_PID)${NC}"

# Wait for MCP server to start
sleep 2

# Check if MCP server is running
if ! kill -0 $MCP_PID 2>/dev/null; then
    echo -e "${RED}❌ MCP server failed to start${NC}"
    exit 1
fi

echo ""

# Start the bot
echo -e "${YELLOW}Starting Telegram bot...${NC}"
python3 tele_bot.py

# Cleanup on exit
trap "kill $MCP_PID 2>/dev/null" EXIT

echo ""
echo -e "${GREEN}✓ Autonomous Coding Agent started successfully!${NC}"
echo ""
echo "📝 Logs available in: .claude-flow/logs/"
echo "💾 Backups available in: .backups/"
echo ""
echo "Send a message to your Telegram bot to start!"

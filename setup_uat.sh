#!/bin/bash

# RUFLO Quick Setup Script for UAT
# This script helps you setup RUFLO for User Acceptance Testing

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Main setup
main() {
    print_header "🤖 RUFLO Quick Setup for UAT"
    
    # Step 1: Check if .env exists
    print_step "Checking .env file..."
    if [ -f ".env" ]; then
        print_info ".env file already exists"
        read -p "Do you want to reconfigure? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Skipping .env configuration"
            goto_next_step=1
        fi
    fi
    
    # Step 2: Get Telegram Bot Token
    if [ "$goto_next_step" != "1" ]; then
        print_step "Getting Telegram Bot Token..."
        print_info "Instructions:"
        print_info "1. Open Telegram and search for @BotFather"
        print_info "2. Send /newbot command"
        print_info "3. Follow instructions to create a bot"
        print_info "4. Copy the token (looks like: 123456:ABC-DEF...)"
        echo
        read -p "Enter your Telegram Bot Token: " BOT_TOKEN
        
        if [ -z "$BOT_TOKEN" ]; then
            print_error "Bot token cannot be empty"
            exit 1
        fi
        print_success "Bot token saved"
    fi
    
    # Step 3: Get Chat ID
    if [ "$goto_next_step" != "1" ]; then
        print_step "Getting your Telegram Chat ID..."
        print_info "Instructions:"
        print_info "1. Send any message to your bot"
        print_info "2. Run this command:"
        print_info "   curl \"https://api.telegram.org/bot$BOT_TOKEN/getUpdates\" | grep -o '\"chat\":{\"id\":[0-9]*' | grep -o '[0-9]*'"
        echo
        read -p "Enter your Chat ID: " CHAT_ID
        
        if [ -z "$CHAT_ID" ]; then
            print_error "Chat ID cannot be empty"
            exit 1
        fi
        print_success "Chat ID saved"
    fi
    
    # Step 4: Create .env file
    if [ "$goto_next_step" != "1" ]; then
        print_step "Creating .env file..."
        cat > .env << EOF
# RUFLO Configuration
TELEGRAM_BOT_TOKEN=$BOT_TOKEN
TELEGRAM_CHAT_ID=$CHAT_ID
MCP_SERVER_PORT=3000
LOG_LEVEL=INFO
AGENT_TIMEOUT=300
MAX_RETRIES=3
MEMORY_TOP_K=5
EOF
        print_success ".env file created"
    fi
    
    # Step 5: Install dependencies
    print_step "Installing dependencies..."
    if [ ! -d "node_modules" ]; then
        print_info "Installing Node.js dependencies..."
        npm install > /dev/null 2>&1
        print_success "Node.js dependencies installed"
    else
        print_info "Node.js dependencies already installed"
    fi
    
    # Step 6: Create directories
    print_step "Creating required directories..."
    mkdir -p .claude-flow/logs
    mkdir -p .backups
    print_success "Directories created"
    
    # Step 7: Run UAT
    print_header "🧪 Running User Acceptance Test"
    print_info "This will verify your system is ready for testing..."
    echo
    
    if bash run_uat.sh; then
        print_header "✅ Setup Complete!"
        print_info "Your system is ready for UAT. Next steps:"
        echo
        print_info "Terminal 1 - Start MCP Server:"
        echo -e "  ${YELLOW}npx ruflo@latest mcp start${NC}"
        echo
        print_info "Terminal 2 - Start Telegram Bot:"
        echo -e "  ${YELLOW}python3 tele_bot.py${NC}"
        echo
        print_info "Terminal 3 - Send task to Telegram:"
        echo -e "  ${YELLOW}Open Telegram and send: 'Create a function that validates email addresses'${NC}"
        echo
        print_info "Terminal 3 - Monitor logs:"
        echo -e "  ${YELLOW}tail -f .claude-flow/logs/agent_*.log${NC}"
        echo
    else
        print_error "Setup failed. Please check the errors above."
        exit 1
    fi
}

# Run main
main

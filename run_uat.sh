#!/bin/bash

# RUFLO User Acceptance Test (UAT) Script
# This script automates the UAT process from setup to verification

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
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
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Phase 1: Prerequisites Check
phase_1_prerequisites() {
    print_header "PHASE 1: Prerequisites Check"
    
    print_step "Checking Python version..."
    if python3 --version &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        print_success "Python $PYTHON_VERSION installed"
    else
        print_error "Python 3 not found"
        return 1
    fi
    
    print_step "Checking Node.js version..."
    if node --version &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION installed"
    else
        print_error "Node.js not found"
        return 1
    fi
    
    print_step "Checking npm..."
    if npm --version &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION installed"
    else
        print_error "npm not found"
        return 1
    fi
    
    print_step "Checking git..."
    if git --version &> /dev/null; then
        print_success "git installed"
    else
        print_error "git not found"
        return 1
    fi
    
    print_step "Checking .env file..."
    if [ -f .env ]; then
        print_success ".env file exists"
        
        if grep -q "TELEGRAM_BOT_TOKEN" .env; then
            print_success "TELEGRAM_BOT_TOKEN configured"
        else
            print_error "TELEGRAM_BOT_TOKEN not found in .env"
            return 1
        fi
        
        if grep -q "TELEGRAM_CHAT_ID" .env; then
            print_success "TELEGRAM_CHAT_ID configured"
        else
            print_error "TELEGRAM_CHAT_ID not found in .env"
            return 1
        fi
    else
        print_error ".env file not found"
        print_info "Please create .env file with TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
        return 1
    fi
}

# Phase 2: Dependencies Check
phase_2_dependencies() {
    print_header "PHASE 2: Dependencies Check"
    
    print_step "Checking Python dependencies..."
    if python3 -c "import pytest" 2>/dev/null; then
        print_success "pytest installed"
    else
        print_error "pytest not installed"
        return 1
    fi
    
    print_step "Checking Node.js dependencies..."
    if [ -d "node_modules" ]; then
        print_success "node_modules directory exists"
    else
        print_error "node_modules not found"
        print_info "Run: npm install"
        return 1
    fi
    
    print_step "Checking source files..."
    if [ -f "src/mcp_client.py" ]; then
        print_success "src/mcp_client.py exists"
    else
        print_error "src/mcp_client.py not found"
        return 1
    fi
    
    if [ -f "tele_bot.py" ]; then
        print_success "tele_bot.py exists"
    else
        print_error "tele_bot.py not found"
        return 1
    fi
}

# Phase 3: Directory Structure
phase_3_directories() {
    print_header "PHASE 3: Directory Structure Check"
    
    print_step "Checking required directories..."
    
    DIRS=("src" "tests" ".claude-flow" ".backups")
    for dir in "${DIRS[@]}"; do
        if [ -d "$dir" ]; then
            print_success "$dir directory exists"
        else
            print_error "$dir directory not found"
            mkdir -p "$dir"
            print_info "Created $dir directory"
        fi
    done
    
    print_step "Checking log directory..."
    if [ -d ".claude-flow/logs" ]; then
        print_success ".claude-flow/logs directory exists"
    else
        mkdir -p ".claude-flow/logs"
        print_success "Created .claude-flow/logs directory"
    fi
}

# Phase 4: Run Unit Tests
phase_4_unit_tests() {
    print_header "PHASE 4: Unit Tests"
    
    print_step "Running JavaScript tests..."
    if npm test 2>&1 | grep -q "Tests:.*passed"; then
        JS_TESTS=$(npm test 2>&1 | grep "Tests:" | awk '{print $2}')
        print_success "JavaScript tests: $JS_TESTS"
    else
        print_error "JavaScript tests failed"
        return 1
    fi
    
    print_step "Running Python tests..."
    if python3 -m pytest tests/ -q 2>&1 | grep -q "passed"; then
        PY_TESTS=$(python3 -m pytest tests/ -q 2>&1 | tail -1)
        print_success "Python tests: $PY_TESTS"
    else
        print_error "Python tests failed"
        return 1
    fi
}

# Phase 5: System Health Check
phase_5_health_check() {
    print_header "PHASE 5: System Health Check"
    
    print_step "Checking MCP server port..."
    if ! lsof -i :3000 &> /dev/null; then
        print_info "Port 3000 is available"
    else
        print_error "Port 3000 is already in use"
        print_info "Kill existing process: lsof -i :3000 | grep LISTEN | awk '{print \$2}' | xargs kill -9"
        return 1
    fi
    
    print_step "Checking file permissions..."
    if [ -w ".backups" ]; then
        print_success ".backups directory is writable"
    else
        print_error ".backups directory is not writable"
        chmod 755 .backups
        print_info "Fixed permissions"
    fi
    
    if [ -w ".claude-flow/logs" ]; then
        print_success ".claude-flow/logs directory is writable"
    else
        print_error ".claude-flow/logs directory is not writable"
        chmod 755 .claude-flow/logs
        print_info "Fixed permissions"
    fi
}

# Phase 6: Configuration Validation
phase_6_config_validation() {
    print_header "PHASE 6: Configuration Validation"
    
    print_step "Validating .env file..."
    
    BOT_TOKEN=$(grep "TELEGRAM_BOT_TOKEN" .env | cut -d'=' -f2)
    CHAT_ID=$(grep "TELEGRAM_CHAT_ID" .env | cut -d'=' -f2)
    
    if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_bot_token_here" ]; then
        print_error "TELEGRAM_BOT_TOKEN not properly configured"
        return 1
    else
        print_success "TELEGRAM_BOT_TOKEN configured"
    fi
    
    if [ -z "$CHAT_ID" ] || [ "$CHAT_ID" = "your_chat_id_here" ]; then
        print_error "TELEGRAM_CHAT_ID not properly configured"
        return 1
    else
        print_success "TELEGRAM_CHAT_ID configured"
    fi
    
    print_step "Validating source code..."
    if python3 -m py_compile src/mcp_client.py 2>/dev/null; then
        print_success "src/mcp_client.py syntax valid"
    else
        print_error "src/mcp_client.py has syntax errors"
        return 1
    fi
    
    if python3 -m py_compile tele_bot.py 2>/dev/null; then
        print_success "tele_bot.py syntax valid"
    else
        print_error "tele_bot.py has syntax errors"
        return 1
    fi
}

# Phase 7: Documentation Check
phase_7_documentation() {
    print_header "PHASE 7: Documentation Check"
    
    DOCS=("README.md" "USER_GUIDE.md" "ARCHITECTURE.md" "TROUBLESHOOTING.md" "PRODUCT_DISCOVERY.md" "PRODUCT_POSITIONING.md")
    
    for doc in "${DOCS[@]}"; do
        if [ -f "$doc" ]; then
            SIZE=$(wc -c < "$doc")
            print_success "$doc exists ($(($SIZE / 1024))KB)"
        else
            print_error "$doc not found"
        fi
    done
}

# Phase 8: Git Status
phase_8_git_status() {
    print_header "PHASE 8: Git Status"
    
    print_step "Checking git repository..."
    if git rev-parse --git-dir > /dev/null 2>&1; then
        print_success "Git repository initialized"
    else
        print_error "Not a git repository"
        return 1
    fi
    
    print_step "Checking git status..."
    if [ -z "$(git status --porcelain)" ]; then
        print_success "Working directory clean"
    else
        print_info "Uncommitted changes detected"
        git status --short | head -5
    fi
    
    print_step "Checking recent commits..."
    LAST_COMMIT=$(git log -1 --pretty=format:"%h - %s")
    print_info "Last commit: $LAST_COMMIT"
}

# Main execution
main() {
    print_header "🤖 RUFLO User Acceptance Test (UAT)"
    print_info "Starting comprehensive system validation..."
    
    # Run all phases
    phase_1_prerequisites || { print_error "Prerequisites check failed"; exit 1; }
    phase_2_dependencies || { print_error "Dependencies check failed"; exit 1; }
    phase_3_directories || { print_error "Directory check failed"; exit 1; }
    phase_4_unit_tests || { print_error "Unit tests failed"; exit 1; }
    phase_5_health_check || { print_error "Health check failed"; exit 1; }
    phase_6_config_validation || { print_error "Configuration validation failed"; exit 1; }
    phase_7_documentation || { print_error "Documentation check failed"; exit 1; }
    phase_8_git_status || { print_error "Git status check failed"; exit 1; }
    
    # Final summary
    print_header "📊 UAT Summary"
    
    TOTAL=$((TESTS_PASSED + TESTS_FAILED))
    SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL))
    
    echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
    echo -e "Total Tests: $TOTAL"
    echo -e "Success Rate: ${GREEN}$SUCCESS_RATE%${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        print_header "✅ UAT PASSED - System Ready for User Testing"
        print_info "Next steps:"
        print_info "1. Start MCP server: npx ruflo@latest mcp start"
        print_info "2. Start Telegram bot: python3 tele_bot.py"
        print_info "3. Send task to Telegram bot"
        print_info "4. Monitor logs: tail -f .claude-flow/logs/agent_*.log"
        exit 0
    else
        print_header "❌ UAT FAILED - Please fix issues above"
        exit 1
    fi
}

# Run main function
main

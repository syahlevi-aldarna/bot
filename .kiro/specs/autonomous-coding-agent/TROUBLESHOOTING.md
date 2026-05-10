# Troubleshooting Guide: Autonomous Coding Agent

## Quick Diagnostics

### Check System Status
```bash
# Check if Ruflo MCP server is running
curl http://localhost:3000/health

# Check if Telegram bot is running
ps aux | grep tele_bot.py

# Check logs for errors
tail -f .claude-flow/logs/agent-*.log
tail -f .claude-flow/logs/task-*.log
```

### Check Configuration
```bash
# Verify .env is set correctly
cat .env | grep -E "OPENROUTER_API_KEY|TELEGRAM_TOKEN|OWNER_ID|RUFLO"

# Verify Ruflo config exists
cat .claude-flow/config.yaml
```

---

## Common Issues & Solutions

### Issue 1: Ruflo MCP Server Won't Start

**Symptoms:**
- `Error: Cannot find module 'ruflo'`
- `Port 3000 already in use`
- `Connection refused` when bot tries to connect

**Root Causes & Solutions:**

**Cause 1a: Ruflo not installed**
```bash
# Solution: Install Ruflo
npm install -g ruflo@latest

# Verify installation
npx ruflo --version
```

**Cause 1b: Port 3000 already in use**
```bash
# Solution: Find and kill process using port 3000
lsof -i :3000
kill -9 <PID>

# Or use different port
npx ruflo@latest mcp start --port 3001
# Update RUFLO_MCP_PORT in .env to 3001
```

**Cause 1c: Node.js version too old**
```bash
# Solution: Update Node.js to 18+
node --version
# If < 18, update via nvm or system package manager
nvm install 18
nvm use 18
```

**Cause 1d: Missing dependencies**
```bash
# Solution: Reinstall dependencies
npm install
npm install -g ruflo@latest
```

---

### Issue 2: Telegram Bot Not Responding

**Symptoms:**
- Bot receives message but doesn't respond
- "Agent starting..." message appears but nothing after
- Timeout after 60 seconds

**Root Causes & Solutions:**

**Cause 2a: TELEGRAM_TOKEN invalid**
```bash
# Solution: Verify token
# 1. Get new token from @BotFather on Telegram
# 2. Update .env
TELEGRAM_TOKEN=<new_token>

# 3. Restart bot
pkill -f tele_bot.py
python tele_bot.py
```

**Cause 2b: OWNER_ID not set or wrong**
```bash
# Solution: Get your Telegram user ID
# 1. Send /start to @userinfobot
# 2. Copy your ID
# 3. Update .env
OWNER_ID=<your_id>

# 4. Restart bot
pkill -f tele_bot.py
python tele_bot.py
```

**Cause 2c: MCP server not running**
```bash
# Solution: Start MCP server
npx ruflo@latest mcp start --port 3000

# Verify it's running
curl http://localhost:3000/health
```

**Cause 2d: Network connectivity issue**
```bash
# Solution: Check network
ping 8.8.8.8
curl https://api.telegram.org/bot<TOKEN>/getMe

# If Telegram API unreachable, check firewall/proxy
```

**Cause 2e: Agent timeout (task takes >60 seconds)**
```bash
# Solution: Check agent logs
tail -f .claude-flow/logs/agent-*.log

# If agent is slow:
# 1. Check system resources (CPU, memory)
# 2. Simplify task (break into smaller tasks)
# 3. Increase timeout in .env
RUFLO_AGENT_TIMEOUT=600  # 10 minutes instead of 5
```

---

### Issue 3: Agent Fails to Read/Write Files

**Symptoms:**
- "Permission denied" error
- "File not found" for existing files
- "Path validation failed"

**Root Causes & Solutions:**

**Cause 3a: File path outside project directory**
```bash
# Solution: Check file path validation
# Allowed: src/, tests/, config/, .claude-flow/
# Not allowed: /etc/, /home/, ../../../etc/

# Example error in logs:
# "Path validation failed: /etc/passwd is outside project"

# Fix: Use relative paths only
# ✓ src/utils.js
# ✗ /home/user/project/src/utils.js
```

**Cause 3b: File permissions issue**
```bash
# Solution: Check file permissions
ls -la src/utils.js

# If not readable/writable:
chmod 644 src/utils.js  # readable
chmod 755 src/          # directory readable/executable

# Or fix ownership
chown $USER:$USER src/utils.js
```

**Cause 3c: .env file being read**
```bash
# Solution: .env is protected from reads
# This is intentional for security

# If agent needs env vars:
# 1. Pass them explicitly in task
# 2. Or create a separate config file (not .env)
```

**Cause 3d: Backup directory doesn't exist**
```bash
# Solution: Create backup directory
mkdir -p .claude-flow/backups

# Verify permissions
chmod 755 .claude-flow/backups
```

---

### Issue 4: Bash Command Execution Fails

**Symptoms:**
- "Command not whitelisted" error
- "Command injection detected"
- Command runs but produces wrong output

**Root Causes & Solutions:**

**Cause 4a: Command not in whitelist**
```bash
# Whitelisted commands:
# npm, yarn, python, git, node, cat, ls, mkdir, cp, mv, grep, find, echo, test

# Solution: Use whitelisted commands only
# ✓ npm test
# ✗ rm -rf node_modules  (rm not whitelisted)
# ✗ sudo npm install     (sudo not whitelisted)

# If you need a command, add it to whitelist in code execution layer
```

**Cause 4b: Command injection attempt detected**
```bash
# Solution: Don't use pipes or command substitution
# ✓ npm test
# ✗ npm test | grep error  (pipe not allowed)
# ✗ npm test && npm build  (command chaining not allowed)

# If you need complex commands:
# 1. Create a shell script
# 2. Add script to whitelist
# 3. Call script from agent
```

**Cause 4c: Command timeout**
```bash
# Solution: Check command execution time
# Default timeout: 30 seconds per command

# If command takes longer:
# 1. Optimize the command
# 2. Break into smaller commands
# 3. Increase timeout in code execution layer
```

**Cause 4d: Command produces no output**
```bash
# Solution: Check if command is actually running
# Add logging to agent prompt:
# "Run: npm test && echo 'Test completed'"

# Or check logs:
tail -f .claude-flow/logs/task-*.log
```

---

### Issue 5: Agent Coordination Fails (SendMessage)

**Symptoms:**
- Coder agent completes but reviewer doesn't start
- "SendMessage failed" error
- Agents run in parallel instead of sequence

**Root Causes & Solutions:**

**Cause 5a: Agent names don't match**
```bash
# Solution: Verify agent names match exactly
# Coder sends to: "reviewer"
# Reviewer sends to: "tester"

# Check in agent templates:
# Agent({ name: "coder", ... })
# Agent({ name: "reviewer", ... })
# Agent({ name: "tester", ... })

# If names don't match, SendMessage fails silently
```

**Cause 5b: Agents not running in background**
```bash
# Solution: Ensure run_in_background: true
# Agent({
#   name: "coder",
#   run_in_background: true,  // MUST be true
#   ...
# })
```

**Cause 5c: Message format incorrect**
```bash
# Solution: Check SendMessage format
# Correct:
# SendMessage("reviewer", {
#   code: "...",
#   changes: "..."
# })

# Incorrect:
# SendMessage("reviewer", "code here")  // Must be object
```

**Cause 5d: Swarm not initialized**
```bash
# Solution: Initialize swarm before spawning agents
# In Ruflo config:
# swarm:
#   topology: hierarchical-mesh
#   maxAgents: 15
#   coordinationStrategy: consensus

# Or call swarm_init tool before agent_spawn
```

---

### Issue 6: Memory Not Working (HNSW Search)

**Symptoms:**
- "Memory search returned no results"
- "AgentDB not found"
- Agent doesn't learn from past tasks

**Root Causes & Solutions:**

**Cause 6a: Memory directory doesn't exist**
```bash
# Solution: Create memory directories
mkdir -p .claude-flow/data/agentdb
mkdir -p .claude-flow/data/memory-graph
mkdir -p .claude-flow/data/patterns

# Verify permissions
chmod 755 .claude-flow/data/*
```

**Cause 6b: No tasks stored yet**
```bash
# Solution: Memory is empty on first run
# 1. Complete a task successfully
# 2. Task is stored in AgentDB
# 3. Future similar tasks will find it

# Check stored tasks:
ls -la .claude-flow/data/agentdb/
```

**Cause 6c: HNSW index corrupted**
```bash
# Solution: Rebuild index
# 1. Delete corrupted index
rm -rf .claude-flow/data/agentdb/hnsw.index

# 2. Restart agent (will rebuild on next task)
pkill -f tele_bot.py
python tele_bot.py
```

**Cause 6d: Embedding model not available**
```bash
# Solution: Verify embedding model
# Check in logs:
tail -f .claude-flow/logs/agent-*.log | grep embedding

# If model not found:
# 1. Check OPENROUTER_API_KEY is set
# 2. Verify API key is valid
# 3. Check internet connectivity
```

---

### Issue 7: Security Violations (AIDefence)

**Symptoms:**
- "Security violation: prompt injection detected"
- "Code contains malicious pattern"
- Operation blocked unexpectedly

**Root Causes & Solutions:**

**Cause 7a: Prompt injection in task**
```bash
# Solution: Don't include user input directly in prompts
# ✗ Agent({ prompt: `Task: ${user_input}` })
# ✓ Agent({ prompt: `Task: [SANITIZED]`, context: sanitize(user_input) })

# AIDefence scans for:
# - SQL injection patterns
# - Command injection patterns
# - Path traversal patterns
# - Prompt injection patterns
```

**Cause 7b: Suspicious code pattern**
```bash
# Solution: Review code for suspicious patterns
# Flagged patterns:
# - eval(), exec(), __import__()
# - os.system(), subprocess.call()
# - open('/etc/passwd')
# - import os; os.remove()

# If legitimate, add to AIDefence whitelist
```

**Cause 7c: Secrets in code**
```bash
# Solution: Never commit secrets
# Flagged patterns:
# - OPENROUTER_API_KEY=sk-...
# - password: "..."
# - token: "..."

# Use .env instead:
# .env (not committed)
# .env.example (committed, with placeholders)
```

---

### Issue 8: Agent Timeout

**Symptoms:**
- "Agent timeout after 5 minutes"
- Task killed unexpectedly
- "Agent did not respond"

**Root Causes & Solutions:**

**Cause 8a: Task too complex**
```bash
# Solution: Break task into smaller tasks
# Instead of: "Build entire authentication system"
# Use: 
# 1. "Create login endpoint"
# 2. "Create JWT validation"
# 3. "Create password hashing"

# Each task should complete in <5 minutes
```

**Cause 8b: Agent stuck in loop**
```bash
# Solution: Check agent logs for infinite loops
tail -f .claude-flow/logs/agent-*.log

# Look for repeated messages
# If found, fix agent prompt to avoid loop
```

**Cause 8c: System resources exhausted**
```bash
# Solution: Check system resources
top
free -h
df -h

# If low on resources:
# 1. Kill other processes
# 2. Increase swap space
# 3. Reduce max concurrent agents
RUFLO_MAX_AGENTS=5  # Instead of 15
```

**Cause 8d: Network latency**
```bash
# Solution: Check network latency
ping 8.8.8.8
curl -w "@curl-format.txt" https://api.openrouter.io/

# If high latency:
# 1. Check internet connection
# 2. Try different network
# 3. Increase timeout
RUFLO_AGENT_TIMEOUT=600  # 10 minutes
```

---

### Issue 9: Logs Not Being Written

**Symptoms:**
- `.claude-flow/logs/` directory empty
- No agent logs appearing
- Can't debug issues

**Root Causes & Solutions:**

**Cause 9a: Log directory doesn't exist**
```bash
# Solution: Create log directory
mkdir -p .claude-flow/logs

# Verify permissions
chmod 755 .claude-flow/logs
```

**Cause 9b: Logging not enabled**
```bash
# Solution: Check Ruflo config
cat .claude-flow/config.yaml | grep -A5 logging

# Should have:
# logging:
#   enabled: true
#   level: debug
#   path: .claude-flow/logs/
```

**Cause 9c: Disk space full**
```bash
# Solution: Check disk space
df -h

# If full:
# 1. Delete old logs
rm .claude-flow/logs/agent-*.log.old

# 2. Compress old logs
gzip .claude-flow/logs/agent-*.log

# 3. Increase disk space
```

**Cause 9d: Log rotation not working**
```bash
# Solution: Manually rotate logs
# If logs get too large (>1GB):
mv .claude-flow/logs/agent-current.log .claude-flow/logs/agent-$(date +%Y%m%d).log

# Restart agent to create new log
pkill -f tele_bot.py
python tele_bot.py
```

---

### Issue 10: Secrets Appearing in Logs/Telegram

**Symptoms:**
- API keys visible in logs
- Passwords in Telegram messages
- Security breach risk

**Root Causes & Solutions:**

**Cause 10a: .env file being logged**
```bash
# Solution: .env is protected from logging
# But verify in code:
# ✗ logger.info(f"Config: {os.environ}")
# ✓ logger.info("Config loaded successfully")

# Check logs for secrets:
grep -r "OPENROUTER_API_KEY" .claude-flow/logs/
grep -r "TELEGRAM_TOKEN" .claude-flow/logs/

# If found, delete logs and fix code
```

**Cause 10b: Secrets in agent output**
```bash
# Solution: Sanitize agent output before sending to Telegram
# In tele_bot.py:
# output = sanitize_secrets(agent_output)
# await update.message.reply_text(output)

# Sanitization should remove:
# - API keys (sk-*, Bearer *)
# - Passwords (password: "...")
# - Tokens (token: "...")
```

**Cause 10c: Secrets in error messages**
```bash
# Solution: Catch exceptions and sanitize
# ✗ except Exception as e:
#     logger.error(f"Error: {e}")  # Might contain secrets
# ✓ except Exception as e:
#     logger.error(f"Error: {type(e).__name__}")
#     logger.debug(f"Details: {sanitize_secrets(str(e))}")
```

---

## Performance Troubleshooting

### Agent Response Time Too Slow

**Check:**
```bash
# 1. Check agent logs for timing
grep "duration:" .claude-flow/logs/agent-*.log

# 2. Check system resources
top -b -n 1 | head -20

# 3. Check network latency
curl -w "Time: %{time_total}s\n" https://api.openrouter.io/
```

**Solutions:**
- Reduce task complexity
- Increase system resources
- Optimize agent prompts
- Use faster LLM model

### Memory Search Too Slow

**Check:**
```bash
# 1. Check HNSW index size
du -sh .claude-flow/data/agentdb/

# 2. Check number of stored tasks
ls -1 .claude-flow/data/agentdb/ | wc -l
```

**Solutions:**
- Rebuild HNSW index
- Archive old tasks
- Increase HNSW parameters
- Use faster storage (SSD)

### High Memory Usage

**Check:**
```bash
# 1. Check process memory
ps aux | grep -E "tele_bot|ruflo" | grep -v grep

# 2. Check total memory
free -h
```

**Solutions:**
- Reduce max concurrent agents
- Clear old logs
- Reduce HNSW cache size
- Restart agent periodically

---

## Recovery Procedures

### Recover from Agent Crash

```bash
# 1. Check if agent is still running
ps aux | grep tele_bot.py

# 2. If running, kill it
pkill -f tele_bot.py

# 3. Check for corrupted state
ls -la .claude-flow/sessions/

# 4. If corrupted, delete session
rm .claude-flow/sessions/telegram-*.json

# 5. Restart agent
python tele_bot.py
```

### Recover from MCP Server Crash

```bash
# 1. Check if server is running
curl http://localhost:3000/health

# 2. If not, kill any orphaned processes
pkill -f "ruflo.*mcp"

# 3. Check for corrupted state
ls -la .claude-flow/data/

# 4. If corrupted, rebuild
rm -rf .claude-flow/data/agentdb/hnsw.index

# 5. Restart server
npx ruflo@latest mcp start --port 3000
```

### Recover from Memory Corruption

```bash
# 1. Backup current memory
cp -r .claude-flow/data .claude-flow/data.backup

# 2. Rebuild HNSW index
rm -rf .claude-flow/data/agentdb/hnsw.index

# 3. Verify memory integrity
# Run a test task and check if memory works

# 4. If still broken, restore from backup
rm -rf .claude-flow/data
cp -r .claude-flow/data.backup .claude-flow/data
```

---

## Debug Mode

### Enable Debug Logging

```bash
# Set environment variable
export RUFLO_LOG_LEVEL=debug

# Restart agent
pkill -f tele_bot.py
python tele_bot.py

# Now logs will include debug information
tail -f .claude-flow/logs/agent-*.log
```

### Enable Verbose Output

```bash
# In tele_bot.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)

# Restart bot
python tele_bot.py
```

### Trace Agent Execution

```bash
# Check agent execution trace
grep "Agent:" .claude-flow/logs/agent-*.log | head -20

# Check SendMessage calls
grep "SendMessage" .claude-flow/logs/agent-*.log

# Check memory operations
grep "memory_" .claude-flow/logs/agent-*.log
```

---

## Getting Help

### Collect Debug Information

```bash
# Create debug bundle
mkdir debug-bundle
cp .env debug-bundle/  # Remove secrets first!
cp .claude-flow/config.yaml debug-bundle/
cp .claude-flow/logs/agent-*.log debug-bundle/
cp .claude-flow/logs/task-*.log debug-bundle/
tar -czf debug-bundle.tar.gz debug-bundle/

# Share with support (remove secrets first!)
```

### Check System Requirements

```bash
# Verify all requirements
node --version          # Should be 18+
python --version        # Should be 3.8+
npm --version           # Should be 8+
npx ruflo --version     # Should be 3.7.0-alpha.20+

# Check disk space
df -h /                 # Should have >1GB free

# Check network
ping 8.8.8.8           # Should respond
curl https://api.telegram.org/  # Should respond
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Cannot find module 'ruflo'` | Ruflo not installed | `npm install -g ruflo@latest` |
| `Port 3000 already in use` | Another process using port | `lsof -i :3000` and kill |
| `Connection refused` | MCP server not running | `npx ruflo@latest mcp start --port 3000` |
| `TELEGRAM_TOKEN invalid` | Wrong token | Get new token from @BotFather |
| `OWNER_ID not authorized` | Wrong user ID | Get ID from @userinfobot |
| `Path validation failed` | File outside project | Use relative paths only |
| `Command not whitelisted` | Command not allowed | Use whitelisted commands only |
| `Agent timeout` | Task took >5 minutes | Break into smaller tasks |
| `Memory search failed` | AgentDB corrupted | Delete and rebuild index |
| `Security violation` | Suspicious code detected | Review code for injection patterns |

---

## Preventive Maintenance

### Daily Checks

```bash
# Check agent is running
ps aux | grep tele_bot.py

# Check MCP server is running
curl http://localhost:3000/health

# Check disk space
df -h / | tail -1

# Check logs for errors
grep ERROR .claude-flow/logs/agent-*.log | tail -5
```

### Weekly Maintenance

```bash
# Rotate logs
mv .claude-flow/logs/agent-current.log .claude-flow/logs/agent-$(date +%Y%m%d).log

# Backup memory
cp -r .claude-flow/data .claude-flow/data.backup-$(date +%Y%m%d)

# Check memory size
du -sh .claude-flow/data/

# Verify backups exist
ls -la .claude-flow/data.backup-*
```

### Monthly Maintenance

```bash
# Clean old logs (>30 days)
find .claude-flow/logs/ -name "*.log" -mtime +30 -delete

# Archive old backups
tar -czf .claude-flow/backups-$(date +%Y%m).tar.gz .claude-flow/data.backup-*

# Verify system health
df -h /
free -h
top -b -n 1 | head -10
```

---

## Contact & Support

For issues not covered here:

1. Check logs: `tail -f .claude-flow/logs/agent-*.log`
2. Enable debug mode: `export RUFLO_LOG_LEVEL=debug`
3. Collect debug bundle (see above)
4. Check Ruflo documentation: https://ruflo.dev/docs
5. Check Telegram bot documentation: https://core.telegram.org/bots


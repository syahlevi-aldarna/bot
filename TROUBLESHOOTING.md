# Troubleshooting Guide

## Common Issues and Solutions

### 1. MCP Server Issues

#### Problem: "MCP server not responding"

**Symptoms:**
- Agents fail to spawn
- Connection timeout errors
- "Cannot connect to MCP server" messages

**Solutions:**

```bash
# Check if port 3000 is in use
lsof -i :3000

# Kill existing process if needed
kill -9 <PID>

# Restart MCP server
npx ruflo@latest mcp start

# Check MCP server logs
tail -f .claude-flow/logs/coordination.log
```

#### Problem: "Port 3000 already in use"

**Solutions:**

```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use different port
MCP_SERVER_PORT=3001 npx ruflo@latest mcp start
```

---

### 2. Agent Issues

#### Problem: "Agent timeout"

**Symptoms:**
- Agent runs for >5 minutes
- "Agent exceeded timeout" message
- Agent killed unexpectedly

**Solutions:**

```python
# Increase timeout in timeout_manager.py
timeout_manager = TimeoutManager(default_timeout=600)  # 10 minutes

# Or check what task is taking too long
tail -f .claude-flow/logs/agent_*.log
```

#### Problem: "Agent spawn failed"

**Symptoms:**
- "Failed to spawn agent" error
- Agent ID is None
- No agent in agent list

**Solutions:**

```bash
# Check MCP server is running
ps aux | grep ruflo

# Check MCP server logs
tail -f .claude-flow/logs/coordination.log

# Verify MCP client connection
python3 -c "from src.mcp_client import MCPClient; c = MCPClient(); print('Connected')"
```

#### Problem: "Agent stuck in running state"

**Symptoms:**
- Agent status always "running"
- Cannot kill agent
- Memory leak

**Solutions:**

```python
# Manually kill agent
from src.mcp_client import MCPClient
client = MCPClient()
await client.kill_agent('agent_id')

# Check agent logs
tail -f .claude-flow/logs/agent_<agent_id>.log
```

---

### 3. File Operation Issues

#### Problem: "Permission denied" when writing files

**Symptoms:**
- "Failed to write file" error
- File not created
- Backup not created

**Solutions:**

```bash
# Check file permissions
ls -la src/

# Check backup directory
ls -la .backups/

# Fix permissions
chmod 755 .backups/
chmod 644 src/

# Check file executor logs
tail -f .claude-flow/logs/error.log
```

#### Problem: "Path outside project directory"

**Symptoms:**
- "Path validation failed" error
- Cannot write to certain files
- Security violation detected

**Solutions:**

```python
# Check path validation
from src.file_executor import FileExecutor
executor = FileExecutor()
result = executor.read_file("src/app.py")  # Should work
result = executor.read_file("../etc/passwd")  # Should fail
```

#### Problem: "Backup restore failed"

**Symptoms:**
- Cannot restore from backup
- "Backup not found" error
- File corrupted

**Solutions:**

```bash
# List available backups
ls -la .backups/

# Check backup file format
file .backups/app_*.py

# Manually restore
cp .backups/app_20240101_120000.py src/app.py
```

---

### 4. Code Execution Issues

#### Problem: "Command not allowed"

**Symptoms:**
- "Command not in whitelist" error
- Bash command fails
- "Dangerous pattern detected" message

**Solutions:**

```python
# Check allowed commands
from src.bash_executor import BashExecutor
executor = BashExecutor()
print(executor.get_allowed_commands())

# Add command to whitelist if needed
# Edit ALLOWED_COMMANDS in bash_executor.py
```

#### Problem: "Command timeout"

**Symptoms:**
- "Command timeout after 60 seconds" error
- Long-running commands fail
- Tests timeout

**Solutions:**

```python
# Increase timeout
executor = BashExecutor(timeout=120)  # 2 minutes

# Or optimize command
# Instead of: npm install
# Use: npm ci --prefer-offline
```

#### Problem: "Bash execution failed"

**Symptoms:**
- Command returns non-zero exit code
- stderr output present
- "Command failed" error

**Solutions:**

```bash
# Check command manually
npm test

# Check bash executor logs
tail -f .claude-flow/logs/error.log

# Verify command syntax
bash -n script.sh
```

---

### 5. Memory and Learning Issues

#### Problem: "Memory search returns no results"

**Symptoms:**
- "No similar tasks found" message
- Empty search results
- Patterns not applied

**Solutions:**

```python
# Check if tasks are stored
from src.memory.agent_db import AgentDB
db = AgentDB()
print(db.get_all_tasks())

# Check embeddings
from src.memory.task_embedder import TaskEmbedder
embedder = TaskEmbedder()
embedding = embedder.embed_task("test task")
print(len(embedding))  # Should be > 0
```

#### Problem: "Pattern learning failed"

**Symptoms:**
- "Error learning from task" message
- Patterns not created
- Success rate not updated

**Solutions:**

```python
# Check SONA learner
from src.memory.sona_learner import SONALearner
learner = SONALearner()
result = learner.learn_from_task(task, result)
print(learner.get_stats())
```

#### Problem: "Embedding dimension mismatch"

**Symptoms:**
- "Dimension mismatch" error
- Search fails
- Similarity calculation fails

**Solutions:**

```python
# Rebuild vocabulary
embedder = TaskEmbedder()
documents = ["task 1", "task 2", "task 3"]
embedder.build_vocabulary(documents)

# Re-embed all tasks
for task in tasks:
    embedding = embedder.embed_task(task['description'])
    db.store_task(task['id'], task, embedding)
```

---

### 6. Error Handling Issues

#### Problem: "Error handler not catching exception"

**Symptoms:**
- Exception not handled
- System crashes
- No error log

**Solutions:**

```python
# Check error handler
from src.error_handler import ErrorHandler, ErrorType, ErrorSeverity
handler = ErrorHandler()
result = handler.handle_error(
    ErrorType.TIMEOUT,
    "Test error",
    ErrorSeverity.HIGH
)
print(result)
```

#### Problem: "Rollback failed"

**Symptoms:**
- "Failed to rollback" error
- File not restored
- Backup corrupted

**Solutions:**

```bash
# Check rollback manager logs
tail -f .claude-flow/logs/error.log

# Manually restore
cp .backups/file_backup.py src/file.py

# Verify file integrity
md5sum src/file.py .backups/file_backup.py
```

#### Problem: "Network retry exhausted"

**Symptoms:**
- "Max retries exceeded" error
- Circuit breaker open
- Cannot connect to endpoint

**Solutions:**

```python
# Check circuit breaker status
from src.recovery.network_retry_manager import NetworkRetryManager
manager = NetworkRetryManager()
print(manager.get_circuit_breaker_status())

# Reset circuit breaker
manager.reset_all_circuit_breakers()
```

---

### 7. Security Issues

#### Problem: "Security violation detected"

**Symptoms:**
- "Path traversal detected" error
- "Command injection detected" error
- Agent blocked

**Solutions:**

```bash
# Check security logs
tail -f .claude-flow/logs/security.log

# Review violations
grep "violation" .claude-flow/logs/security.log

# Unblock agent if needed
python3 -c "
from src.recovery.security_violation_manager import SecurityViolationManager
manager = SecurityViolationManager()
manager.unblock_agent('agent_id')
"
```

#### Problem: "Secret exposure detected"

**Symptoms:**
- "Secret exposure detected" error
- API keys in logs
- Passwords exposed

**Solutions:**

```bash
# Check what was detected
grep "SECRET" .claude-flow/logs/security.log

# Rotate secrets
# Update .env file with new values

# Clean logs
rm .claude-flow/logs/security.log
```

---

### 8. Logging Issues

#### Problem: "Log file not created"

**Symptoms:**
- No logs in .claude-flow/logs/
- "Log directory not found" error
- Logging disabled

**Solutions:**

```bash
# Create log directory
mkdir -p .claude-flow/logs

# Check permissions
chmod 755 .claude-flow/logs

# Verify logger factory
python3 -c "
from src.logging.logger_factory import LoggerFactory
factory = LoggerFactory()
logger = factory.get_logger('test', log_file='test.log')
logger.info('Test message')
"
```

#### Problem: "Log file too large"

**Symptoms:**
- Log files > 10MB
- Disk space issues
- Slow log reading

**Solutions:**

```bash
# Check log sizes
du -sh .claude-flow/logs/*

# Archive old logs
tar -czf .claude-flow/logs/archive_$(date +%Y%m%d).tar.gz .claude-flow/logs/*.log

# Clean old logs
find .claude-flow/logs -name "*.log" -mtime +7 -delete
```

#### Problem: "Cannot read logs"

**Symptoms:**
- "Failed to read log file" error
- Log analyzer returns empty
- Cannot search logs

**Solutions:**

```python
# Check log format
from src.logging.log_analyzer import LogAnalyzer
analyzer = LogAnalyzer()
entries = analyzer.read_log_file('agent.log')
print(entries[:1])  # Print first entry

# Verify JSON format
python3 -m json.tool .claude-flow/logs/agent.log | head -20
```

---

### 9. Telegram Bot Issues

#### Problem: "Bot not responding to messages"

**Symptoms:**
- Messages not received
- No response from bot
- "Telegram connection failed" error

**Solutions:**

```bash
# Check bot token
grep TELEGRAM_BOT_TOKEN .env

# Verify token is valid
curl -s https://api.telegram.org/bot<TOKEN>/getMe

# Check bot logs
tail -f .claude-flow/logs/coordination.log
```

#### Problem: "Long response timeout"

**Symptoms:**
- "Response timeout" error
- Message not sent back
- User sees "Bot is not responding"

**Solutions:**

```python
# Increase timeout in tele_bot.py
timeout = 120  # 2 minutes

# Or split response
if len(response) > 4096:
    # Send in chunks
    for i in range(0, len(response), 4096):
        send_message(response[i:i+4096])
```

---

### 10. Performance Issues

#### Problem: "System running slow"

**Symptoms:**
- High CPU usage
- High memory usage
- Slow response times

**Solutions:**

```bash
# Check system resources
top -b -n 1 | head -20

# Check Python memory usage
ps aux | grep python3

# Profile code
python3 -m cProfile -s cumulative tele_bot.py
```

#### Problem: "Memory leak"

**Symptoms:**
- Memory usage increases over time
- System becomes unresponsive
- Out of memory error

**Solutions:**

```python
# Check for unclosed resources
import gc
gc.collect()

# Monitor memory
import tracemalloc
tracemalloc.start()
# ... run code ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f}MB; Peak: {peak / 1024 / 1024:.1f}MB")
```

---

## Debug Mode

Enable debug logging for more detailed information:

```bash
# Set debug level
export LOG_LEVEL=DEBUG

# Or in Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Getting Help

If you can't find a solution:

1. Check logs in `.claude-flow/logs/`
2. Run tests: `python3 -m pytest tests/ -v`
3. Check GitHub Issues
4. Create a new issue with:
   - Error message
   - Relevant logs
   - Steps to reproduce
   - System information

## Performance Tuning

### Optimize Agent Spawn Time

```python
# Reduce timeout for faster failure detection
timeout_manager = TimeoutManager(default_timeout=300)  # 5 minutes
```

### Optimize Memory Search

```python
# Reduce search results for faster response
similar_tasks = agent_db.search_similar(embedding, top_k=3)  # Instead of 5
```

### Optimize Logging

```python
# Use async logging for better performance
# Or reduce log level in production
logging.getLogger().setLevel(logging.WARNING)
```

---

**Last Updated**: 2024
**Version**: 1.0.0

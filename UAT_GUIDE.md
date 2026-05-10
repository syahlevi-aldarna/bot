# 🧪 User Acceptance Test (UAT) Guide - RUFLO

## Overview

Dokumen ini adalah **step-by-step guide untuk testing RUFLO dari perspektif user nyata**, dari setup awal sampai menjalankan task pertama dan menerima hasil.

**Tujuan:** Memastikan sistem bekerja end-to-end seperti yang dijanjikan di dokumentasi.

---

## Prerequisites

Sebelum mulai UAT, pastikan Anda memiliki:

- ✅ Python 3.8+ installed
- ✅ Node.js 14+ installed
- ✅ Telegram account
- ✅ Telegram Bot Token (dari @BotFather)
- ✅ Chat ID Telegram Anda
- ✅ Git installed
- ✅ 30 menit waktu luang

---

## Phase 1: Setup & Configuration (5 menit)

### Step 1.1: Clone Repository

```bash
git clone https://github.com/syahlevi-aldarna/bot.git
cd bot
```

**Expected Output:**
```
Cloning into 'bot'...
remote: Enumerating objects: ...
Receiving objects: 100% (...)
```

**✅ Success Criteria:** Repository cloned successfully

---

### Step 1.2: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

**Expected Output:**
```
Collecting pytest==8.2.2
...
Successfully installed ...

npm notice ...
added X packages
```

**✅ Success Criteria:** All dependencies installed without errors

---

### Step 1.3: Get Telegram Bot Token

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow instructions:
   - Give bot a name (e.g., "RUFLO Bot")
   - Give bot a username (e.g., "ruflo_bot_123")
5. Copy the token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

**✅ Success Criteria:** You have a valid bot token

---

### Step 1.4: Get Your Chat ID

1. Send message to your bot: `/start`
2. In terminal, run:

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates" | grep -o '"chat":{"id":[0-9]*' | grep -o '[0-9]*'
```

Replace `<YOUR_BOT_TOKEN>` with your actual token.

**Expected Output:**
```
123456789
```

**✅ Success Criteria:** You have your chat ID

---

### Step 1.5: Configure Environment

```bash
# Create .env file
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
MCP_SERVER_PORT=3000
LOG_LEVEL=INFO
EOF
```

**Verify:**
```bash
cat .env
```

**✅ Success Criteria:** .env file created with correct values

---

## Phase 2: System Startup (3 menit)

### Step 2.1: Start MCP Server

```bash
npx ruflo@latest mcp start
```

**Expected Output:**
```
Starting MCP server...
Server listening on port 3000
✓ MCP server ready
```

**⏱️ Wait:** 10-15 seconds for server to fully start

**✅ Success Criteria:** MCP server running on port 3000

---

### Step 2.2: Start Telegram Bot (New Terminal)

Open a new terminal window and run:

```bash
cd bot
python3 tele_bot.py
```

**Expected Output:**
```
Starting Telegram bot...
Bot connected to Telegram
Listening for messages...
```

**✅ Success Criteria:** Bot connected and listening

---

### Step 2.3: Verify System Health

In a third terminal, run:

```bash
# Check if MCP server is running
curl http://localhost:3000/health

# Check if logs directory exists
ls -la .claude-flow/logs/
```

**Expected Output:**
```
{"status":"ok"}

total ...
drwxr-xr-x ... coordination.log
drwxr-xr-x ... agent.log
```

**✅ Success Criteria:** Both services running and logs directory exists

---

## Phase 3: First Task - Simple Function (5 menit)

### Step 3.1: Send Task to Telegram

Open Telegram and send this message to your bot:

```
Create a function that validates email addresses
```

**What to expect:**
- Bot should acknowledge receipt
- Bot should show "Agent working..."
- Status should update every 2 seconds

**✅ Success Criteria:** Bot acknowledges and shows working status

---

### Step 3.2: Monitor Progress

In terminal, watch the logs:

```bash
tail -f .claude-flow/logs/agent_*.log
```

**Expected Output:**
```
[2024-05-10 19:45:23] Agent spawned: coder_agent_123
[2024-05-10 19:45:25] Coder writing code...
[2024-05-10 19:45:30] Code written, sending to reviewer
[2024-05-10 19:45:35] Reviewer checking code...
[2024-05-10 19:45:40] Review complete, sending to tester
[2024-05-10 19:45:45] Tester generating tests...
[2024-05-10 19:45:50] Tests passing: 5/5
[2024-05-10 19:45:52] Task complete!
```

**⏱️ Expected Duration:** 30-60 seconds total

**✅ Success Criteria:** Logs show all 3 agents working in sequence

---

### Step 3.3: Receive Result in Telegram

After 30-60 seconds, you should receive a message in Telegram:

```
✅ Task Complete!

Code:
```python
def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

Tests: 5/5 passing ✅

Execution Time: 45 seconds
```

**✅ Success Criteria:** 
- Result received in Telegram
- Code is valid Python
- Tests are passing
- Execution time is reasonable

---

### Step 3.4: Verify Code Works

Test the code locally:

```bash
python3 << 'EOF'
def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Test cases
print(validate_email("user@example.com"))  # Should be True
print(validate_email("invalid.email"))     # Should be False
print(validate_email("test@domain.co.uk")) # Should be True
EOF
```

**Expected Output:**
```
True
False
True
```

**✅ Success Criteria:** Code works as expected

---

## Phase 4: Second Task - Learning System (5 menit)

### Step 4.1: Send Similar Task

Send this message to Telegram:

```
Create a function that validates phone numbers
```

**What to expect:**
- Agent should recall the email validator pattern
- Should be faster than first task (agent learned!)
- Similar structure but for phone numbers

**⏱️ Expected Duration:** 20-30 seconds (faster than first task!)

**✅ Success Criteria:** Task completes faster due to learning

---

### Step 4.2: Compare Results

Check logs to see if memory system was used:

```bash
grep -i "memory\|pattern\|similar" .claude-flow/logs/memory.log
```

**Expected Output:**
```
[2024-05-10 19:47:15] Searching for similar tasks...
[2024-05-10 19:47:16] Found similar task: email_validator
[2024-05-10 19:47:17] Applying learned pattern...
[2024-05-10 19:47:18] Pattern applied successfully
```

**✅ Success Criteria:** Memory system found and applied similar pattern

---

## Phase 5: Error Handling Test (5 menit)

### Step 5.1: Send Invalid Task

Send this message:

```
Create a function that deletes all files in /etc
```

**What to expect:**
- Bot should reject the task
- Security violation should be detected
- User should be notified

**Expected Telegram Response:**
```
❌ Security Violation Detected!

Reason: Dangerous command detected
Command: rm -rf /etc
Status: BLOCKED

This operation is not allowed for security reasons.
```

**✅ Success Criteria:** Security system blocks dangerous operations

---

### Step 5.2: Verify Security Logs

Check security logs:

```bash
tail -f .claude-flow/logs/security.log
```

**Expected Output:**
```
[2024-05-10 19:49:00] VIOLATION: Command injection detected
[2024-05-10 19:49:00] Command: rm -rf /etc
[2024-05-10 19:49:00] Action: BLOCKED
[2024-05-10 19:49:00] Agent: blocked
```

**✅ Success Criteria:** Security event logged correctly

---

## Phase 6: Monitoring & Logs (5 menit)

### Step 6.1: Check Agent Logs

```bash
ls -lah .claude-flow/logs/
```

**Expected Output:**
```
total ...
-rw-r--r-- ... agent_action.log
-rw-r--r-- ... memory.log
-rw-r--r-- ... security.log
-rw-r--r-- ... coordination.log
-rw-r--r-- ... error.log
```

**✅ Success Criteria:** All log files created

---

### Step 6.2: View Agent Statistics

```bash
python3 << 'EOF'
from src.logging.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer()
stats = analyzer.get_log_stats()
print(f"Total tasks: {stats.get('total_tasks', 0)}")
print(f"Success rate: {stats.get('success_rate', 0)}%")
print(f"Average time: {stats.get('avg_time', 0)}s")
EOF
```

**Expected Output:**
```
Total tasks: 2
Success rate: 100%
Average time: 42.5s
```

**✅ Success Criteria:** Statistics show correct metrics

---

### Step 6.3: Check Memory System

```bash
python3 << 'EOF'
from src.memory.agent_db import AgentDB

db = AgentDB()
tasks = db.get_all_tasks()
print(f"Stored tasks: {len(tasks)}")
for task in tasks:
    print(f"  - {task['description'][:50]}...")
EOF
```

**Expected Output:**
```
Stored tasks: 2
  - Create a function that validates email addresses...
  - Create a function that validates phone numbers...
```

**✅ Success Criteria:** Memory system storing tasks correctly

---

## Phase 7: Stress Test (5 menit)

### Step 7.1: Send Multiple Tasks

Send 3 tasks in quick succession:

```
Task 1: Create a function that validates URLs
Task 2: Create a function that validates credit card numbers
Task 3: Create a function that validates postal codes
```

**What to expect:**
- Bot should queue tasks
- Process them one by one
- All should complete successfully

**✅ Success Criteria:** All 3 tasks complete without errors

---

### Step 7.2: Check Queue Status

```bash
python3 << 'EOF'
from src.coordination.send_message import SendMessageCoordinator

coordinator = SendMessageCoordinator()
queue_status = coordinator.get_queue_status()
print(f"Pending tasks: {queue_status.get('pending', 0)}")
print(f"Completed tasks: {queue_status.get('completed', 0)}")
EOF
```

**Expected Output:**
```
Pending tasks: 0
Completed tasks: 5
```

**✅ Success Criteria:** Queue processed all tasks

---

## Phase 8: Cleanup & Verification (2 menit)

### Step 8.1: Stop Services

In each terminal, press `Ctrl+C` to stop:

```bash
# Terminal 1: Stop MCP server
Ctrl+C

# Terminal 2: Stop Telegram bot
Ctrl+C
```

**✅ Success Criteria:** Services stopped gracefully

---

### Step 8.2: Run Full Test Suite

```bash
# Run all tests
npm test && python3 -m pytest tests/ -q
```

**Expected Output:**
```
Test Suites: 1 passed, 1 total
Tests: 20 passed, 20 total

125 passed in 6.98s
```

**✅ Success Criteria:** All 145 tests still passing

---

### Step 8.3: Verify Backups

```bash
ls -la .backups/
```

**Expected Output:**
```
total ...
-rw-r--r-- ... file_backup_20240510_194500.py
-rw-r--r-- ... file_backup_20240510_194530.py
```

**✅ Success Criteria:** Backup system created backups

---

## UAT Results Summary

### Checklist

- [ ] Phase 1: Setup & Configuration ✅
- [ ] Phase 2: System Startup ✅
- [ ] Phase 3: First Task (Email Validator) ✅
- [ ] Phase 4: Learning System (Phone Validator) ✅
- [ ] Phase 5: Error Handling (Security) ✅
- [ ] Phase 6: Monitoring & Logs ✅
- [ ] Phase 7: Stress Test (Multiple Tasks) ✅
- [ ] Phase 8: Cleanup & Verification ✅

### Metrics

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Setup Time | < 5 min | ___ | ✅/❌ |
| First Task Time | 30-60s | ___ | ✅/❌ |
| Second Task Time | 20-30s | ___ | ✅/❌ |
| Security Block | Instant | ___ | ✅/❌ |
| Test Pass Rate | 100% | ___ | ✅/❌ |
| Backup Creation | Yes | ___ | ✅/❌ |
| Log Generation | Yes | ___ | ✅/❌ |
| Memory Learning | Yes | ___ | ✅/❌ |

### Overall Result

**Total Tests Passed:** ___ / 8  
**Success Rate:** ___%  
**Status:** ✅ PASS / ❌ FAIL

---

## Troubleshooting During UAT

### Issue: Bot not responding

**Solution:**
```bash
# Check if bot is running
ps aux | grep tele_bot

# Check Telegram token
grep TELEGRAM_BOT_TOKEN .env

# View bot logs
tail -f .claude-flow/logs/coordination.log
```

---

### Issue: MCP server not starting

**Solution:**
```bash
# Check if port 3000 is in use
lsof -i :3000

# Kill existing process
kill -9 <PID>

# Restart MCP server
npx ruflo@latest mcp start
```

---

### Issue: Task timeout

**Solution:**
```bash
# Increase timeout
# Edit timeout_manager.py
# Change: default_timeout=300 to default_timeout=600

# Restart bot
python3 tele_bot.py
```

---

### Issue: Permission denied on file write

**Solution:**
```bash
# Fix permissions
chmod 755 .backups/
chmod 644 src/

# Restart bot
python3 tele_bot.py
```

---

## Sign-Off

**Tester Name:** _______________  
**Date:** _______________  
**Status:** ✅ PASS / ❌ FAIL  
**Comments:** _______________

---

## Appendix: Expected Outputs

### Email Validator Output

```python
def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

### Phone Validator Output

```python
def validate_phone(phone):
    import re
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))
```

### URL Validator Output

```python
def validate_url(url):
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))
```

---

## Next Steps After UAT

If all tests pass:
1. ✅ System is production-ready
2. ✅ Ready for user adoption
3. ✅ Ready for market launch
4. ✅ Ready for enterprise deployment

If any tests fail:
1. ❌ Document the issue
2. ❌ Create bug report
3. ❌ Fix the issue
4. ❌ Re-run UAT

---

**Last Updated:** May 2024  
**Version:** 1.0.0  
**Status:** Ready for User Acceptance Testing

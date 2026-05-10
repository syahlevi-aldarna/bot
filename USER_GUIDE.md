# 🤖 RUFLO: Autonomous Coding Agent via Telegram

## Product Identity

**RUFLO** adalah sistem koordinasi agen AI yang memungkinkan Anda menjalankan tugas coding kompleks (write code, review, test) secara otomatis melalui Telegram, tanpa perlu membuka terminal atau IDE.

**Value Proposition:** Ubah cara Anda bekerja dengan kode—dari "manual coding" menjadi "collaborative AI agents" yang bekerja 24/7, belajar dari pengalaman, dan memberikan hasil berkualitas tinggi dengan jaminan keamanan penuh.

---

## 🎯 Core Features & Benefits

### 1. **Telegram-First Interface**
**Feature:** Kontrol seluruh sistem melalui Telegram Bot  
**Benefit:** Anda bisa memberikan perintah coding dari mana saja—di kantor, di rumah, bahkan di kafe—tanpa perlu setup kompleks.

```
User: "Create email validator function"
→ Agent: Writes code, reviews, tests
→ Result: Working code + test suite delivered to Telegram
```

### 2. **Safe Code Execution Layer**
**Feature:** Semua eksekusi kode dijalankan dalam sandbox dengan validasi path dan command whitelist  
**Benefit:** Anda tidak perlu khawatir agen akan menghapus file penting atau menjalankan command berbahaya. Sistem otomatis melakukan backup sebelum perubahan.

**Security Guarantees:**
- ✅ No file operations outside project directory
- ✅ Only whitelisted bash commands allowed
- ✅ Automatic backup before any file modification
- ✅ Secret protection (.env files never exposed)

### 3. **Multi-Agent Coordination Pipeline**
**Feature:** 3 agen spesialis (Coder, Reviewer, Tester) bekerja secara berurutan  
**Benefit:** Setiap tugas melalui quality gate—kode ditulis, direview untuk kualitas/security, lalu ditest. Hasilnya adalah kode production-ready, bukan draft.

```
Task Flow:
Coder Agent → (writes code) → 
Reviewer Agent → (checks quality/security) → 
Tester Agent → (generates & runs tests) → 
Result: Telegram notification
```

### 4. **Memory & Learning System**
**Feature:** Agen mengingat solusi masa lalu dan belajar dari pola sukses  
**Benefit:** Semakin lama Anda menggunakan sistem, semakin cepat dan akurat hasilnya. Agen tidak perlu "belajar ulang" untuk tugas serupa.

**Example:**
- Task 1: "Create email validator" → Agen belajar pola
- Task 2: "Create phone validator" → Agen recall pola serupa, eksekusi 3x lebih cepat

### 5. **Comprehensive Logging & Monitoring**
**Feature:** Setiap aksi agen tercatat dalam structured JSON logs  
**Benefit:** Anda bisa audit trail lengkap, debug masalah dengan mudah, dan monitor performa agen real-time.

### 6. **Error Recovery & Resilience**
**Feature:** Sistem otomatis handle timeout, network errors, dan security violations  
**Benefit:** Agen tidak crash—jika ada masalah, sistem otomatis retry atau rollback, dan Anda diberitahu via Telegram.

---

## 📖 User Journey: Step-by-Step Guide

### Phase 1: Setup (5 menit)

#### Step 1: Clone Repository
```bash
git clone https://github.com/syahlevi-aldarna/bot.git
cd bot
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
npm install
```

#### Step 3: Configure Telegram Bot
```bash
# Edit .env file
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

**How to get Telegram Bot Token:**
1. Open Telegram, search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions, copy token to `.env`

#### Step 4: Start System
```bash
bash start.sh
```

**What happens:**
- ✅ MCP Server starts on port 3000
- ✅ Telegram Bot connects
- ✅ System ready for commands

---

### Phase 2: First Command (2 menit)

#### Send Your First Task
Open Telegram, send message to your bot:

```
"Create a function that validates email addresses"
```

**Behind the scenes:**
1. Telegram Bot receives message
2. Spawns Coder Agent via MCP Server
3. Coder writes validation function
4. Sends to Reviewer Agent
5. Reviewer checks code quality
6. Sends to Tester Agent
7. Tester generates & runs tests
8. Results sent back to Telegram

**Expected Output:**
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
```

---

### Phase 3: Monitor & Iterate (Ongoing)

#### Check Agent Status
```bash
# View real-time logs
tail -f .claude-flow/logs/agent_*.log

# View security events
tail -f .claude-flow/logs/security.log

# View memory learning
tail -f .claude-flow/logs/memory.log
```

#### Refine Results
If you want to improve the result:

```
"Improve the email validator to handle international domains"
```

Agent akan:
1. Recall previous email validator from memory
2. Apply improvement
3. Re-test
4. Send updated version

---

## 🔒 Safety & Trust

### How RUFLO Protects Your System

#### 1. **Sandboxed Execution**
- All code runs in isolated environment
- Cannot access files outside project directory
- Cannot execute dangerous commands (rm -rf, etc.)

#### 2. **Automatic Backups**
- Before any file modification, system creates backup
- If something goes wrong, automatic rollback
- Backups stored in `.backups/` directory

#### 3. **Secret Protection**
- `.env` files never appear in logs
- API keys never exposed to Telegram
- Secrets masked in all outputs

#### 4. **Command Whitelist**
Only these commands allowed:
- `npm` (package management)
- `git` (version control)
- `python3` (code execution)
- `node` (JavaScript execution)
- `bash` (shell scripts)

#### 5. **Timeout Protection**
- Agents automatically killed after 5 minutes
- Prevents infinite loops or hanging processes
- User notified via Telegram

#### 6. **Audit Trail**
- Every action logged with timestamp
- Who did what, when, and why
- Searchable and exportable logs

---

## 🛠️ Technical Specification

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram User                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Telegram Bot (Python)                       │
│  - Receives messages                                     │
│  - Spawns agents via MCP                                │
│  - Sends results back                                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         MCP Server (Node.js on port 3000)               │
│  - Agent spawning & lifecycle management                │
│  - Message coordination                                 │
│  - Memory store access                                  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │ Coder  │  │Reviewer│  │ Tester │
    │ Agent  │  │ Agent  │  │ Agent  │
    └────────┘  └────────┘  └────────┘
        │            │            │
        └────────────┼────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
    ┌──────────────┐      ┌──────────────┐
    │ Safe Code    │      │ Memory &     │
    │ Execution    │      │ Learning     │
    │ Layer        │      │ System       │
    └──────────────┘      └──────────────┘
        │                         │
        ▼                         ▼
    ┌──────────────┐      ┌──────────────┐
    │ File/Bash    │      │ Vector DB    │
    │ Executor     │      │ (HNSW)       │
    └──────────────┘      └──────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Bot Interface** | Python 3.10+ | Telegram integration |
| **MCP Server** | Node.js + Ruflo | Agent coordination |
| **Agents** | Claude API | Code generation & review |
| **Execution** | Python subprocess | Safe code execution |
| **Memory** | HNSW Vector DB | Task similarity search |
| **Logging** | Python logging | Structured JSON logs |
| **Testing** | pytest + Jest | Comprehensive test suite |

### System Requirements

```
Minimum:
- Python 3.8+
- Node.js 14+
- 2GB RAM
- 500MB disk space

Recommended:
- Python 3.10+
- Node.js 18+
- 4GB RAM
- 2GB disk space (for logs & backups)
```

---

## ⚡ Quick Start Guide (< 2 minutes)

### For Impatient Users

```bash
# 1. Clone & setup
git clone https://github.com/syahlevi-aldarna/bot.git
cd bot
pip install -r requirements.txt && npm install

# 2. Configure
cp .env.example .env
# Edit .env with your Telegram bot token

# 3. Run
bash start.sh

# 4. Send message to Telegram bot
# "Create a hello world function"

# 5. Wait for result (30-60 seconds)
# Check .claude-flow/logs/ for details
```

---

## 📊 Performance Metrics

### Typical Execution Times

| Task | Time | Notes |
|------|------|-------|
| Simple function | 30-45s | Write + review + test |
| Complex feature | 2-3 min | Multiple files, integration |
| Code review | 15-20s | Existing code analysis |
| Test generation | 20-30s | Full test suite creation |

### System Capacity

- **Concurrent agents:** 5-10 (depends on hardware)
- **Message queue:** 100+ pending tasks
- **Memory storage:** 10,000+ task records
- **Log retention:** 30 days (auto-archive)

---

## 🐛 Troubleshooting

### Common Issues

#### "Bot not responding"
```bash
# Check if MCP server is running
ps aux | grep ruflo

# Check Telegram token
grep TELEGRAM_BOT_TOKEN .env

# View logs
tail -f .claude-flow/logs/coordination.log
```

#### "Agent timeout"
```bash
# Increase timeout in timeout_manager.py
# Default: 300 seconds (5 minutes)
# Increase to: 600 seconds (10 minutes)
```

#### "Permission denied on file write"
```bash
# Fix permissions
chmod 755 .backups/
chmod 644 src/
```

**For more troubleshooting:** See `TROUBLESHOOTING.md`

---

## 🚀 Advanced Usage

### Custom Agent Configuration

```python
# In tele_bot.py
agent_config = {
    'timeout': 600,           # 10 minutes
    'max_retries': 3,         # Retry failed tasks
    'memory_top_k': 5,        # Recall top 5 similar tasks
    'log_level': 'DEBUG'      # Verbose logging
}
```

### Monitoring Dashboard

```bash
# Real-time agent status
python3 -c "
from src.logging.log_analyzer import LogAnalyzer
analyzer = LogAnalyzer()
print(analyzer.generate_report())
"
```

### Export Task History

```bash
# Export all completed tasks
python3 -c "
from src.memory.agent_db import AgentDB
db = AgentDB()
tasks = db.get_all_tasks()
# Process and export...
"
```

---

## 📞 Support & Community

### Getting Help

1. **Check Logs:** `.claude-flow/logs/` contains detailed information
2. **Read Docs:** `ARCHITECTURE.md` for technical details
3. **Run Tests:** `npm test && python3 -m pytest tests/` to verify setup
4. **GitHub Issues:** Report bugs or request features

### Feedback

We'd love to hear from you! Share:
- Feature requests
- Bug reports
- Performance insights
- Use case stories

---

## 📋 Correctness Properties (What We Guarantee)

RUFLO is built with formal correctness properties that are continuously verified:

✅ **Agent Isolation** - Agents don't interfere with each other  
✅ **Memory Consistency** - Stored tasks always retrievable  
✅ **Code Safety** - No file operations outside project  
✅ **Command Safety** - Only whitelisted commands execute  
✅ **Secret Protection** - Secrets never exposed  
✅ **Timeout Enforcement** - Agents killed after 5 minutes  
✅ **Learning Effectiveness** - Agent improves over time  
✅ **Coordination Correctness** - Agents execute in right order  

---

## 📈 Roadmap

### Phase 10: Advanced Features (Planned)
- [ ] Multi-project support
- [ ] Custom agent templates
- [ ] Performance analytics dashboard
- [ ] Slack integration
- [ ] GitHub integration

### Phase 11: Enterprise Features (Planned)
- [ ] Role-based access control
- [ ] Audit logging for compliance
- [ ] API rate limiting
- [ ] Multi-tenant support

---

## 📄 License & Attribution

RUFLO is built on:
- **Ruflo MCP Server** - Agent coordination
- **Claude API** - Code generation & review
- **Python ecosystem** - Core infrastructure

---

## 🎓 Learning Resources

### For Beginners
- Start with Quick Start Guide above
- Send simple tasks first
- Monitor logs to understand flow

### For Developers
- Read `ARCHITECTURE.md` for system design
- Check `src/` for implementation details
- Review tests in `tests/` for usage examples

### For DevOps
- Monitor `.claude-flow/logs/` for system health
- Set up log rotation for production
- Configure backup retention policy

---

## ✨ What Makes RUFLO Different

| Feature | RUFLO | Traditional Approach |
|---------|-------|---------------------|
| **Interface** | Telegram (anywhere) | Terminal/IDE (local) |
| **Coordination** | Multi-agent pipeline | Single tool |
| **Learning** | Remembers past solutions | Starts fresh each time |
| **Safety** | Sandboxed + backups | Manual safeguards |
| **Monitoring** | Real-time logs | Manual checking |
| **Scalability** | 5-10 concurrent agents | Limited by user |

---

## 🎯 Next Steps

1. **Install & Setup** (5 min) - Follow Quick Start Guide
2. **Send First Task** (2 min) - Try simple function
3. **Monitor Results** (ongoing) - Check logs & Telegram
4. **Iterate & Learn** (ongoing) - Refine tasks, improve results
5. **Scale Up** (optional) - Add more complex tasks

---

**Ready to transform your coding workflow?** 🚀

Start with: `bash start.sh` and send your first task to Telegram!

---

*Last Updated: May 2024*  
*Version: 1.0.0 (Production Ready)*  
*Status: ✅ Stable & Tested (145/145 tests passing)*

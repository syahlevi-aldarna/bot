# Design: Autonomous Coding Agent via Telegram

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram User                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Telegram Bot (tele_bot.py)                      │
│  - Receive message from user                                │
│  - Validate OWNER_ID                                        │
│  - Send to Ruflo MCP Server                                 │
│  - Receive response & send back to Telegram                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           Ruflo MCP Server (npx ruflo@latest mcp start)      │
│  - Orchestration Layer                                      │
│  - Router (task → agent)                                    │
│  - 27 Hooks (pre/post execution)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Swarm Coordination Layer                        │
│  - Topology: hierarchical-mesh                              │
│  - Max Agents: 15                                           │
│  - Consensus: enabled                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Coder Agent  │  │Reviewer Agent│  │ Tester Agent │
│              │  │              │  │              │
│ - Read files │  │ - Review code│  │ - Write tests│
│ - Write code │  │ - Check style│  │ - Run tests  │
│ - Git ops    │  │ - Security   │  │ - Report     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Memory & Learning Layer                        │
│  - AgentDB (vector database)                                │
│  - HNSW indexing (fast search)                              │
│  - SONA (self-learning patterns)                            │
│  - ReasoningBank (trajectory learning)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Code Execution Layer                           │
│  - File I/O (read/write with validation)                    │
│  - Bash execution (npm, git, python, etc.)                  │
│  - Test execution                                           │
│  - Logging to .claude-flow/logs/                            │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Telegram Bot Enhancement (tele_bot.py)

**Current state:** Calls `npx ruflo ask` (which doesn't exist)

**New state:** 
- Calls Ruflo MCP server via HTTP/stdio
- Sends task to agent_spawn tool
- Polls agent_status for progress
- Streams updates back to Telegram

```python
# Pseudo-code
async def handle_message(update, context):
    task = update.message.text
    
    # Spawn agent via MCP
    agent_id = await mcp_call("agent_spawn", {
        "type": "coder",
        "task": task,
        "namespace": "telegram-tasks"
    })
    
    # Poll status
    while True:
        status = await mcp_call("agent_status", {"agent_id": agent_id})
        await update.message.reply_text(f"Status: {status.state}")
        
        if status.state == "completed":
            await update.message.reply_text(f"Result:\n{status.output}")
            break
        
        await asyncio.sleep(2)
```

### 2. Ruflo MCP Server Integration

**Setup:**
```bash
# Start MCP server in background
npx ruflo@latest mcp start --port 3000
```

**Tools used:**
- `agent_spawn` - Create new agent
- `agent_status` - Check agent progress
- `agent_list` - List running agents
- `memory_store` - Save task results
- `memory_search` - Retrieve past solutions
- `swarm_init` - Initialize swarm
- `swarm_status` - Check swarm health

### 3. Agent Coordination (SendMessage Pattern)

**Coder Agent:**
```javascript
Agent({
  prompt: `
    Task: ${task}
    
    1. Understand the requirement
    2. Read relevant files
    3. Write/edit code
    4. SendMessage to 'reviewer' with code changes
  `,
  name: "coder",
  type: "coder",
  run_in_background: true
})
```

**Reviewer Agent:**
```javascript
Agent({
  prompt: `
    Wait for 'coder' message.
    Review the code for:
    - Code quality
    - Security issues
    - Best practices
    
    SendMessage to 'tester' with review feedback
  `,
  name: "reviewer",
  type: "reviewer",
  run_in_background: true
})
```

**Tester Agent:**
```javascript
Agent({
  prompt: `
    Wait for 'reviewer' message.
    1. Write tests for the code
    2. Run tests
    3. Report results back to 'coder' if tests fail
    4. SendMessage final results to 'telegram-bot'
  `,
  name: "tester",
  type: "tester",
  run_in_background: true
})
```

### 4. Code Execution Layer

**File Operations:**
```python
# Allowed operations
- Read: any file in project (except .env, .git)
- Write: src/, tests/, config/ (with backup)
- Execute: npm, git, python, bash (with whitelist)

# Validation
- Path must be within project directory
- No absolute paths
- No dangerous commands (rm -rf, etc.)
```

**Bash Execution:**
```python
# Whitelist of allowed commands
ALLOWED_COMMANDS = [
    "npm", "yarn", "python", "git", "node",
    "cat", "ls", "mkdir", "cp", "mv",
    "grep", "find", "echo", "test"
]

# Validation
- Command must start with whitelisted command
- No pipes to dangerous commands
- No command injection
```

### 5. Memory & Learning

**Storage:**
```
.claude-flow/
├── data/
│   ├── agentdb/          # Vector database
│   ├── memory-graph/     # Entity relationships
│   └── patterns/         # Learned patterns
├── logs/
│   ├── agent-*.log       # Agent execution logs
│   └── task-*.log        # Task logs
└── sessions/
    └── telegram-*.json   # Session state
```

**Learning Flow:**
1. Task completed → Store in AgentDB
2. Embed task + solution via HNSW
3. Future similar tasks → Retrieve via vector search
4. Agent learns patterns via SONA
5. Confidence increases with successful patterns

### 6. Error Handling & Recovery

**Error scenarios:**
1. Agent timeout (>5 min) → Kill agent, report to user
2. File write fails → Restore from backup, retry
3. Test fails → Send back to coder for fix
4. Network error → Retry with exponential backoff
5. Security violation → Block operation, log incident

**Recovery:**
- All state persisted to disk
- Agent can resume from checkpoint
- Memory survives crashes
- Telegram session state saved

## Data Flow

### Task Execution Flow

```
1. User sends message to Telegram
   ↓
2. Bot validates OWNER_ID
   ↓
3. Bot calls agent_spawn (coder)
   ↓
4. Coder reads files, writes code
   ↓
5. Coder calls SendMessage to reviewer
   ↓
6. Reviewer reviews code
   ↓
7. Reviewer calls SendMessage to tester
   ↓
8. Tester writes tests, runs them
   ↓
9. If tests pass → Store in memory, report to Telegram
   If tests fail → SendMessage back to coder
   ↓
10. Bot sends final result to Telegram user
```

### Memory Retrieval Flow

```
1. New task arrives
   ↓
2. Embed task description
   ↓
3. Search AgentDB via HNSW (fast vector search)
   ↓
4. Retrieve similar past solutions
   ↓
5. Agent learns from past patterns
   ↓
6. Agent applies learned patterns to new task
```

## Configuration

### Environment Variables (in .env)
```
OPENROUTER_API_KEY=...          # For LLM calls
TELEGRAM_TOKEN=...              # Telegram bot token
OWNER_ID=...                    # Only user who can trigger agent
RUFLO_MCP_PORT=3000             # MCP server port
RUFLO_AGENT_TIMEOUT=300         # 5 minutes
RUFLO_MAX_AGENTS=15             # Max concurrent agents
```

### Ruflo Configuration (.claude-flow/config.yaml)
```yaml
swarm:
  topology: hierarchical-mesh
  maxAgents: 15
  coordinationStrategy: consensus

memory:
  backend: hybrid
  enableHNSW: true
  persistPath: .claude-flow/data

hooks:
  enabled: true
  autoExecute: true
```

## Security Considerations

1. **Input Validation**
   - Validate all file paths (no ../)
   - Validate bash commands (whitelist)
   - Scan for prompt injection (AIDefence)

2. **Secret Protection**
   - Never log .env files
   - Never send secrets to Telegram
   - Strip PII before logging

3. **Access Control**
   - Only OWNER_ID can trigger agent
   - File operations restricted to project dir
   - Bash commands restricted to whitelist

4. **Audit Trail**
   - All operations logged
   - Logs stored in .claude-flow/logs/
   - Searchable via HNSW

## Testing Strategy

### Unit Tests
- File validation logic
- Bash command validation
- Memory storage/retrieval

### Integration Tests
- Agent spawn and status
- SendMessage coordination
- Code execution (read/write/bash)

### End-to-End Tests
- Full task execution (coder → reviewer → tester)
- Memory learning and retrieval
- Error recovery

## Deployment

### Prerequisites
- Node.js 18+
- Python 3.8+
- Ruflo v3.7.0-alpha.20 installed
- .env configured with API keys

### Startup
```bash
# Terminal 1: Start Ruflo MCP server
npx ruflo@latest mcp start --port 3000

# Terminal 2: Start Telegram bot
python tele_bot.py
```

### Monitoring
- Check .claude-flow/logs/ for agent logs
- Check .claude-flow/data/ for memory
- Monitor agent status via Telegram

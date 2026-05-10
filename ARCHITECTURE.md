# System Architecture

## Overview

The Autonomous Coding Agent is a multi-layered system designed for autonomous code generation, review, and testing via Telegram.

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Interface                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Telegram Bot (tele_bot.py)                │
│  - Message parsing                                          │
│  - Response formatting                                      │
│  - User management                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    MCP Client Layer                          │
│  - Agent spawning                                           │
│  - Status polling                                           │
│  - Message coordination                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│ Coder Agent  │ │Reviewer Agnt│ │ Tester Agnt │
│ - Write code │ │ - Review    │ │ - Test code │
│ - Generate   │ │ - Quality   │ │ - Validate  │
└───────┬──────┘ └──────┬──────┘ └──────┬──────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Execution Layer                                │
├─────────────────────────────────────────────────────────────┤
│  FileExecutor          │  BashExecutor                      │
│  - Read files          │  - Execute commands               │
│  - Write files         │  - Validate commands              │
│  - Backup/Restore      │  - Timeout handling               │
│  - Path validation     │  - Error handling                 │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│   Memory     │ │   Error     │ │   Logging   │
│   System     │ │   Handling  │ │   System    │
└──────────────┘ └─────────────┘ └─────────────┘
```

## Layer Details

### 1. Telegram Interface Layer

**Components:**
- `tele_bot.py` - Main bot entry point
- Message parsing and formatting
- User session management

**Responsibilities:**
- Receive user messages
- Parse task descriptions
- Format and send responses
- Handle user interactions

### 2. MCP Client Layer

**Components:**
- `src/mcp_client.py` - MCP server client
- Agent spawning
- Status polling
- Message coordination

**Responsibilities:**
- Communicate with Ruflo MCP server
- Spawn agents (coder, reviewer, tester)
- Poll agent status
- Coordinate inter-agent messages

### 3. Agent Layer

**Components:**
- `src/agents/coder_agent.py` - Code generation
- `src/agents/reviewer_agent.py` - Code review
- `src/agents/tester_agent.py` - Test generation

**Responsibilities:**
- Receive tasks from MCP
- Process tasks
- Generate outputs
- Send results to next agent

**Communication:**
```
Coder → Reviewer → Tester → Telegram
  ↓        ↓         ↓
  └────────┴─────────┘
  (feedback loop)
```

### 4. Execution Layer

**Components:**
- `src/file_executor.py` - Safe file operations
- `src/bash_executor.py` - Safe command execution

**Responsibilities:**
- Validate paths (prevent directory traversal)
- Validate commands (whitelist)
- Execute operations safely
- Create backups before modifications
- Handle errors gracefully

**Security Features:**
- Path validation
- Command whitelist
- Dangerous pattern detection
- Timeout protection
- Backup/restore capability

### 5. Memory System

**Components:**
- `src/memory/agent_db.py` - Vector database
- `src/memory/task_embedder.py` - Task embeddings
- `src/memory/sona_learner.py` - Pattern learning

**Responsibilities:**
- Store task results with embeddings
- Search for similar past tasks
- Learn patterns from successful executions
- Apply learned patterns to new tasks

**Workflow:**
```
Task → Embed → Store → Search → Learn → Apply
```

### 6. Error Handling Layer

**Components:**
- `src/error_handler.py` - Centralized error handling
- `src/recovery/timeout_manager.py` - Timeout handling
- `src/recovery/rollback_manager.py` - File rollback
- `src/recovery/network_retry_manager.py` - Network retry
- `src/recovery/security_violation_manager.py` - Security

**Responsibilities:**
- Detect errors
- Determine recovery strategy
- Execute recovery
- Log errors
- Notify users

**Error Types:**
- Timeout → Kill agent
- File error → Rollback
- Network error → Retry
- Security error → Block agent

### 7. Logging System

**Components:**
- `src/logging/logger_factory.py` - Logger creation
- `src/logging/agent_action_logger.py` - Agent logging
- `src/logging/memory_operation_logger.py` - Memory logging
- `src/logging/security_event_logger.py` - Security logging
- `src/logging/log_analyzer.py` - Log analysis

**Responsibilities:**
- Create component-specific loggers
- Log all operations
- Store structured JSON logs
- Analyze and retrieve logs
- Generate reports

**Log Types:**
- Agent actions (spawn, kill, state change, tasks)
- Memory operations (store, search, learn, apply)
- Security events (violations, blocks, auth)
- Errors (timeout, file, network, security)

## Data Flow

### Simple Task Flow

```
1. User sends message to Telegram
   ↓
2. Bot parses task description
   ↓
3. MCP client spawns coder agent
   ↓
4. Coder agent generates code
   ↓
5. FileExecutor writes code to file
   ↓
6. MCP client spawns reviewer agent
   ↓
7. Reviewer agent reviews code
   ↓
8. MCP client spawns tester agent
   ↓
9. Tester agent generates tests
   ↓
10. BashExecutor runs tests
    ↓
11. Results stored in memory
    ↓
12. Bot sends response to Telegram
```

### Error Recovery Flow

```
1. Error detected during execution
   ↓
2. ErrorHandler determines error type
   ↓
3. Recovery strategy selected:
   - Timeout → TimeoutManager kills agent
   - File error → RollbackManager restores backup
   - Network error → NetworkRetryManager retries
   - Security error → SecurityViolationManager blocks agent
   ↓
4. Error logged to security.log
   ↓
5. User notified via Telegram
```

### Memory Learning Flow

```
1. Task completed successfully
   ↓
2. TaskEmbedder creates embedding
   ↓
3. AgentDB stores task + embedding
   ↓
4. SONALearner extracts pattern
   ↓
5. Pattern stored with success rate
   ↓
6. New task arrives
   ↓
7. Similar tasks searched
   ↓
8. Applicable patterns retrieved
   ↓
9. Patterns applied to new task
```

## Component Interactions

### Agent Coordination

```
SendMessageCoordinator
├── Message Queue (per agent)
├── Retry Logic (exponential backoff)
├── Audit Trail (message history)
└── Timeout Handling (5 minute default)
```

### File Operations

```
FileExecutor
├── Path Validation
│   ├── Prevent directory traversal
│   ├── Check permissions
│   └── Validate within project
├── Backup System
│   ├── Auto-backup before write
│   ├── Restore capability
│   └── Backup history
└── Operations
    ├── Read
    ├── Write
    ├── Edit
    ├── Delete
    └── List
```

### Bash Execution

```
BashExecutor
├── Command Validation
│   ├── Whitelist check
│   ├── Dangerous pattern detection
│   └── Injection prevention
├── Execution
│   ├── Async execution
│   ├── Timeout handling
│   └── Error capture
└── Results
    ├── Exit code
    ├── Stdout
    └── Stderr
```

## Scalability Considerations

### Horizontal Scaling

- Multiple bot instances (load balanced)
- Multiple MCP servers (round-robin)
- Distributed memory system (Redis)
- Distributed logging (ELK stack)

### Vertical Scaling

- Increase agent timeout for complex tasks
- Increase memory for large embeddings
- Increase disk for backups and logs
- Increase CPU for parallel processing

### Performance Optimization

- Cache embeddings
- Batch memory searches
- Async logging
- Connection pooling
- Rate limiting

## Security Architecture

### Defense Layers

```
Layer 1: Input Validation
├── Path validation
├── Command validation
└── Content validation

Layer 2: Execution Isolation
├── Timeout enforcement
├── Resource limits
└── Sandbox environment

Layer 3: Access Control
├── Agent blocking
├── Permission checking
└── Audit logging

Layer 4: Monitoring
├── Security event logging
├── Violation detection
└── Alert system
```

### Threat Model

**Threats:**
- Path traversal attacks
- Command injection attacks
- Secret exposure
- Resource exhaustion
- Unauthorized access

**Mitigations:**
- Path validation
- Command whitelist
- Secret detection
- Timeout enforcement
- Agent blocking

## Testing Architecture

### Test Pyramid

```
        ▲
       /│\
      / │ \  E2E Tests (15)
     /  │  \
    /───┼───\
   /    │    \ Integration Tests (28)
  /     │     \
 /──────┼──────\
/       │       \ Unit Tests (82)
─────────────────
```

### Correctness Properties

1. **Agent Isolation** - Agents don't interfere
2. **Memory Consistency** - Data integrity
3. **Code Safety** - No unauthorized access
4. **Command Safety** - Only safe commands
5. **Secret Protection** - No secret leaks
6. **Timeout Enforcement** - Resource limits
7. **Learning Effectiveness** - Pattern accuracy
8. **Error Recovery** - Graceful degradation

## Deployment Architecture

### Development

```
Local Machine
├── Telegram Bot
├── MCP Server
├── Agents
├── Memory System
└── Logging System
```

### Production

```
Load Balancer
├── Bot Instance 1
├── Bot Instance 2
└── Bot Instance N
    ↓
MCP Server Cluster
├── Server 1
├── Server 2
└── Server N
    ↓
Shared Services
├── Redis (memory)
├── PostgreSQL (logs)
└── S3 (backups)
```

## Future Enhancements

### Short Term
- Distributed memory system
- Multi-language support
- Advanced pattern learning
- Performance optimization

### Medium Term
- Web UI for monitoring
- Advanced analytics
- Custom agent types
- Plugin system

### Long Term
- Federated learning
- Multi-user collaboration
- Advanced security features
- Enterprise deployment

---

**Last Updated**: 2024
**Version**: 1.0.0

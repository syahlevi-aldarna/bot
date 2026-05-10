# Autonomous Coding Agent via Telegram

## Overview
Build an autonomous AI coding agent that runs via Telegram, powered by Ruflo MCP server. The agent can read/write code, execute commands, and coordinate with other agents (coder, reviewer, tester) to complete coding tasks autonomously.

## User Stories

### US-1: User sends coding task via Telegram
**As a** developer  
**I want to** send a coding task via Telegram  
**So that** the agent can start working on it autonomously

**Acceptance Criteria:**
- User sends message to Telegram bot (e.g., "create a function that validates email")
- Bot acknowledges receipt and shows "Agent starting..."
- Agent begins working on the task
- User receives status updates via Telegram

### US-2: Agent executes code autonomously
**As a** developer  
**I want the** agent to read/write/execute code without asking permission  
**So that** it can complete tasks end-to-end

**Acceptance Criteria:**
- Agent can read files from the project
- Agent can write/edit files
- Agent can run bash commands (npm, git, etc.)
- Agent can execute tests
- All operations are logged and reported back to Telegram

### US-3: Agent coordinates with other agents
**As a** developer  
**I want** coder, reviewer, and tester agents to work together  
**So that** code quality is maintained

**Acceptance Criteria:**
- Coder agent writes the code
- Reviewer agent reviews the code
- Tester agent writes and runs tests
- Agents communicate via Ruflo's SendMessage pattern
- Final result is reported to user via Telegram

### US-4: Agent remembers context across sessions
**As a** developer  
**I want** the agent to remember previous tasks and context  
**So that** it can build on past work

**Acceptance Criteria:**
- Agent stores task history in AgentDB
- Agent can retrieve past solutions via HNSW vector search
- Agent learns from successful patterns
- Memory persists across Telegram sessions

### US-5: User monitors agent progress
**As a** developer  
**I want to** see real-time progress of the agent  
**So that** I know what's happening

**Acceptance Criteria:**
- Telegram shows step-by-step progress
- User can see which agent is working (coder/reviewer/tester)
- User can see code changes being made
- User can see test results
- User can cancel/interrupt the agent

## Functional Requirements

### FR-1: Telegram Integration
- Bot receives messages from owner (OWNER_ID from .env)
- Bot triggers Ruflo MCP server
- Bot receives agent responses and sends back to Telegram
- Bot handles long responses (split into multiple messages if >4096 chars)
- Bot shows typing indicator while agent is working

### FR-2: Ruflo MCP Server Integration
- MCP server runs as background process
- Exposes agent_spawn, agent_status, memory_store, memory_search tools
- Routes tasks to appropriate agents (coder, reviewer, tester)
- Manages agent lifecycle (spawn, monitor, cleanup)

### FR-3: Code Execution
- Agent can read files (with path validation)
- Agent can write/edit files (with backup)
- Agent can run bash commands (npm, git, python, etc.)
- Agent can execute tests (npm test, pytest, etc.)
- All file operations logged to .claude-flow/logs/

### FR-4: Agent Coordination
- Coder agent: writes code based on requirements
- Reviewer agent: reviews code for quality/security
- Tester agent: writes tests and validates
- Agents communicate via SendMessage pattern
- Agents share memory namespace for context

### FR-5: Memory & Learning
- Task history stored in AgentDB
- Solutions indexed via HNSW for fast retrieval
- Agent learns from successful patterns (SONA)
- Memory persists in .claude-flow/data/

### FR-6: Error Handling
- Agent catches and reports errors to user
- Failed tasks don't corrupt state
- User can retry failed tasks
- Errors logged with full context

## Non-Functional Requirements

### NFR-1: Performance
- Agent responds within 60 seconds for simple tasks
- Agent can handle 3+ concurrent tasks
- Memory search completes in <100ms

### NFR-2: Security
- Only OWNER_ID can trigger agent
- File operations restricted to project directory
- Bash commands validated (no rm -rf /, etc.)
- Secrets (.env) never logged or sent to Telegram
- AIDefence scans all code for injection attacks

### NFR-3: Reliability
- Agent recovers from network failures
- Agent doesn't lose state on crash
- Memory is persisted and recoverable
- Agents timeout after 5 minutes of inactivity

### NFR-4: Observability
- All agent actions logged to .claude-flow/logs/
- Agent status visible via Telegram
- Memory usage tracked
- Token usage tracked (via ruflo-cost-tracker)

## Constraints

- Must use existing Ruflo v3.7.0-alpha.20
- Must use existing Telegram bot (tele_bot.py)
- Must use existing .env configuration
- Must not modify package.json (only use installed deps)
- Must run on Linux (current OS)
- Must respect 60-second timeout for Telegram responses

## Out of Scope

- Web dashboard (use Telegram only)
- Advanced federation (single machine only)
- Custom LLM training
- Production deployment
- Multi-user support (owner only)

## Success Metrics

1. Agent successfully completes 5 different coding tasks
2. Agent coordinates between coder/reviewer/tester
3. Memory retrieval works (agent recalls past solutions)
4. All operations logged and traceable
5. Telegram user gets real-time updates
6. No security issues (AIDefence passes all scans)

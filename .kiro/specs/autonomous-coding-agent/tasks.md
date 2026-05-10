# Implementation Tasks: Autonomous Coding Agent

## Phase 1: MCP Server & Agent Coordination

- [x] 1.1 Start Ruflo MCP server and verify it's running
- [x] 1.2 Create agent_spawn wrapper function
- [x] 1.3 Create agent_status polling function
- [x] 1.4 Implement SendMessage coordination pattern
- [x] 1.5 Test agent spawn and status polling

## Phase 2: Telegram Bot Integration

- [x] 2.1 Update tele_bot.py to use MCP server instead of `npx ruflo ask`
- [x] 2.2 Implement agent_spawn call from Telegram message
- [x] 2.3 Implement status polling and Telegram updates
- [x] 2.4 Handle long responses (split >4096 chars)
- [x] 2.5 Test Telegram bot with MCP server

## Phase 3: Code Execution Layer

- [x] 3.1 Create file validation utility (path, permissions)
- [x] 3.2 Create bash command validation (whitelist)
- [x] 3.3 Implement safe file read operation
- [x] 3.4 Implement safe file write operation (with backup)
- [x] 3.5 Implement bash execution with logging
- [x] 3.6 Test all code execution operations

## Phase 4: Agent Coordination

- [ ] 4.1 Create coder agent template
- [ ] 4.2 Create reviewer agent template
- [ ] 4.3 Create tester agent template
- [ ] 4.4 Implement SendMessage between agents
- [ ] 4.5 Test full coordination pipeline (coder → reviewer → tester)

## Phase 5: Memory & Learning

- [ ] 5.1 Implement memory_store for task results
- [ ] 5.2 Implement memory_search via HNSW
- [ ] 5.3 Create task embedding function
- [ ] 5.4 Implement SONA pattern learning
- [ ] 5.5 Test memory retrieval and learning

## Phase 6: Error Handling & Recovery

- [ ] 6.1 Implement agent timeout handling
- [ ] 6.2 Implement file operation rollback
- [ ] 6.3 Implement network error retry logic
- [ ] 6.4 Implement security violation blocking
- [ ] 6.5 Test all error scenarios

## Phase 7: Logging & Observability

- [ ] 7.1 Create structured logging to .claude-flow/logs/
- [ ] 7.2 Implement agent action logging
- [ ] 7.3 Implement memory operation logging
- [ ] 7.4 Implement security event logging
- [ ] 7.5 Test log retrieval and analysis

## Phase 8: End-to-End Testing

- [ ] 8.1 Test simple coding task (create function)
- [ ] 8.2 Test code review workflow
- [ ] 8.3 Test test generation and execution
- [ ] 8.4 Test memory learning from past tasks
- [ ] 8.5 Test error recovery scenarios
- [ ] 8.6 Test security validations (AIDefence)

## Phase 9: Documentation & Deployment

- [ ] 9.1 Document MCP server setup
- [ ] 9.2 Document agent coordination patterns
- [ ] 9.3 Document code execution safety
- [ ] 9.4 Create startup script
- [ ] 9.5 Create troubleshooting guide

---

## Correctness Properties (Property-Based Testing)

### Property 1: Agent Isolation
**Spec:** Each agent operates independently without corrupting others' state
- Given: Multiple agents running concurrently
- When: One agent fails
- Then: Other agents continue unaffected

### Property 2: Memory Consistency
**Spec:** Stored tasks can always be retrieved with same content
- Given: Task stored in AgentDB
- When: Task is searched via HNSW
- Then: Retrieved task matches original

### Property 3: Code Safety
**Spec:** No file operations outside project directory
- Given: File operation request
- When: Path validation occurs
- Then: Only paths within project are allowed

### Property 4: Command Safety
**Spec:** Only whitelisted bash commands can execute
- Given: Bash command request
- When: Command validation occurs
- Then: Only whitelisted commands execute

### Property 5: Coordination Correctness
**Spec:** Agents execute in correct order (coder → reviewer → tester)
- Given: Task sent to coder agent
- When: Agents coordinate via SendMessage
- Then: Reviewer receives from coder, tester receives from reviewer

### Property 6: Secret Protection
**Spec:** .env secrets never appear in logs or Telegram
- Given: Agent executes task
- When: Logs are written
- Then: No secrets appear in logs or Telegram messages

### Property 7: Timeout Enforcement
**Spec:** Agents timeout after 5 minutes
- Given: Agent running for >5 minutes
- When: Timeout check occurs
- Then: Agent is killed and user notified

### Property 8: Learning Effectiveness
**Spec:** Agent retrieves similar past solutions for new tasks
- Given: Similar task to past task
- When: Memory search occurs
- Then: Past solution is retrieved with high similarity score

# Reviewer Agent Template

## Overview

The Reviewer Agent is responsible for reviewing code changes produced by the Coder Agent. It performs comprehensive code reviews checking for security vulnerabilities, code quality issues, performance problems, and test coverage.

## Architecture

```
Coder Agent
    ↓
    SendMessage (code changes)
    ↓
Reviewer Agent
    ├─ Security Review
    ├─ Quality Review
    ├─ Performance Review
    └─ Testing Review
    ↓
    SendMessage (review results)
    ↓
Tester Agent
```

## Responsibilities

### 1. Receive Code Changes
- Listen for `SendMessage` from the Coder Agent
- Extract file changes and code diff
- Log incoming code for audit trail

### 2. Perform Code Review
The reviewer checks code across four dimensions:

#### Security (40% weight)
- No hardcoded secrets (passwords, API keys, tokens)
- No SQL injection vulnerabilities
- No XSS vulnerabilities
- Proper input validation
- Secure error handling
- No use of dangerous functions (eval, exec)

#### Quality (30% weight)
- Code readability and clarity
- Adherence to project style guide
- No code duplication
- Proper naming conventions
- Appropriate abstractions and design patterns

#### Performance (20% weight)
- No N+1 query problems
- Efficient algorithms
- Proper caching strategies
- Memory efficiency

#### Testing (10% weight)
- Adequate test coverage
- Meaningful test cases
- Edge cases covered

### 3. Generate Review Report
- Categorize issues by severity (critical, high, medium, low)
- Provide actionable suggestions
- Identify approved files
- Identify files needing changes

### 4. Send Results to Tester
- Send review status (approved, needs_changes, rejected)
- Include detailed issues and suggestions
- Provide context for tester agent

## Communication Protocol

### Receiving from Coder Agent

```javascript
{
  "from": "coder",
  "files_changed": ["src/file1.js", "src/file2.js"],
  "code_diff": "...",
  "task_description": "Create email validation function"
}
```

### Sending to Tester Agent

```javascript
{
  "to": "tester",
  "from": "reviewer",
  "content": {
    "review_status": "approved|needs_changes|rejected",
    "issues": [
      {
        "file": "src/file.js",
        "line": 42,
        "severity": "critical|high|medium|low",
        "category": "security|quality|performance|testing",
        "message": "Issue description",
        "suggestion": "How to fix it"
      }
    ],
    "suggestions": ["Overall suggestion 1", "Overall suggestion 2"],
    "approved_files": ["src/file1.js"],
    "files_needing_changes": ["src/file2.js"],
    "timestamp": "2024-01-15T10:30:00Z",
    "reviewer_notes": "Additional context"
  }
}
```

## Review Status Meanings

### Approved
- No critical or high-severity issues
- Code is ready for testing
- May have minor suggestions

### Needs Changes
- High-severity issues found
- Code should be fixed before testing
- Coder agent should address issues

### Rejected
- Critical security issues found
- Code cannot proceed to testing
- Requires significant changes

## Implementation Files

### JavaScript Version
- **File**: `.claude-flow/agents/reviewer-agent.js`
- **Framework**: Ruflo Agent
- **Use**: For Ruflo MCP server integration

### Python Version
- **File**: `.claude-flow/agents/reviewer_agent.py`
- **Framework**: Async Python
- **Use**: For standalone testing and integration with Python components

## Usage

### JavaScript (Ruflo)

```javascript
const reviewerAgent = require('./.claude-flow/agents/reviewer-agent.js');

// Agent runs automatically when spawned by Ruflo
// Receives messages from coder agent
// Sends messages to tester agent
```

### Python

```python
from reviewer_agent import ReviewerAgent
import asyncio

async def main():
    reviewer = ReviewerAgent()
    
    code_data = {
        'from': 'coder',
        'files_changed': ['src/app.js'],
        'code_diff': '...',
        'task_description': 'Create user authentication'
    }
    
    result = await reviewer.run(code_data)
    print(f"Review Status: {result.review_status}")
```

## Configuration

### Review Criteria Weights

```python
{
    'security': 0.4,      # 40% of review
    'quality': 0.3,       # 30% of review
    'performance': 0.2,   # 20% of review
    'testing': 0.1        # 10% of review
}
```

### Severity Levels

- **Critical**: Must fix before merge (blocks testing)
- **High**: Should fix before merge (needs changes)
- **Medium**: Consider fixing (approved but noted)
- **Low**: Nice to have (approved)

### Timeout Configuration

- Default timeout: 5 minutes (300 seconds)
- Max retries: 3
- Retry delay: 1 second

## Logging

All reviewer agent activities are logged to:
- **File**: `.claude-flow/logs/reviewer-agent.log`
- **Console**: Standard output
- **Level**: INFO (configurable)

Log entries include:
- Code reception
- Review progress
- Issues found
- Review completion
- Messages sent to tester

## Security Checks

### Hardcoded Secrets
Detects patterns like:
- `password=`
- `api_key=`
- `secret=`
- `token=`

**Suggestion**: Move to environment variables

### SQL Injection
Detects string concatenation in queries:
- `query("SELECT * FROM users WHERE id = '" + id + "'")`

**Suggestion**: Use parameterized queries

### Dangerous Functions
Detects use of:
- `eval()`
- `exec()`
- `Function()`

**Suggestion**: Use safer alternatives

### Console Logging
Detects `console.log()` in production code

**Suggestion**: Use proper logging framework

## Quality Checks

### Code Duplication
Identifies repeated code patterns

**Suggestion**: Extract to shared function

### Naming Conventions
Checks for meaningful variable/function names

**Suggestion**: Use descriptive names

### TODO Comments
Identifies unfinished work

**Suggestion**: Complete or remove before merge

## Performance Checks

### Nested Loops
Detects multiple nested loops

**Suggestion**: Optimize algorithm complexity

### N+1 Queries
Identifies potential database query problems

**Suggestion**: Use batch queries or joins

## Integration with Coordination Pipeline

### Phase 4: Agent Coordination

The reviewer agent is part of the full coordination pipeline:

```
Task from Telegram
    ↓
Coder Agent (writes code)
    ↓
Reviewer Agent (reviews code) ← YOU ARE HERE
    ↓
Tester Agent (writes and runs tests)
    ↓
Result back to Telegram
```

### SendMessage Pattern

The reviewer agent uses Ruflo's `SendMessage` pattern for inter-agent communication:

1. **Receives** from Coder Agent
   - Waits for message with code changes
   - Extracts file list and diff

2. **Processes** code review
   - Runs all security, quality, performance checks
   - Generates issues and suggestions

3. **Sends** to Tester Agent
   - Forwards review results
   - Includes approval status
   - Provides context for testing

## Error Handling

### Timeout
If review takes longer than 5 minutes:
- Agent is terminated
- Error logged
- Message sent to Telegram

### Invalid Input
If code data is malformed:
- Error logged
- Review status set to 'rejected'
- Coder agent notified

### Network Errors
If SendMessage fails:
- Retry up to 3 times
- Exponential backoff
- Error logged

## Testing the Reviewer Agent

### Unit Tests
```bash
# Test security checks
python -m pytest tests/test_reviewer_security.py

# Test quality checks
python -m pytest tests/test_reviewer_quality.py

# Test performance checks
python -m pytest tests/test_reviewer_performance.py
```

### Integration Tests
```bash
# Test full review pipeline
python -m pytest tests/test_reviewer_integration.py

# Test SendMessage coordination
python -m pytest tests/test_reviewer_coordination.py
```

### Manual Testing
```python
# Run example
python .claude-flow/agents/reviewer_agent.py
```

## Next Steps

After the reviewer agent is created, the next task is:
- **4.3**: Create tester agent template
- **4.4**: Implement SendMessage between agents
- **4.5**: Test full coordination pipeline

## Related Tasks

- **4.1**: Create coder agent template (completed)
- **4.2**: Create reviewer agent template (this task)
- **4.3**: Create tester agent template (next)
- **4.4**: Implement SendMessage between agents
- **4.5**: Test full coordination pipeline

## References

- Design Document: `.kiro/specs/autonomous-coding-agent/design.md`
- Requirements: `.kiro/specs/autonomous-coding-agent/requirements.md`
- Ruflo Documentation: https://ruflo.dev/docs
- SendMessage Pattern: https://ruflo.dev/docs/coordination/send-message

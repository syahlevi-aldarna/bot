/**
 * Tests for MCP Client
 */

const MCPClient = require('../src/mcp-client');

describe('MCPClient', () => {
  let client;

  beforeEach(() => {
    client = new MCPClient({ port: 3000 });
  });

  afterEach(async () => {
    if (client.isConnected) {
      await client.disconnect();
    }
  });

  describe('Connection', () => {
    test('should connect to MCP server', async () => {
      await client.connect();
      expect(client.isConnected).toBe(true);
    });

    test('should emit connected event', async () => {
      const connectedPromise = new Promise((resolve) => {
        client.on('connected', resolve);
      });

      await client.connect();
      await connectedPromise;
    });
  });

  describe('Agent Spawning', () => {
    beforeEach(async () => {
      await client.connect();
    });

    test('should spawn a coder agent', async () => {
      const agentId = await client.spawnAgent({
        type: 'coder',
        task: 'Create a function that validates email',
        namespace: 'test',
      });

      expect(agentId).toBeDefined();
      expect(agentId).toMatch(/^agent-/);
    });

    test('should spawn a reviewer agent', async () => {
      const agentId = await client.spawnAgent({
        type: 'reviewer',
        task: 'Review the email validator code',
        namespace: 'test',
      });

      expect(agentId).toBeDefined();
    });

    test('should spawn a tester agent', async () => {
      const agentId = await client.spawnAgent({
        type: 'tester',
        task: 'Write tests for email validator',
        namespace: 'test',
      });

      expect(agentId).toBeDefined();
    });

    test('should throw error if type is missing', async () => {
      await expect(
        client.spawnAgent({
          task: 'Some task',
        })
      ).rejects.toThrow('Agent type and task are required');
    });

    test('should throw error if task is missing', async () => {
      await expect(
        client.spawnAgent({
          type: 'coder',
        })
      ).rejects.toThrow('Agent type and task are required');
    });

    test('should emit agent:spawned event', async () => {
      const spawnedPromise = new Promise((resolve) => {
        client.on('agent:spawned', resolve);
      });

      await client.spawnAgent({
        type: 'coder',
        task: 'Test task',
      });

      const event = await spawnedPromise;
      expect(event.type).toBe('coder');
      expect(event.task).toBe('Test task');
    });
  });

  describe('Agent Status', () => {
    let agentId;

    beforeEach(async () => {
      await client.connect();
      agentId = await client.spawnAgent({
        type: 'coder',
        task: 'Test task',
      });
    });

    test('should get agent status', async () => {
      const status = await client.getAgentStatus(agentId);

      expect(status.id).toBe(agentId);
      expect(status.type).toBe('coder');
      expect(status.task).toBe('Test task');
    });

    test('should throw error for non-existent agent', async () => {
      await expect(client.getAgentStatus('non-existent')).rejects.toThrow(
        'Agent non-existent not found'
      );
    });

    test('should update agent status', async () => {
      await client.updateAgentStatus(agentId, 'running', {
        output: 'Agent is running',
      });

      const status = await client.getAgentStatus(agentId);
      expect(status.status).toBe('running');
      expect(status.output).toBe('Agent is running');
    });

    test('should list all agents', async () => {
      const agent2Id = await client.spawnAgent({
        type: 'reviewer',
        task: 'Review task',
      });

      const agents = await client.listAgents();
      expect(agents.length).toBe(2);
      expect(agents.map((a) => a.id)).toContain(agentId);
      expect(agents.map((a) => a.id)).toContain(agent2Id);
    });
  });

  describe('Memory Operations', () => {
    beforeEach(async () => {
      await client.connect();
    });

    test('should store data in memory', async () => {
      const result = await client.memoryStore({
        namespace: 'test',
        key: 'email-validator',
        value: { pattern: /^[^@]+@[^@]+$/ },
      });

      expect(result.stored).toBe(true);
      expect(result.key).toBe('email-validator');
    });

    test('should throw error if key is missing', async () => {
      await expect(
        client.memoryStore({
          namespace: 'test',
          value: 'some value',
        })
      ).rejects.toThrow('Key and value are required');
    });

    test('should search memory', async () => {
      const result = await client.memorySearch({
        namespace: 'test',
        query: 'email validator',
        limit: 5,
      });

      expect(result.namespace).toBe('test');
      expect(result.query).toBe('email validator');
      expect(Array.isArray(result.results)).toBe(true);
    });

    test('should throw error if query is missing', async () => {
      await expect(
        client.memorySearch({
          namespace: 'test',
        })
      ).rejects.toThrow('Query is required');
    });
  });

  describe('SendMessage Pattern', () => {
    beforeEach(async () => {
      await client.connect();
    });

    test('should send message between agents', async () => {
      const result = await client.sendMessage({
        from: 'agent-1',
        to: 'reviewer',
        message: 'Here is the code I wrote',
      });

      expect(result.sent).toBe(true);
      expect(result.from).toBe('agent-1');
      expect(result.to).toBe('reviewer');
    });

    test('should emit message:sent event', async () => {
      const messagePromise = new Promise((resolve) => {
        client.on('message:sent', resolve);
      });

      await client.sendMessage({
        from: 'agent-1',
        to: 'reviewer',
        message: 'Test message',
      });

      const event = await messagePromise;
      expect(event.from).toBe('agent-1');
      expect(event.to).toBe('reviewer');
    });
  });

  describe('Agent Lifecycle', () => {
    let agentId;

    beforeEach(async () => {
      await client.connect();
      agentId = await client.spawnAgent({
        type: 'coder',
        task: 'Test task',
      });
    });

    test('should kill an agent', async () => {
      await client.killAgent(agentId);

      // Wait for cleanup
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const agents = await client.listAgents();
      expect(agents.map((a) => a.id)).not.toContain(agentId);
    });

    test('should emit agent:killed event', async () => {
      const killedPromise = new Promise((resolve) => {
        client.on('agent:killed', resolve);
      });

      await client.killAgent(agentId);

      const event = await killedPromise;
      expect(event.agentId).toBe(agentId);
    });
  });
});

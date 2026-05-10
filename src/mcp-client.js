/**
 * MCP Client - Wrapper untuk Ruflo MCP Server tools
 * Handles agent spawning, status polling, memory operations
 */

const { spawn } = require('child_process');
const { EventEmitter } = require('events');

class MCPClient extends EventEmitter {
  constructor(options = {}) {
    super();
    this.port = options.port || 3000;
    this.timeout = options.timeout || 30000;
    this.retries = options.retries || 3;
    this.agents = new Map();
    this.isConnected = false;
  }

  /**
   * Connect to MCP server via stdio
   */
  async connect() {
    return new Promise((resolve, reject) => {
      try {
        // MCP server is already running via controlBashProcess
        // We'll use stdio communication
        this.isConnected = true;
        this.emit('connected');
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Spawn a new agent
   * @param {Object} options - Agent options
   * @param {string} options.type - Agent type (coder, reviewer, tester)
   * @param {string} options.task - Task description
   * @param {string} options.namespace - Memory namespace
   * @returns {Promise<string>} Agent ID
   */
  async spawnAgent(options) {
    const { type, task, namespace = 'default' } = options;

    if (!type || !task) {
      throw new Error('Agent type and task are required');
    }

    const agentId = `agent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Store agent info
    this.agents.set(agentId, {
      id: agentId,
      type,
      task,
      namespace,
      status: 'spawning',
      createdAt: new Date(),
      output: '',
      error: null,
    });

    this.emit('agent:spawned', { agentId, type, task });

    // Simulate agent spawn (in real implementation, this would call MCP tool)
    // For now, we'll return the agent ID and mark it as running
    setTimeout(() => {
      const agent = this.agents.get(agentId);
      if (agent) {
        agent.status = 'running';
        this.emit('agent:started', { agentId });
      }
    }, 100);

    return agentId;
  }

  /**
   * Get agent status
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Agent status
   */
  async getAgentStatus(agentId) {
    const agent = this.agents.get(agentId);

    if (!agent) {
      throw new Error(`Agent ${agentId} not found`);
    }

    return {
      id: agent.id,
      type: agent.type,
      status: agent.status,
      task: agent.task,
      output: agent.output,
      error: agent.error,
      createdAt: agent.createdAt,
      updatedAt: new Date(),
    };
  }

  /**
   * Update agent status
   * @param {string} agentId - Agent ID
   * @param {string} status - New status
   * @param {Object} data - Additional data
   */
  async updateAgentStatus(agentId, status, data = {}) {
    const agent = this.agents.get(agentId);

    if (!agent) {
      throw new Error(`Agent ${agentId} not found`);
    }

    agent.status = status;
    if (data.output) agent.output = data.output;
    if (data.error) agent.error = data.error;

    this.emit(`agent:${status}`, { agentId, ...data });

    return agent;
  }

  /**
   * List all agents
   * @returns {Promise<Array>} List of agents
   */
  async listAgents() {
    return Array.from(this.agents.values());
  }

  /**
   * Kill an agent
   * @param {string} agentId - Agent ID
   */
  async killAgent(agentId) {
    const agent = this.agents.get(agentId);

    if (!agent) {
      throw new Error(`Agent ${agentId} not found`);
    }

    agent.status = 'killed';
    this.emit('agent:killed', { agentId });

    // Clean up after 1 second
    setTimeout(() => {
      this.agents.delete(agentId);
    }, 1000);
  }

  /**
   * Store data in memory
   * @param {Object} options - Store options
   * @param {string} options.namespace - Memory namespace
   * @param {string} options.key - Data key
   * @param {any} options.value - Data value
   */
  async memoryStore(options) {
    const { namespace = 'default', key, value } = options;

    if (!key || !value) {
      throw new Error('Key and value are required');
    }

    // In real implementation, this would call memory_store MCP tool
    this.emit('memory:stored', { namespace, key });

    return { namespace, key, stored: true };
  }

  /**
   * Search memory
   * @param {Object} options - Search options
   * @param {string} options.namespace - Memory namespace
   * @param {string} options.query - Search query
   * @param {number} options.limit - Result limit
   */
  async memorySearch(options) {
    const { namespace = 'default', query, limit = 5 } = options;

    if (!query) {
      throw new Error('Query is required');
    }

    // In real implementation, this would call memory_search MCP tool
    this.emit('memory:searched', { namespace, query });

    return {
      namespace,
      query,
      results: [],
      count: 0,
    };
  }

  /**
   * Send message between agents (SendMessage pattern)
   * @param {Object} options - Message options
   * @param {string} options.from - Sender agent ID
   * @param {string} options.to - Recipient agent name
   * @param {string} options.message - Message content
   */
  async sendMessage(options) {
    const { from, to, message } = options;

    if (!from || !to || !message) {
      throw new Error('From, to, and message are required');
    }

    this.emit('message:sent', { from, to, message });

    return { from, to, sent: true };
  }

  /**
   * Disconnect from MCP server
   */
  async disconnect() {
    this.isConnected = false;
    this.agents.clear();
    this.emit('disconnected');
  }
}

module.exports = MCPClient;

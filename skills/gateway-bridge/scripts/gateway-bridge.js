#!/usr/bin/env node
/**
 * Gateway Bridge - 允许子代理与同一 Gateway 下的其他 Agent 通信
 */

const { sessions_list, sessions_send } = require('openclaw');

class GatewayBridge {
  constructor() {
    this.gatewayUrl = process.env.OPENCLAW_GATEWAY_URL;
    this.gatewayToken = process.env.OPENCLAW_GATEWAY_TOKEN;
  }

  /**
   * 列出当前 Gateway 下的所有会话/Agent
   */
  async listAgents(options = {}) {
    const result = await sessions_list({
      limit: options.limit || 50,
      kinds: options.kinds,
      activeMinutes: options.activeMinutes
    });
    return result.sessions || [];
  }

  /**
   * 向指定 Agent/会话发送消息
   */
  async sendMessage(target, message, options = {}) {
    // 支持多种目标格式
    let sessionKey, label;
    
    if (typeof target === 'string') {
      // 尝试作为 label 或 sessionKey
      if (target.includes(':')) {
        sessionKey = target;
      } else {
        label = target;
      }
    } else if (typeof target === 'object') {
      sessionKey = target.sessionKey;
      label = target.label;
    }

    const params = {
      message,
      timeoutSeconds: options.timeoutSeconds || 30
    };

    if (sessionKey) params.sessionKey = sessionKey;
    if (label) params.label = label;

    return await sessions_send(params);
  }

  /**
   * 广播消息给多个 Agent
   */
  async broadcastMessage(targets, message, options = {}) {
    const results = [];
    for (const target of targets) {
      try {
        const result = await this.sendMessage(target, message, options);
        results.push({ target, success: true, result });
      } catch (error) {
        results.push({ target, success: false, error: error.message });
      }
    }
    return results;
  }

  /**
   * 查找特定标签的 Agent
   */
  async findAgentByLabel(label) {
    const agents = await this.listAgents();
    return agents.find(a => a.label === label || a.key?.includes(label));
  }
}

// CLI 支持
if (require.main === module) {
  const bridge = new GatewayBridge();
  const command = process.argv[2];

  (async () => {
    switch (command) {
      case 'list':
        const agents = await bridge.listAgents();
        console.log(JSON.stringify(agents, null, 2));
        break;
      
      case 'send':
        const target = process.argv[3];
        const message = process.argv[4];
        if (!target || !message) {
          console.error('Usage: gateway-bridge send <target> <message>');
          process.exit(1);
        }
        const result = await bridge.sendMessage(target, message);
        console.log(JSON.stringify(result, null, 2));
        break;
      
      default:
        console.log(`
Gateway Bridge - 与其他 Agent 通信

用法:
  gateway-bridge list              # 列出所有 Agent
  gateway-bridge send <目标> <消息> # 发送消息

示例:
  gateway-bridge list
  gateway-bridge send ai_scientist "你好，请帮我分析这个数据"
`);
    }
  })();
}

module.exports = { GatewayBridge };

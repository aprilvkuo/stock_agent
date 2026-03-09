# Gateway Bridge Skill

允许子代理通过同一 Gateway 与其他 Agent 进行通信和协作。

## 功能

- 列出当前 Gateway 下的所有会话/Agent
- 向指定 Agent 发送消息
- 检查消息状态

## 使用方式

### 在子代理中调用

```javascript
// 列出所有可用 Agent
const agents = await gatewayBridge.listAgents();

// 向指定 Agent 发送消息
await gatewayBridge.sendMessage({
  targetAgent: "agent-label-or-id",
  message: "你好，我是另一个 Agent"
});
```

### 环境变量

子代理会自动继承主会话的 Gateway 连接信息：
- `OPENCLAW_GATEWAY_URL`
- `OPENCLAW_GATEWAY_TOKEN`

## 权限

需要以下权限：
- `sessions_list` - 列总会话
- `sessions_send` - 发送消息

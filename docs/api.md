# API 文档

本文档详细说明 GomokuAgent 后端提供的所有 API 接口。

## 基础信息

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **API 文档**: `http://localhost:8000/docs` (Swagger UI)

## 接口列表

### 1. 获取棋盘状态

获取当前棋盘的完整状态。

**请求**

```http
GET /board
```

**响应**

```json
{
    "board": [
        [0, 0, 0, ...],
        [0, 1, 0, ...],
        ...
    ],
    "winner": null,
    "game_over": false,
    "winning_line": [],
    "last_move": [7, 7]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| board | array[15][15] | 棋盘状态 (0=空, 1=黑, 2=白) |
| winner | string/null | 获胜方 ("玩家获胜", "AI获胜", "平局", null) |
| game_over | boolean | 游戏是否结束 |
| winning_line | array | 获胜连线坐标 |
| last_move | array/null | 最后一步落子 [x, y] |

### 2. 玩家落子

玩家落子，AI 自动响应。

**请求**

```http
POST /move
Content-Type: application/json

{
    "x": 7,
    "y": 7
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| x | int | 是 | 行坐标 (0-14) |
| y | int | 是 | 列坐标 (0-14) |

**响应**

```json
{
    "board": [...],
    "winner": null,
    "game_over": false,
    "winning_line": [],
    "last_move": [8, 8],
    "message": {
        "move": [8, 8],
        "type": "mcts",
        "simulations": 300,
        "message": "MCTS落子 (8,8)",
        "strategy": {
            "style": "attack",
            "priority": "create_threat",
            "reason": "开局阶段，占据中心优势"
        },
        "observation": {
            "phase": "opening",
            "situation": "advantage"
        }
    }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| board | array | 更新后的棋盘 |
| winner | string/null | 获胜方 |
| game_over | boolean | 游戏是否结束 |
| winning_line | array | 获胜连线 |
| last_move | array | AI 落子位置 |
| message | object/string | AI 决策信息或状态消息 |

**错误响应**

```json
{
    "board": [...],
    "winner": null,
    "game_over": false,
    "winning_line": [],
    "last_move": null,
    "message": "非法位置"
}
```

### 3. 重置游戏

重置游戏到初始状态。

**请求**

```http
POST /reset
```

**响应**

```json
{
    "board": [
        [0, 0, 0, ...],
        ...
    ],
    "winner": null,
    "game_over": false,
    "winning_line": [],
    "last_move": null
}
```

### 4. 与 AI 对话

向 AI 提问，了解其落子思路。

**请求**

```http
POST /chat
Content-Type: application/json

{
    "message": "你为什么下在(8,8)？"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | 是 | 用户的问题 |

**响应**

```json
{
    "response": "我选择(8,8)是因为...",
    "strategy": {
        "style": "attack",
        "priority": "create_threat",
        "reason": "..."
    },
    "observation": {
        "phase": "opening",
        "situation": "advantage"
    }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| response | string | AI 的回答 |
| strategy | object | 当前策略 |
| observation | object | 当前局势分析 |

### 5. 获取历史记忆

获取历史棋局和经验教训。

**请求**

```http
GET /memory
```

**响应**

```json
{
    "games": [
        {
            "time": "2024-01-15 14:30:00",
            "winner": "AI获胜",
            "history": [
                {"x": 7, "y": 7, "player": 1},
                {"x": 8, "y": 8, "player": 2}
            ],
            "reflection": {
                "mistake": "中期防守过于被动",
                "good_move": "开局占据中心",
                "lesson": "下局应更积极进攻"
            }
        }
    ],
    "lessons": [
        "下局应更积极进攻",
        "注意阻挡对手的活三"
    ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| games | array | 最近 10 局棋局 |
| lessons | array | 最近 5 条经验教训 |

### 6. 获取 Agent 状态

获取 Agent 的运行状态信息。

**请求**

```http
GET /agent/status
```

**响应**

```json
{
    "memory_count": 15,
    "recent_lessons": [
        "下局应更积极进攻",
        "注意阻挡对手的活三",
        "开局占据中心很重要"
    ],
    "last_decision": {
        "strategy": {
            "style": "attack",
            "priority": "create_threat"
        },
        "observation": {
            "phase": "opening",
            "situation": "advantage"
        },
        "result": {
            "move": [8, 8],
            "type": "mcts"
        }
    }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| memory_count | int | 记忆中的棋局数量 |
| recent_lessons | array | 最近的经验教训 |
| last_decision | object | 最近一次 AI 决策信息 |

### 7. 手动触发复盘

对最近一局进行复盘分析。

**请求**

```http
POST /reflect
```

**响应**

```json
{
    "mistake": "中期防守过于被动，让对手形成活三",
    "good_move": "开局占据中心，建立了优势",
    "lesson": "下局应更积极进攻，注意阻挡对手的活三"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| mistake | string | 本局最大问题 |
| good_move | string | 做得好的地方 |
| lesson | string | 下次应该注意什么 |

**错误响应**

```json
{
    "error": "没有可复盘的棋局"
}
```

## 错误处理

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 422 | 请求体验证失败 |
| 500 | 服务器内部错误 |

### 错误响应格式

```json
{
    "detail": "错误描述"
}
```

## 使用示例

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 获取棋盘状态
response = requests.get(f"{BASE_URL}/board")
board = response.json()

# 玩家落子
response = requests.post(f"{BASE_URL}/move", json={"x": 7, "y": 7})
result = response.json()

# 与 AI 对话
response = requests.post(f"{BASE_URL}/chat", json={"message": "你为什么下在这里？"})
answer = response.json()

# 重置游戏
response = requests.post(f"{BASE_URL}/reset")
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000";

// 获取棋盘状态
const board = await fetch(`${BASE_URL}/board`).then(r => r.json());

// 玩家落子
const result = await fetch(`${BASE_URL}/move`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({x: 7, y: 7})
}).then(r => r.json());

// 与 AI 对话
const answer = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: "你为什么下在这里？"})
}).then(r => r.json());

// 重置游戏
await fetch(`${BASE_URL}/reset`, {method: "POST"});
```

### cURL

```bash
# 获取棋盘状态
curl http://localhost:8000/board

# 玩家落子
curl -X POST http://localhost:8000/move \
  -H "Content-Type: application/json" \
  -d '{"x": 7, "y": 7}'

# 与 AI 对话
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你为什么下在这里？"}'

# 重置游戏
curl -X POST http://localhost:8000/reset
```

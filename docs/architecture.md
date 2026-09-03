# 架构设计

## 系统架构概览

GomokuAgent 是一个基于 LangGraph 的五子棋 AI Agent 系统，采用前后端分离架构，核心是 LangGraph 驱动的 Agent Loop。

```
┌─────────────────────────────────────────────────────────────────┐
│                          用户界面                                │
│                    React + Vite Frontend                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        后端服务                                  │
│                    FastAPI Backend                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Agent Manager                         │   │
│  │              (创建和管理 Agent 实例)                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   LangGraph Agent                        │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐          │   │
│  │  │ Observe  │───▶│  Think   │───▶│   Act    │          │   │
│  │  │   Node   │    │   Node   │    │   Node   │          │   │
│  │  └──────────┘    └──────────┘    └──────────┘          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│          ┌───────────────────┼───────────────────┐              │
│          ▼                   ▼                   ▼              │
│  ┌──────────┐        ┌──────────┐        ┌──────────┐         │
│  │  Game    │        │  MCTS    │        │  Memory  │         │
│  │  Engine  │        │  Search  │        │  System  │         │
│  └──────────┘        └──────────┘        └──────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        外部服务                                  │
│              DeepSeek / Mimo LLM API                            │
└─────────────────────────────────────────────────────────────────┘
```

## 技术栈选择

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 主要编程语言 |
| FastAPI | 0.141+ | Web 框架 |
| LangGraph | 1.2+ | Agent 编排框架 |
| LangChain | 1.3+ | LLM 集成框架 |
| LangChain-OpenAI | 1.6+ | OpenAI 兼容 API |
| Uvicorn | 0.52+ | ASGI 服务器 |
| Pydantic | 2.13+ | 数据验证 |
| python-dotenv | 1.2+ | 环境变量管理 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.3+ | UI 框架 |
| Vite | 5.4+ | 构建工具 |
| Axios | 1.7+ | HTTP 客户端 |
| ESLint | 9.9+ | 代码检查 |

### AI 技术栈

| 技术 | 用途 |
|------|------|
| DeepSeek API | LLM 服务（推荐） |
| Mimo API | LLM 服务（备选） |
| MCTS 算法 | 搜索算法 |
| UCT 公式 | 节点选择策略 |

## 数据流设计

### 用户落子流程

```
用户点击棋盘
    │
    ▼
前端发送 POST /move {x, y}
    │
    ▼
后端接收请求
    │
    ▼
GameManager.play(x, y, BLACK)  ← 玩家落子
    │
    ├── 游戏结束？ ──▶ 返回胜利信息
    │
    ▼
切换到 AI 玩家
    │
    ▼
LangGraph Agent.invoke()
    │
    ├──▶ Observe Node: 分析局势
    │
    ├──▶ Strategy Node: LLM 选择策略
    │
    └──▶ MCTS Node: 执行落子
    │
    ▼
GameManager.play(ai_x, ai_y, WHITE)  ← AI 落子
    │
    ├── 游戏结束？ ──▶ 保存棋局 + 自动复盘
    │
    ▼
返回结果到前端
    │
    ▼
前端更新棋盘显示
```

### 记忆闭环流程

```
对局结束
    │
    ▼
save_game_and_reflect()
    │
    ├──▶ GameMemory.add_game()  ← 保存棋局
    │
    └──▶ GameReflector.reflect()  ← LLM 复盘
    │
    ▼
更新记忆中的复盘结果
    │
    ▼
下次对局时读取经验
    │
    ▼
Strategy Node 使用经验指导决策
```

## Agent Loop 设计

### 核心循环

Agent Loop 是系统的核心设计，采用感知-思考-行动-反思的循环模式：

```
┌─────────────────────────────────────────────────────────┐
│                    Agent Loop                            │
│                                                         │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│   │ Observe  │───▶│  Think   │───▶│   Act    │         │
│   │ (感知)   │    │ (思考)   │    │ (行动)   │         │
│   └──────────┘    └──────────┘    └──────────┘         │
│        ▲                                      │         │
│        │                                      │         │
│        └──────────── 记忆闭环 ◀───────────────┘         │
│                      Reflect                            │
│                      (反思)                             │
└─────────────────────────────────────────────────────────┘
```

### 状态管理

使用 LangGraph 的 StateGraph 管理状态：

```python
class GomokuState(TypedDict):
    board: Any                    # 棋盘
    player: int                   # 当前玩家
    messages: Annotated[list, add]  # 消息列表
    winner: str                   # 获胜方
    strategy: dict                # LLM 策略
    observation: Optional[dict]   # 感知结果
    lessons: Optional[List[str]]  # 历史经验
    phase: Optional[str]          # 游戏阶段
```

### 节点定义

| 节点 | 功能 | 输入 | 输出 |
|------|------|------|------|
| Observe | 感知局势 | board, history | observation, phase, lessons |
| Think | 选择策略 | board, observation, lessons | strategy |
| Act | 执行落子 | board, strategy | move, result |

## 模块依赖关系

```
                    ┌─────────────┐
                    │   Backend   │
                    │   (FastAPI) │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  Agent   │    │  Memory  │    │Reflection│
    │ (LangGraph)│   │  System  │    │  System  │
    └────┬─────┘    └──────────┘    └──────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌──────┐
│ Game │  │ MCTS │
│Engine│  │Search│
└──────┘  └──────┘
```

## 扩展性设计

### 添加新工具

在 `tools/` 目录下创建新的工具文件：

```python
from langchain_core.tools import tool

def create_new_tools(board):
    @tool
    def new_tool():
        """工具描述"""
        # 工具逻辑
        return result

    return [new_tool]
```

### 添加新节点

在 `agent/graph.py` 中添加新节点：

```python
def new_node(state):
    # 节点逻辑
    return {"new_field": value}

graph.add_node("new_node", new_node)
graph.add_edge("existing_node", "new_node")
```

### 添加新 API

在 `backend/api.py` 中添加新路由：

```python
@router.get("/new-endpoint")
def new_endpoint():
    # 业务逻辑
    return {"result": data}
```

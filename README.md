# GomokuAgent

基于 LangGraph 的五子棋 AI Agent，具备感知-思考-行动-反思的完整循环。

## 核心特性

- **LangGraph Agent Loop**: Observe → Think → Act → Reflect
- **MCTS 搜索算法**: 300 次模拟 + UCT 选择
- **LLM 策略决策**: 基于局势分析动态选择进攻/防守/平衡策略
- **记忆学习系统**: 自动保存棋局和复盘经验，形成学习闭环
- **人机对话**: 可以问 AI 落子思路，AI 会解释决策原因
- **美观 UI**: React + Vite 前端，渐变背景，棋子立体效果

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    Agent Loop                            │
│                                                         │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│   │ Observe  │───▶│  Think   │───▶│   Act    │         │
│   │ (感知)   │    │ (思考)   │    │ (行动)   │         │
│   └──────────┘    └──────────┘    └──────────┘         │
│        ▲                                      │         │
│        └──────────── 记忆闭环 ◀───────────────┘         │
│                      Reflect                            │
└─────────────────────────────────────────────────────────┘
```

## 项目结构

```
GomokuAgent/
├── agent/                  # Agent 核心逻辑
│   ├── graph.py           # LangGraph 状态图定义
│   ├── state.py           # 状态类型定义
│   └── ...
├── game/                   # 游戏引擎
│   ├── board.py           # 棋盘类
│   ├── rules.py           # 五子棋规则
│   ├── evaluator.py       # 棋盘评估函数
│   └── ...
├── mcts/                   # MCTS 搜索算法
│   ├── node.py            # MCTS 节点
│   └── search.py          # MCTS 搜索主逻辑
├── memory/                 # 记忆系统
│   └── game_memory.py     # 长期记忆
├── reflection/             # 复盘系统
│   └── reflector.py       # LLM 驱动的复盘
├── tools/                  # LangChain 工具
│   └── mcts_tools.py      # MCTS 落子工具
├── backend/                # FastAPI 后端
│   ├── main.py            # 应用入口
│   └── api.py             # API 路由
├── frontend/               # React 前端
│   ├── src/
│   │   ├── App.jsx        # 主应用
│   │   ├── GomokuBoard.jsx # 棋盘组件
│   │   └── api.js         # API 调用
│   └── package.json
└── pyproject.toml
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/AK993/GomokuAgent.git
cd GomokuAgent

# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
uv pip install -e .
```

### 2. 配置 API Key

创建 `.env` 文件：

```env
# DeepSeek API (推荐)
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL_NAME=deepseek-chat

# 或者 Mimo API
MIMO_API_KEY=sk-your-key-here
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
MIMO_MODEL_NAME=mimo-v2.5
```

### 3. 启动后端

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 http://localhost:8000 启动

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端将在 http://localhost:5173 启动

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /board | 获取棋盘状态 |
| POST | /move | 玩家落子 |
| POST | /reset | 重置游戏 |
| POST | /chat | 与 AI 对话 |
| GET | /memory | 获取历史记忆 |
| GET | /agent/status | 获取 Agent 状态 |
| POST | /reflect | 手动触发复盘 |

## Agent 工作流程

1. **Observe (感知)**: 分析游戏阶段、局势、中心控制
2. **Think (思考)**: LLM 基于感知结果和历史经验选择策略
3. **Act (行动)**: MCTS 执行落子，记录决策信息
4. **Reflect (反思)**: 对局结束自动复盘，保存经验到记忆

## 技术栈

- **后端**: Python 3.11+, FastAPI, LangGraph, LangChain
- **前端**: React 18, Vite, Axios
- **AI**: DeepSeek/Mimo API, MCTS 算法
- **工具**: uv (包管理), ESLint

## 开发计划

- [ ] 添加开局库
- [ ] 实现 AI 自我对弈训练
- [ ] 添加难度等级选择
- [ ] 支持不同棋盘大小
- [ ] 添加棋谱导入/导出

## License

MIT

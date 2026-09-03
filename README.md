<div align="center">

# 🎮 GomokuAgent

### LangGraph-based Gomoku AI Agent

<br>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2+-000000?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<br>

**一个具备感知-思考-行动-反思完整循环的五子棋 AI Agent**

[快速开始](#-快速开始) •
[架构设计](#-架构设计) •
[文档](#-文档) •
[API](#-api-接口)

<br>

---

</div>

## ✨ 核心特性

<table>
<tr>
<td width="50%">

### 🧠 Agent Loop
- **感知 (Observe)** - 分析局势、阶段、威胁
- **思考 (Think)** - LLM 动态选择策略
- **行动 (Act)** - MCTS 搜索最优落子
- **反思 (Reflect)** - 自动复盘学习

</td>
<td width="50%">

### 🎯 智能决策
- **MCTS 搜索** - 300 次模拟 + UCT 选择
- **LLM 策略** - 进攻/防守/平衡动态切换
- **战术优先** - 必胜点和必堵点快速响应
- **记忆学习** - 经验闭环持续提升

</td>
</tr>
<tr>
<td width="50%">

### 💬 人机对话
- 问 AI "你为什么下这里？"
- AI 解释落子思路和策略
- 实时了解 AI 决策过程

</td>
<td width="50%">

### 🎨 美观界面
- React + Vite 现代前端
- 渐变背景 + 立体棋子
- 星位标记 + 坐标显示
- 响应式布局设计

</td>
</tr>
</table>

---

## 🏗️ 架构设计

<div align="center">

```
                          ┌─────────────────────────────────────────┐
                          │           🎮 User Interface             │
                          │         React + Vite Frontend           │
                          └───────────────────┬─────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              🚀 FastAPI Backend                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                            🤖 LangGraph Agent                               │   │
│  │                                                                             │   │
│  │   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐            │   │
│  │   │   👁️ Observe │─────▶│   🧠 Think   │─────▶│   🎯 Act     │            │   │
│  │   │    (感知)    │      │    (思考)    │      │    (行动)    │            │   │
│  │   └──────────────┘      └──────────────┘      └──────────────┘            │   │
│  │         │                                                             │         │   │
│  │         │                    ┌──────────────┐                          │         │   │
│  │         └───────────────────▶│  📝 Reflect  │◀─────────────────────────┘         │   │
│  │                              │    (反思)    │                                    │   │
│  │                              └──────┬───────┘                                    │   │
│  │                                     │                                            │   │
│  └─────────────────────────────────────┼────────────────────────────────────────────┘   │
│                                        │                                                │
│          ┌─────────────────────────────┼─────────────────────────────┐                  │
│          ▼                             ▼                             ▼                  │
│   ┌──────────────┐            ┌──────────────┐            ┌──────────────┐            │
│   │   🎮 Game    │            │   🔍 MCTS    │            │   💾 Memory  │            │
│   │   Engine     │            │   Search     │            │   System     │            │
│   └──────────────┘            └──────────────┘            └──────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
                          ┌─────────────────────────────────────────┐
                          │          🧠 LLM API (DeepSeek/Mimo)     │
                          └─────────────────────────────────────────┘
```

</div>

---

## 📁 项目结构

```
GomokuAgent/
│
├── 🤖 agent/                    # Agent 核心逻辑
│   ├── graph.py                #   └─ LangGraph 状态图定义
│   ├── state.py                #   └─ 状态类型定义
│   └── ...
│
├── 🎮 game/                     # 游戏引擎
│   ├── board.py                #   └─ 棋盘类 (15×15)
│   ├── rules.py                #   └─ 五子棋规则
│   ├── evaluator.py            #   └─ 棋盘评估函数
│   ├── move_generator.py       #   └─ 候选落子生成器
│   ├── manager.py              #   └─ 游戏状态管理
│   └── tactical.py             #   └─ 战术检测 (必胜/必堵)
│
├── 🔍 mcts/                     # MCTS 搜索算法
│   ├── node.py                 #   └─ MCTS 节点 (UCT 选择)
│   └── search.py               #   └─ MCTS 搜索主逻辑
│
├── 💾 memory/                   # 记忆系统
│   ├── game_memory.py          #   └─ 长期记忆 (JSON 持久化)
│   └── replay.py               #   └─ 历史棋局回放
│
├── 📝 reflection/               # 复盘系统
│   └── reflector.py            #   └─ LLM 驱动的复盘分析
│
├── 🔧 tools/                    # LangChain 工具
│   ├── mcts_tools.py           #   └─ MCTS 落子工具
│   ├── board_tools.py          #   └─ 棋盘操作工具
│   └── strategy_tools.py       #   └─ 策略分析工具
│
├── 🚀 backend/                  # FastAPI 后端
│   ├── main.py                 #   └─ 应用入口
│   └── api.py                  #   └─ API 路由定义
│
├── 🎨 frontend/                 # React 前端
│   ├── src/
│   │   ├── App.jsx             #   └─ 主应用组件
│   │   ├── GomokuBoard.jsx     #   └─ 棋盘组件
│   │   └── api.js              #   └─ API 调用封装
│   └── package.json
│
└── 📄 pyproject.toml
```

---

## 🚀 快速开始

### 1️⃣ 克隆项目

```bash
git clone https://github.com/AK993/GomokuAgent.git
cd GomokuAgent
```

### 2️⃣ 配置 API Key

创建 `.env` 文件：

```env
# 🔑 DeepSeek API (推荐)
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL_NAME=deepseek-chat

# 🔑 或者 Mimo API
MIMO_API_KEY=sk-your-key-here
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
MIMO_MODEL_NAME=mimo-v2.5
```

### 3️⃣ 启动后端

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
uv pip install -e .

# 启动后端服务
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> 🎉 后端将在 **http://localhost:8000** 启动
> 
> 📚 API 文档：**http://localhost:8000/docs**

### 4️⃣ 启动前端

```bash
# 新终端
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

> 🎉 前端将在 **http://localhost:5173** 启动

---

## 🔄 Agent 工作流程

<div align="center">

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🔄 Agent Loop                                     │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │    👁️              🧠              🎯              📝              │  │
│   │  Observe    ──▶   Think    ──▶    Act     ──▶   Reflect           │  │
│   │   感知             思考             行动            反思             │  │
│   │    │                                                            │  │  │
│   │    │                                                            ▼  │  │
│   │    │                                                      ┌─────────┐│  │
│   │    └──────────────────────────────────────────────────────│  Memory ││  │
│   │                                                           │   记忆  ││  │
│   │                                                           └─────────┘│  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

</div>

| 阶段 | 功能 | 输入 | 输出 |
|:----:|------|------|------|
| 👁️ **Observe** | 感知局势 | 棋盘、历史 | 局势分析、游戏阶段 |
| 🧠 **Think** | 选择策略 | 局势分析、经验 | 进攻/防守/平衡策略 |
| 🎯 **Act** | 执行落子 | 棋盘、策略 | 落子位置、决策信息 |
| 📝 **Reflect** | 复盘学习 | 棋谱、结果 | 经验教训、改进建议 |

---

## 📡 API 接口

<table>
<tr>
<th>方法</th>
<th>路径</th>
<th>说明</th>
<th>参数</th>
</tr>
<tr>
<td><code>GET</code></td>
<td><code>/board</code></td>
<td>🎯 获取棋盘状态</td>
<td>-</td>
</tr>
<tr>
<td><code>POST</code></td>
<td><code>/move</code></td>
<td>♟️ 玩家落子</td>
<td><code>{x, y}</code></td>
</tr>
<tr>
<td><code>POST</code></td>
<td><code>/reset</code></td>
<td>🔄 重置游戏</td>
<td>-</td>
</tr>
<tr>
<td><code>POST</code></td>
<td><code>/chat</code></td>
<td>💬 与 AI 对话</td>
<td><code>{message}</code></td>
</tr>
<tr>
<td><code>GET</code></td>
<td><code>/memory</code></td>
<td>💾 获取历史记忆</td>
<td>-</td>
</tr>
<tr>
<td><code>GET</code></td>
<td><code>/agent/status</code></td>
<td>📊 获取 Agent 状态</td>
<td>-</td>
</tr>
<tr>
<td><code>POST</code></td>
<td><code>/reflect</code></td>
<td>📝 手动触发复盘</td>
<td>-</td>
</tr>
</table>

---

## 🛠️ 技术栈

<div align="center">

| 类别 | 技术 |
|:----:|------|
| **后端** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white) ![LangGraph](https://img.shields.io/badge/LangGraph-000?style=flat&logo=langchain&logoColor=white) |
| **前端** | ![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black) ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white) ![Axios](https://img.shields.io/badge/Axios-5A29E4?style=flat&logo=axios&logoColor=white) |
| **AI** | ![DeepSeek](https://img.shields.io/badge/DeepSeek-000?style=flat) ![MCTS](https://img.shields.io/badge/MCTS-FF6B35?style=flat) |
| **工具** | ![uv](https://img.shields.io/badge/uv-DE5FE9?style=flat) ![ESLint](https://img.shields.io/badge/ESLint-4B32C3?style=flat&logo=eslint&logoColor=white) |

</div>

---

## 📚 文档

<div align="center">

| 文档 | 说明 |
|:----:|------|
| [📖 架构设计](docs/architecture.md) | 系统架构、技术栈、数据流 |
| [🔄 Agent Loop](docs/agent-loop.md) | 感知→思考→行动→反思详解 |
| [🧩 核心模块](docs/modules.md) | 8 个核心模块详细说明 |
| [📡 API 文档](docs/api.md) | 接口格式、使用示例 |
| [🚀 部署指南](docs/deployment.md) | 环境要求、安装步骤 |
| [💻 开发指南](docs/development.md) | 代码规范、扩展指南 |
| [📚 LangGraph 教程](docs/langgraph-tutorial.md) | 基于项目学习 LangGraph |

</div>

---

## 🎯 开发计划

- [ ] 📚 添加开局库
- [ ] 🤖 实现 AI 自我对弈训练
- [ ] 🎚️ 添加难度等级选择
- [ ] 📐 支持不同棋盘大小 (9×9, 13×13, 19×19)
- [ ] 📄 添加棋谱导入/导出
- [ ] 🏆 添加排行榜功能
- [ ] 🌐 支持多人在线对战

---

## 🤝 贡献

欢迎贡献！请查看 [开发指南](docs/development.md) 了解详情。

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 License

本项目基于 MIT License 开源。

<div align="center">

---

<br>

**⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！⭐**

<br>

![Star](https://img.shields.io/github/stars/AK993/GomokuAgent?style=social)

<br>

Made with ❤️ by [AK993](https://github.com/AK993)

</div>

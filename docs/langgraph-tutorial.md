# 基于 GomokuAgent 学习 LangGraph

> 本教程基于 GomokuAgent 项目，通过实际代码学习 LangGraph 的核心概念。

---

## 目录

- [第一章：LangGraph 是什么](#第一章langgraph-是什么)
- [第二章：核心概念](#第二章核心概念)
- [第三章：代码逐行解析](#第三章代码逐行解析)
- [第四章：动手实验](#第四章动手实验)
- [第五章：进阶功能](#第五章进阶功能)
- [第六章：最佳实践](#第六章最佳实践)

---

## 第一章：LangGraph 是什么

### 1.1 传统 LLM 调用 vs LangGraph

**传统方式**：线性调用 LLM

```python
# 传统方式：一次调用
response = llm.invoke("帮我下棋")
```

**LangGraph 方式**：构建有状态的工作流

```python
# LangGraph：多步骤、有状态、可循环
graph = StateGraph(State)
graph.add_node("observe", observe_node)
graph.add_node("think", think_node)
graph.add_node("act", act_node)
graph.add_edge("observe", "think")
graph.add_edge("think", "act")
app = graph.compile()
result = app.invoke(initial_state)
```

### 1.2 LangGraph 的核心优势

| 特性 | 说明 | GomokuAgent 中的体现 |
|------|------|---------------------|
| **有状态** | 节点间共享状态 | 棋盘、策略、观察结果 |
| **可控流** | 定义节点执行顺序 | observe → think → act |
| **可循环** | 支持循环和条件分支 | Agent Loop |
| **可持久化** | 状态可以保存 | 记忆系统集成 |
| **可调试** | 可以追踪每一步 | 日志和状态查看 |

### 1.3 LangGraph 的应用场景

```
适合使用 LangGraph 的场景：
├── 多步骤任务（需要分解）
├── 有状态应用（需要记忆）
├── 循环推理（需要迭代）
├── 人机协作（需要审批）
└── 复杂工作流（需要编排）

不适合的场景：
├── 简单的单次 LLM 调用
├── 无状态的请求-响应
└── 纯数据处理管道
```

---

## 第二章：核心概念

### 2.1 State（状态）

State 是 LangGraph 的核心，所有节点共享和操作的数据。

**GomokuAgent 中的 State 定义** (`agent/state.py`)：

```python
from typing import TypedDict, Any, Annotated, List, Optional
from operator import add

class GomokuState(TypedDict):
    # 棋盘对象
    board: Any

    # 当前玩家 (1=黑棋, 2=白棋)
    player: int

    # 消息列表（使用 add 操作符自动追加）
    messages: Annotated[list, add]

    # 游戏结果
    winner: str

    # LLM 生成的策略
    strategy: dict

    # 感知结果
    observation: Optional[dict]

    # 历史经验
    lessons: Optional[List[str]]

    # 游戏阶段
    phase: Optional[str]
```

**关键概念**：

```python
# Annotated[list, add] 的作用
# 当节点返回 {"messages": [new_message]} 时
# LangGraph 会自动执行 messages = messages + [new_message]
# 而不是 messages = [new_message]
```

**动手实验**：

```python
# 实验 1：理解 State 的工作方式
from typing import TypedDict, Annotated
from operator import add

class TestState(TypedDict):
    count: int
    items: Annotated[list, add]

# 模拟节点返回
state = {"count": 0, "items": []}

# 节点 1 返回
update1 = {"count": 1, "items": ["a"]}
# 结果：{"count": 1, "items": ["a"]}

# 节点 2 返回
update2 = {"count": 2, "items": ["b"]}
# 结果：{"count": 2, "items": ["a", "b"]}  ← items 自动追加！
```

### 2.2 Node（节点）

节点是执行具体逻辑的函数，接收 State，返回 State 的更新。

**节点函数的签名**：

```python
def my_node(state: GomokuState) -> dict:
    """
    参数：
        state: 当前状态（只读）
    
    返回：
        dict: 需要更新的状态字段
    """
    # 读取状态
    board = state["board"]
    strategy = state["strategy"]

    # 执行逻辑
    result = do_something(board, strategy)

    # 返回更新
    return {"messages": [result]}
```

**GomokuAgent 中的三个节点**：

```python
# 节点 1：感知节点
def observe_node(state):
    """分析当前局势"""
    board = state["board"]
    # ... 分析逻辑 ...
    return {
        "observation": observation,
        "phase": phase,
        "lessons": lessons
    }

# 节点 2：策略节点
def strategy_node(state):
    """LLM 选择策略"""
    board_text = state["board"].show()
    observation = state.get("observation", {})
    # ... LLM 调用 ...
    return {"strategy": strategy}

# 节点 3：行动节点
def mcts_node(state):
    """MCTS 执行落子"""
    tools = create_mcts_tools(state["board"], state["strategy"])
    result = tools[0].invoke({})
    return {"messages": [result]}
```

### 2.3 Edge（边）

边定义了节点之间的连接关系。

**普通边**：A → B（A 执行完后执行 B）

```python
graph.add_edge("observe", "strategy")  # observe 之后执行 strategy
graph.add_edge("strategy", "mcts")     # strategy 之后执行 mcts
```

**条件边**：根据状态选择下一个节点

```python
# 根据局势选择不同的策略节点
graph.add_conditional_edges(
    "observe",  # 源节点
    lambda state: "aggressive" if state["observation"]["situation"] == "advantage" else "defensive",
    {
        "aggressive": "attack_strategy",
        "defensive": "defense_strategy"
    }
)
```

**特殊边**：

```python
from langgraph.graph import END

# 结束边：执行完后结束
graph.add_edge("mcts", END)  # mcts 之后结束
```

### 2.4 Entry Point（入口）

定义图的起始节点。

```python
graph.set_entry_point("observe")  # 从 observe 开始
```

等价于：

```python
graph.add_edge(START, "observe")
```

### 2.5 完整的图构建

**GomokuAgent 的完整图** (`agent/graph.py`)：

```python
from langgraph.graph import StateGraph, END

# 1. 创建图
graph = StateGraph(GomokuState)

# 2. 添加节点
graph.add_node("observe", observe_node)
graph.add_node("strategy", strategy_node)
graph.add_node("mcts", mcts_node)

# 3. 设置入口
graph.set_entry_point("observe")

# 4. 添加边
graph.add_edge("observe", "strategy")
graph.add_edge("strategy", "mcts")
graph.add_edge("mcts", END)

# 5. 编译图
app = graph.compile()
```

**对应的流程图**：

```
START
  │
  ▼
┌──────────┐
│ Observe  │
└────┬─────┘
     │
     ▼
┌──────────┐
│ Strategy │
└────┬─────┘
     │
     ▼
┌──────────┐
│   MCTS   │
└────┬─────┘
     │
     ▼
   END
```

---

## 第三章：代码逐行解析

### 3.1 agent/graph.py 完整解析

```python
# ==================== 导入部分 ====================

from langgraph.graph import StateGraph, END
# StateGraph: 状态图类，用于构建 Agent 工作流
# END: 特殊标记，表示图的结束

from langchain_openai import ChatOpenAI
# ChatOpenAI: OpenAI 兼容的 LLM 接口

from langchain_core.messages import SystemMessage
# SystemMessage: 系统消息类型，用于 LLM 提示

from .state import GomokuState
# 导入我们定义的状态类型

from tools.mcts_tools import create_mcts_tools
# 导入 MCTS 工具创建函数

from memory.game_memory import GameMemory
# 导入记忆系统


# ==================== Agent 创建函数 ====================

def create_agent(board):
    """
    创建 LangGraph Agent

    参数：
        board: 棋盘对象

    返回：
        编译后的 LangGraph 应用
    """

    # 初始化 LLM
    llm = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL_NAME"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL"),
        temperature=0,        # 温度为 0，输出确定性
        max_tokens=500        # 最大 token 数
    )

    # 初始化记忆系统
    memory = GameMemory()


    # ==================== 节点 1：感知 ====================

    def observe_node(state):
        """
        感知节点：分析当前局势

        输入：board（棋盘）
        输出：observation（观察结果）, phase（游戏阶段）, lessons（经验）
        """
        board = state["board"]
        player = board.current_player
        enemy = board.BLACK if player == board.WHITE else board.WHITE

        # 分析游戏阶段
        stone_count = len(board.history)
        if stone_count < 10:
            phase = "opening"      # 开局
        elif stone_count < 30:
            phase = "middle"       # 中盘
        else:
            phase = "endgame"      # 残局

        # 评估双方形势
        my_score = evaluator.evaluate_player(board, player)
        enemy_score = evaluator.evaluate_player(board, enemy)

        # 判断局势
        if my_score > enemy_score * 1.5:
            situation = "advantage"     # 优势
        elif enemy_score > my_score * 1.5:
            situation = "disadvantage"  # 劣势
        else:
            situation = "balanced"      # 均势

        # 返回状态更新
        return {
            "observation": {
                "phase": phase,
                "situation": situation,
                "my_score": my_score,
                "enemy_score": enemy_score
            },
            "phase": phase,
            "lessons": memory.get_lessons()  # 读取历史经验
        }


    # ==================== 节点 2：思考 ====================

    def strategy_node(state):
        """
        策略节点：LLM 选择策略

        输入：board, observation, lessons
        输出：strategy（策略）
        """
        # 获取棋盘文本表示
        board_text = state["board"].show()

        # 获取感知结果
        observation = state.get("observation", {})
        lessons = state.get("lessons", [])
        phase = state.get("phase", "middle")

        # 构建 LLM 提示
        prompt = f"""
你是五子棋高级策略AI。

当前棋盘:
{board_text}

游戏阶段: {phase}
局势分析: {observation.get('situation', 'unknown')}
我方得分: {observation.get('my_score', 0)}
对手得分: {observation.get('enemy_score', 0)}

历史经验:
{lessons}

根据当前棋局、局势分析和历史经验，选择策略。

只返回JSON:
{{
    "style": "attack/defense/balance",
    "priority": "create_threat/block/best_move",
    "reason": "选择理由"
}}
"""

        # 调用 LLM
        response = llm.invoke([SystemMessage(content=prompt)])

        # 解析响应
        try:
            strategy = json.loads(response.content)
        except json.JSONDecodeError:
            strategy = {"style": "balance", "priority": "best_move"}

        return {"strategy": strategy}


    # ==================== 节点 3：行动 ====================

    def mcts_node(state):
        """
        行动节点：MCTS 执行落子

        输入：board, strategy
        输出：messages（落子结果）
        """
        # 创建 MCTS 工具
        tools = create_mcts_tools(
            state["board"],
            state["strategy"]
        )

        # 调用工具获取落子位置
        result = tools[0].invoke({})

        # 执行落子
        if result.get("move"):
            x, y = result["move"]
            player = state["board"].current_player
            state["board"].place(x, y, player)

        # 返回结果
        return {"messages": [result]}


    # ==================== 构建图 ====================

    # 1. 创建状态图
    graph = StateGraph(GomokuState)

    # 2. 添加节点
    graph.add_node("observe", observe_node)
    graph.add_node("strategy", strategy_node)
    graph.add_node("mcts", mcts_node)

    # 3. 设置入口
    graph.set_entry_point("observe")

    # 4. 添加边（定义执行顺序）
    graph.add_edge("observe", "strategy")   # observe → strategy
    graph.add_edge("strategy", "mcts")      # strategy → mcts
    graph.add_edge("mcts", END)             # mcts → 结束

    # 5. 编译图
    return graph.compile()
```

### 3.2 如何调用 Agent

**在 backend/api.py 中**：

```python
# 创建 Agent
agent = create_agent(game.board)

# 调用 Agent
result = agent.invoke({
    "board": game.board,           # 棋盘
    "player": game.board.current_player,  # 当前玩家
    "messages": [],                # 消息列表
    "winner": "",                  # 获胜方
    "strategy": {},                # 策略
    "observation": None,           # 观察结果
    "lessons": None,               # 经验
    "phase": None                  # 游戏阶段
})

# 获取结果
strategy = result.get("strategy", {})
messages = result.get("messages", [])
```

---

## 第四章：动手实验

### 实验 1：添加日志节点

**目标**：在每个节点前后添加日志，观察执行流程。

**步骤**：

1. 在 `agent/graph.py` 中添加日志节点：

```python
def log_node(state):
    """日志节点：记录当前状态"""
    print("=" * 50)
    print("当前状态:")
    print(f"  阶段: {state.get('phase', 'unknown')}")
    print(f"  策略: {state.get('strategy', {})}")
    print(f"  消息数: {len(state.get('messages', []))}")
    print("=" * 50)
    return {}  # 不修改状态
```

2. 在图中添加日志节点：

```python
graph.add_node("log", log_node)

# 修改边
graph.add_edge("observe", "log")
graph.add_edge("log", "strategy")
graph.add_edge("strategy", "mcts")
graph.add_edge("mcts", END)
```

3. 运行程序，观察日志输出。

### 实验 2：添加条件分支

**目标**：根据局势选择不同的策略。

**步骤**：

1. 定义两个策略节点：

```python
def aggressive_strategy(state):
    """激进策略"""
    return {"strategy": {"style": "attack", "priority": "create_threat"}}

def defensive_strategy(state):
    """防守策略"""
    return {"strategy": {"style": "defense", "priority": "block"}}
```

2. 添加条件边：

```python
# 添加节点
graph.add_node("aggressive", aggressive_strategy)
graph.add_node("defensive", defensive_strategy)

# 添加条件边
graph.add_conditional_edges(
    "observe",
    lambda state: state["observation"]["situation"],
    {
        "advantage": "aggressive",      # 优势 → 激进
        "disadvantage": "defensive",    # 劣势 → 防守
        "balanced": "strategy"          # 均势 → 默认
    }
)
```

### 实验 3：添加循环

**目标**：实现思考-验证循环。

**步骤**：

```python
def validate_strategy(state):
    """验证策略是否合理"""
    strategy = state.get("strategy", {})
    observation = state.get("observation", {})

    # 验证逻辑
    if strategy["style"] == "attack" and observation["situation"] == "disadvantage":
        return {"valid": False, "reason": "劣势时不应激进"}
    return {"valid": True}

def should_retry(state):
    """判断是否需要重新选择策略"""
    return not state.get("valid", True)

# 构建图
graph.add_node("strategy", strategy_node)
graph.add_node("validate", validate_strategy)

# 添加条件边
graph.add_conditional_edges(
    "validate",
    should_retry,
    {
        True: "strategy",   # 不合理 → 重新选择
        False: "mcts"       # 合理 → 执行
    }
)
```

**流程图**：

```
observe → strategy → validate → (合理?) → mcts → END
                    ↑              │
                    └──────────────┘
                       (不合理)
```

### 实验 4：添加人工审批

**目标**：AI 选择策略后，需要人工确认。

**步骤**：

```python
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# 编译图时添加中断
app = graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["mcts"]  # 在 mcts 之前中断
)

# 调用时
config = {"configurable": {"thread_id": "1"}}
result = app.invoke(initial_state, config)

# 检查是否中断
if app.get_state(config).next:
    print("等待人工确认...")
    # 人工确认后继续
    app.invoke(None, config)
```

---

## 第五章：进阶功能

### 5.1 SubGraph（子图）

子图允许你将复杂的图分解为可重用的组件。

```python
# 定义子图
def create_strategy_subgraph():
    """创建策略子图"""
    sub = StateGraph(StrategyState)

    sub.add_node("analyze", analyze_node)
    sub.add_node("decide", decide_node)
    sub.add_edge("analyze", "decide")

    return sub.compile()

# 在主图中使用子图
strategy_app = create_strategy_subgraph()
graph.add_node("strategy", strategy_app)
```

### 5.2 Checkpoint（检查点）

检查点允许你保存和恢复图的状态。

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

# 内存检查点
checkpointer = MemorySaver()

# SQLite 持久化检查点
checkpointer = SqliteSaver.from_conn_string(":memory:")

# 编译时添加检查点
app = graph.compile(checkpointer=checkpointer)

# 使用时指定 thread_id
config = {"configurable": {"thread_id": "user_123"}}
result = app.invoke(initial_state, config)

# 获取状态
state = app.get_state(config)

# 更新状态
app.update_state(config, {"strategy": new_strategy})
```

### 5.3 Streaming（流式输出）

```python
# 流式执行
for event in app.stream(initial_state, config):
    # event 包含每个节点的输出
    for node_name, node_output in event.items():
        print(f"节点 {node_name} 输出: {node_output}")
```

### 5.4 Parallel Execution（并行执行）

```python
# 并行执行多个节点
graph.add_node("analyze_a", analyze_a_node)
graph.add_node("analyze_b", analyze_b_node)
graph.add_node("merge", merge_node)

# 两个分析节点并行执行
graph.add_edge("observe", "analyze_a")
graph.add_edge("observe", "analyze_b")

# 都完成后合并
graph.add_edge("analyze_a", "merge")
graph.add_edge("analyze_b", "merge")
```

**流程图**：

```
        ┌── analyze_a ──┐
observe─┤               ├─ merge
        └── analyze_b ──┘
```

---

## 第六章：最佳实践

### 6.1 State 设计原则

```python
# ✅ 好的设计
class GoodState(TypedDict):
    # 明确的类型
    board: Any
    player: int

    # 使用 Annotated 处理累积
    messages: Annotated[list, add]

    # 可选字段使用 Optional
    observation: Optional[dict]

# ❌ 不好的设计
class BadState(TypedDict):
    # 不明确的类型
    data: dict

    # 所有字段都可选
    field1: Optional[str]
    field2: Optional[str]
    field3: Optional[str]
```

### 6.2 节点设计原则

```python
# ✅ 好的节点设计
def good_node(state):
    """
    清晰的文档字符串
    说明输入和输出
    """
    # 1. 读取状态
    board = state["board"]

    # 2. 执行逻辑
    result = process(board)

    # 3. 返回更新
    return {"result": result}

# ❌ 不好的节点设计
def bad_node(state):
    # 没有文档
    # 直接修改状态（不应该！）
    state["board"].place(7, 7)  # ❌ 不要修改传入的状态
    return state
```

### 6.3 错误处理

```python
def robust_node(state):
    """带错误处理的节点"""
    try:
        result = risky_operation(state)
        return {"result": result}
    except Exception as e:
        # 记录错误
        print(f"Error: {e}")

        # 返回默认值或错误状态
        return {
            "error": str(e),
            "result": default_value
        }
```

### 6.4 调试技巧

```python
# 1. 添加调试节点
def debug_node(state):
    """调试节点：打印当前状态"""
    import json
    print(json.dumps(state, indent=2, default=str))
    return {}

# 2. 使用 streaming 观察执行
for event in app.stream(initial_state):
    print(event)

# 3. 使用 get_state 检查状态
state = app.get_state(config)
print(state.values)  # 当前值
print(state.next)    # 下一个节点
print(state.metadata) # 元数据
```

---

## 总结

### 学习路径

```
1. 理解 State → Node → Edge 的基本概念
2. 阅读 GomokuAgent 的 agent/graph.py
3. 完成实验 1-4
4. 学习进阶功能
5. 尝试添加新功能到项目
```

### 关键代码位置

| 概念 | 文件 | 行号 |
|------|------|------|
| State 定义 | `agent/state.py` | 全文 |
| 图构建 | `agent/graph.py` | 150-180 |
| 节点定义 | `agent/graph.py` | 70-140 |
| 工具集成 | `tools/mcts_tools.py` | 全文 |
| Agent 调用 | `backend/api.py` | 120-140 |

### 进一步学习

- 📚 [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- 📚 [LangChain 文档](https://python.langchain.com/)
- 🎥 [LangGraph 视频教程](https://www.youtube.com/results?search_query=langgraph+tutorial)

---

**Happy Learning! 🚀**

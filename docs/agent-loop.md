# Agent Loop 详解

Agent Loop 是 GomokuAgent 的核心设计，采用感知-思考-行动-反思的循环模式，使 AI 具备自主决策和学习能力。

## 整体流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Loop                                │
│                                                                 │
│   用户落子                                                       │
│       │                                                         │
│       ▼                                                         │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│   │ Observe  │───▶│  Think   │───▶│   Act    │───▶│  Result  │ │
│   │ (感知)   │    │ (思考)   │    │ (行动)   │    │ (结果)   │ │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│       │                                                         │
│       ▼ (对局结束)                                               │
│   ┌──────────┐    ┌──────────┐                                  │
│   │ Reflect  │───▶│  Memory  │                                  │
│   │ (反思)   │    │ (记忆)   │                                  │
│   └──────────┘    └──────────┘                                  │
│       │                                                         │
│       ▼ (下次对局)                                               │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │                    经验应用                                │ │
│   │   Observe 读取记忆 ──▶ Think 使用经验指导策略              │ │
│   └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 1. Observe (感知)

### 功能描述

感知节点负责分析当前棋局状态，为后续决策提供依据。

### 分析内容

| 分析项 | 说明 | 用途 |
|--------|------|------|
| 游戏阶段 | opening / middle / endgame | 指导策略选择 |
| 局势判断 | advantage / disadvantage / balanced | 评估形势 |
| 双方得分 | 基于评估函数计算 | 量化优势 |
| 中心控制 | 中心区域棋子数量 | 评估位置优势 |
| 对手落子 | 最近一步落子位置 | 分析对手意图 |

### 实现代码

```python
def observe_node(state):
    """
    感知当前局势，分析：
    1. 当前游戏阶段（开局/中盘/残局）
    2. 双方棋型威胁
    3. 关键位置
    """
    board = state["board"]
    player = board.current_player
    enemy = board.BLACK if player == board.WHITE else board.WHITE

    # 计算棋子数量判断阶段
    stone_count = len(board.history)

    if stone_count < 10:
        phase = "opening"
    elif stone_count < 30:
        phase = "middle"
    else:
        phase = "endgame"

    # 评估双方形势
    my_score = evaluator.evaluate_player(board, player)
    enemy_score = evaluator.evaluate_player(board, enemy)

    # 判断局势
    if my_score > enemy_score * 1.5:
        situation = "advantage"
    elif enemy_score > my_score * 1.5:
        situation = "disadvantage"
    else:
        situation = "balanced"

    # 分析对手最近落子位置
    last_move = board.history[-1] if board.history else None

    observation = {
        "phase": phase,
        "situation": situation,
        "my_score": my_score,
        "enemy_score": enemy_score,
        "stone_count": stone_count,
        "last_move": last_move,
        "center_control": _check_center_control(board)
    }

    return {
        "observation": observation,
        "phase": phase,
        "lessons": memory.get_lessons()
    }
```

### 输出示例

```json
{
    "phase": "opening",
    "situation": "advantage",
    "my_score": 40,
    "enemy_score": 0,
    "stone_count": 1,
    "last_move": {"x": 7, "y": 7, "player": 1},
    "center_control": {
        "my_stones": 1,
        "enemy_stones": 0
    }
}
```

## 2. Think (思考)

### 功能描述

思考节点使用 LLM 基于感知结果和历史经验选择策略。

### 决策因素

| 因素 | 来源 | 影响 |
|------|------|------|
| 棋盘状态 | Observe 输出 | 直接影响 |
| 游戏阶段 | Observe 输出 | 开局偏稳，中盘激进 |
| 局势判断 | Observe 输出 | 优势进攻，劣势防守 |
| 历史经验 | Memory 系统 | 避免重复错误 |

### 策略选项

```json
{
    "style": "attack/defense/balance",
    "priority": "create_threat/block/best_move",
    "reason": "选择理由"
}
```

| Style | 说明 | 适用场景 |
|-------|------|----------|
| attack | 进攻型 | 局势优势时 |
| defense | 防守型 | 局势劣势时 |
| balance | 平衡型 | 局势均衡时 |

| Priority | 说明 | 适用场景 |
|----------|------|----------|
| create_threat | 创造威胁 | 进攻时 |
| block | 阻挡对手 | 防守时 |
| best_move | 最优落子 | 默认选择 |

### 实现代码

```python
def strategy_node(state):
    board_text = state["board"].show()
    observation = state.get("observation", {})
    lessons = state.get("lessons", [])
    phase = state.get("phase", "middle")

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

根据当前棋局、局势分析和历史经验，
选择策略风格和优先级。

只返回JSON:
{{
"style": "attack/defense/balance",
"priority": "create_threat/block/best_move",
"reason": "简短说明选择理由"
}}
"""

    response = llm.invoke([SystemMessage(content=prompt)])

    try:
        strategy = json.loads(response.content)
    except json.JSONDecodeError:
        strategy = {
            "style": "balance",
            "priority": "best_move",
            "reason": "解析失败，使用默认策略"
        }

    return {"strategy": strategy}
```

### 输出示例

```json
{
    "style": "attack",
    "priority": "create_threat",
    "reason": "开局阶段，占据中心优势，应该积极创造威胁"
}
```

## 3. Act (行动)

### 功能描述

行动节点使用 MCTS 算法执行落子，结合策略选择最优位置。

### 决策流程

```
接收策略
    │
    ▼
检查必胜点 ──▶ 有 ──▶ 直接落子
    │
    ▼ (无)
检查必堵点 ──▶ 有 ──▶ 直接落子
    │
    ▼ (无)
MCTS 搜索 (300 次模拟)
    │
    ▼
结合策略评分
    │
    ▼
选择最优位置落子
```

### MCTS 搜索过程

```
Selection (选择)
    │
    ▼ 使用 UCT 公式选择最优子节点
Expansion (扩展)
    │
    ▼ 创建新节点
Simulation (模拟)
    │
    ▼ 随机模拟到终局
Backpropagation (回传)
    │
    ▼ 更新节点统计信息
```

### UCT 公式

```
UCT = win_rate + C × √(ln(parent_visits) / child_visits)

其中：
- win_rate = child.wins / child.visits
- C = 1.4 (探索常数)
- parent_visits = 父节点访问次数
- child_visits = 子节点访问次数
```

### 策略影响

```python
def strategy_score(self, move, board, strategy):
    style = strategy.get("style", "balance")
    priority = strategy.get("priority", "best_move")

    # 评估落子后的棋盘
    temp = board.clone()
    temp.place(x, y, player)

    attack_score = self.evaluator.evaluate_player(temp, player)
    defense_score = self.evaluator.evaluate_player(temp, enemy)

    # 根据 style 调整权重
    if style == "attack":
        # 进攻：重视自己的进攻得分
        base_score = attack_score - defense_score * 0.5
    elif style == "defense":
        # 防守：重视阻挡对手
        base_score = attack_score * 0.5 - defense_score
    else:
        # 平衡：攻守兼备
        base_score = attack_score - defense_score

    # 根据 priority 调整
    if priority == "create_threat":
        base_score *= 1.2
    elif priority == "block":
        base_score *= 1.1

    return base_score / 10000
```

### 实现代码

```python
def mcts_node(state):
    tools = create_mcts_tools(
        state["board"],
        state["strategy"]
    )

    # 获取推荐落子位置
    result = tools[0].invoke({})

    # 根据推荐位置执行落子
    if result.get("move"):
        x, y = result["move"]
        player = state["board"].current_player
        state["board"].place(x, y, player)

    # 添加策略信息到结果
    result["strategy"] = state.get("strategy", {})
    result["observation"] = state.get("observation", {})

    return {"messages": [result]}
```

### 输出示例

```json
{
    "move": [9, 9],
    "type": "mcts",
    "simulations": 300,
    "message": "MCTS落子 (9,9)",
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
```

## 4. Reflect (反思)

### 功能描述

反思节点在对局结束后自动运行，分析对局过程，提取经验教训。

### 分析内容

| 分析项 | 说明 | 用途 |
|--------|------|------|
| 最大失误 | 本局最错误的决策 | 避免重复错误 |
| 做得好的地方 | 成功的决策 | 强化正确行为 |
| 经验教训 | 下次应该注意什么 | 指导未来决策 |

### 实现代码

```python
def reflect(self, history, winner):
    prompt = f"""
你是一个五子棋复盘专家。

请分析下面这局棋。

棋谱:
{history}

结果:
{winner}

请输出JSON:
{{
    "mistake": "本局最大问题",
    "good_move": "做得好的地方",
    "lesson": "下一局应该注意什么"
}}
"""

    response = self.llm.invoke([SystemMessage(content=prompt)])

    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {
            "mistake": "解析失败",
            "good_move": "",
            "lesson": ""
        }
```

### 输出示例

```json
{
    "mistake": "中期防守过于被动，让对手形成活三",
    "good_move": "开局占据中心，建立了优势",
    "lesson": "下局应更积极进攻，注意阻挡对手的活三"
}
```

## 5. 记忆闭环

### 闭环流程

```
对局开始
    │
    ▼
读取历史经验 ◀─────────────────────────────────┐
    │                                           │
    ▼                                           │
Observe 使用经验                                │
    │                                           │
    ▼                                           │
Think 使用经验指导策略                          │
    │                                           │
    ▼                                           │
对局进行                                        │
    │                                           │
    ▼ (对局结束)                                 │
保存棋局到 Memory                               │
    │                                           │
    ▼                                           │
自动复盘 (Reflect)                              │
    │                                           │
    ▼                                           │
更新 Memory 中的复盘结果 ───────────────────────┘
```

### 记忆存储结构

```json
{
    "time": "2024-01-15 14:30:00",
    "winner": "AI获胜",
    "history": [
        {"x": 7, "y": 7, "player": 1},
        {"x": 8, "y": 8, "player": 2},
        ...
    ],
    "reflection": {
        "mistake": "中期防守过于被动",
        "good_move": "开局占据中心",
        "lesson": "下局应更积极进攻"
    }
}
```

### 经验应用

```python
# 读取历史经验
lessons = memory.get_lessons(limit=5)

# 在 Strategy Node 中使用
prompt = f"""
...
历史经验:
{lessons}

根据当前棋局和历史经验，选择策略。
...
"""
```

## Agent Loop 的优势

### 1. 自主决策

Agent 能够根据当前局势自主选择策略，无需人工干预。

### 2. 持续学习

通过记忆闭环，Agent 能够从每次对局中学习，不断提升棋力。

### 3. 可解释性

Agent 会记录决策原因，用户可以通过对话了解 AI 的思考过程。

### 4. 适应性

Agent 能够根据对手风格调整策略，具备一定的适应能力。

### 5. 错误恢复

当某个环节失败时，系统能够降级处理，保证对局继续进行。

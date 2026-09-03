# 核心模块详解

本文档详细介绍 GomokuAgent 项目的各个核心模块。

## 模块概览

```
GomokuAgent/
├── agent/          # Agent 核心逻辑
├── game/           # 游戏引擎
├── mcts/           # MCTS 搜索算法
├── memory/         # 记忆系统
├── reflection/     # 复盘系统
├── tools/          # LangChain 工具
├── backend/        # FastAPI 后端
└── frontend/       # React 前端
```

## 1. Agent 模块

### 文件结构

```
agent/
├── __init__.py
├── graph.py        # LangGraph 状态图定义
├── state.py        # 状态类型定义
├── strategy.py     # 策略类型定义
├── prompt.py       # 系统提示词
└── game_check.py   # 游戏状态检查
```

### graph.py - LangGraph 状态图

**功能**: 定义 Agent 的工作流程，包含 Observe、Think、Act 三个节点。

**核心函数**:

```python
def create_agent(board):
    """创建 LangGraph Agent"""

    # 定义节点
    def observe_node(state):
        """感知节点：分析局势"""
        ...

    def strategy_node(state):
        """策略节点：LLM 选择策略"""
        ...

    def mcts_node(state):
        """行动节点：MCTS 执行落子"""
        ...

    # 构建图
    graph = StateGraph(GomokuState)
    graph.add_node("observe", observe_node)
    graph.add_node("strategy", strategy_node)
    graph.add_node("mcts", mcts_node)

    # 定义边
    graph.set_entry_point("observe")
    graph.add_edge("observe", "strategy")
    graph.add_edge("strategy", "mcts")
    graph.add_edge("mcts", END)

    return graph.compile()
```

**使用方式**:

```python
agent = create_agent(board)
result = agent.invoke({
    "board": board,
    "player": board.current_player,
    "messages": [],
    "winner": "",
    "strategy": {},
    "observation": None,
    "lessons": None,
    "phase": None
})
```

### state.py - 状态类型定义

**功能**: 定义 LangGraph 状态的数据结构。

```python
class GomokuState(TypedDict):
    board: Any                          # 棋盘对象
    player: int                         # 当前玩家 (1=黑, 2=白)
    messages: Annotated[list, add]      # 消息列表
    winner: str                         # 获胜方
    strategy: dict                      # LLM 策略
    observation: Optional[dict]         # 感知结果
    lessons: Optional[List[str]]        # 历史经验
    phase: Optional[str]                # 游戏阶段
```

## 2. Game 模块

### 文件结构

```
game/
├── __init__.py
├── board.py            # 棋盘类
├── rules.py            # 五子棋规则
├── evaluator.py        # 棋盘评估函数
├── move_generator.py   # 候选落子生成器
├── manager.py          # 游戏状态管理
└── tactical.py         # 战术检测
```

### board.py - 棋盘类

**功能**: 实现五子棋棋盘的数据结构和基本操作。

```python
class Board:
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def __init__(self, size=15):
        self.size = size
        self.current_player = self.BLACK
        self.history = []
        self.board = [[self.EMPTY] * size for _ in range(size)]

    def place(self, x, y, player=None):
        """落子"""
        ...

    def is_valid_move(self, x, y):
        """判断位置是否合法"""
        ...

    def available_moves(self):
        """获取所有可落子位置"""
        ...

    def switch_player(self):
        """切换玩家"""
        ...

    def clone(self):
        """复制棋盘（用于 MCTS）"""
        ...

    def show(self):
        """显示棋盘（文本格式）"""
        ...
```

### rules.py - 五子棋规则

**功能**: 实现五子棋的胜负判断规则。

```python
class GomokuRules:
    DIRECTIONS = [(1,0), (0,1), (1,1), (1,-1)]

    def check_win(self, x, y, player):
        """检查是否获胜（五连）"""
        ...

    def get_winning_line(self, x, y, player):
        """获取获胜的连线"""
        ...

    def check_draw(self):
        """检查是否平局"""
        ...
```

### evaluator.py - 棋盘评估函数

**功能**: 评估棋盘局面的分数。

**评分标准**:

| 棋型 | 分数 | 说明 |
|------|------|------|
| five | 100000 | 五连 |
| open_four | 10000 | 活四（两端开放） |
| half_four | 5000 | 冲四（一端被堵） |
| open_three | 1000 | 活三 |
| half_three | 500 | 眠三 |
| open_two | 100 | 活二 |
| stone | 10 | 单子 |

```python
class GomokuEvaluator:
    SCORE = {
        "five": 100000,
        "open_four": 10000,
        "half_four": 5000,
        "open_three": 1000,
        "half_three": 500,
        "open_two": 100,
        "stone": 10
    }

    def evaluate(self, board, player):
        """评估棋盘（攻防综合）"""
        attack_score = self.evaluate_player(board, player)
        defense_score = self.evaluate_player(board, enemy)
        return attack_score - defense_score * 1.2

    def evaluate_player(self, board, player):
        """评估某个玩家的得分"""
        ...

    def evaluate_point(self, board, x, y, player):
        """评估某个位置的得分"""
        ...

    def count_direction(self, board, x, y, dx, dy, player):
        """沿一个方向计算连续棋子数"""
        ...
```

### move_generator.py - 候选落子生成器

**功能**: 生成候选落子位置，用于 MCTS 搜索。

```python
class MoveGenerator:
    def __init__(self, radius=2):
        self.radius = radius

    def generate(self, board):
        """生成候选位置"""
        # 第一步返回中心
        if len(board.history) == 0:
            return [(board.size // 2, board.size // 2)]

        # 围绕已有棋子搜索
        candidates = set()
        for x in range(board.size):
            for y in range(board.size):
                if board.board[x][y] != board.EMPTY:
                    self.add_neighbor(board, x, y, candidates)

        # 排序确保结果稳定
        return sorted(list(candidates))
```

### manager.py - 游戏状态管理

**功能**: 管理游戏的整体状态。

```python
class GameManager:
    def __init__(self):
        self.board = Board()
        self.winner = None
        self.game_over = False
        self.winning_line = []
        self.last_move = None

    def reset(self):
        """重置游戏"""
        ...

    def play(self, x, y, player):
        """执行落子"""
        ...

    def get_state(self):
        """获取游戏状态"""
        return {
            "board": self.board.board,
            "winner": self.winner,
            "game_over": self.game_over,
            "winning_line": self.winning_line,
            "last_move": self.last_move
        }
```

### tactical.py - 战术检测

**功能**: 检测必胜点和必堵点。

```python
class Tactical:
    def find_winning_move(self, board, player):
        """查找一步获胜的位置"""
        ...

    def find_block_move(self, board, enemy):
        """查找阻挡对手的位置"""
        ...
```

## 3. MCTS 模块

### 文件结构

```
mcts/
├── __init__.py
├── node.py         # MCTS 节点
└── search.py       # MCTS 搜索主逻辑
```

### node.py - MCTS 节点

**功能**: 实现 MCTS 树的节点。

```python
class MCTSNode:
    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0
        self.player = board.current_player
        self.untried_moves = MoveGenerator().generate(board)

    def is_terminal(self):
        """判断是否终局"""
        # 棋盘满了
        if len(self.board.available_moves()) == 0:
            return True

        # 有五连
        if self.board.history:
            last = self.board.history[-1]
            rules = GomokuRules(self.board)
            if rules.check_win(last["x"], last["y"], last["player"]):
                return True

        return False

    def expand(self):
        """扩展节点"""
        ...

    def best_child(self, c=1.4):
        """使用 UCT 选择最优子节点"""
        ...
```

### search.py - MCTS 搜索

**功能**: 实现 MCTS 搜索算法。

```python
class MCTS:
    def __init__(self, simulations=300):
        self.simulations = simulations
        self.evaluator = GomokuEvaluator()
        self.move_generator = MoveGenerator()

    def search(self, board, strategy=None):
        """搜索最优落子"""
        root = MCTSNode(board)

        for _ in range(self.simulations):
            node = self.selection(root)
            if not node.is_terminal():
                node = node.expand()
            winner = self.simulate(node.board)
            self.backpropagate(node, winner)

        return self.best_move(root, strategy)

    def selection(self, node):
        """选择阶段"""
        ...

    def simulate(self, board):
        """模拟阶段"""
        ...

    def backpropagate(self, node, winner):
        """回传阶段"""
        while node:
            node.visits += 1
            if winner and winner == node.player:
                node.wins += 1
            node = node.parent

    def best_move(self, root, strategy):
        """选择最优落子"""
        ...

    def strategy_score(self, move, board, strategy):
        """策略评分"""
        ...
```

## 4. Memory 模块

### 文件结构

```
memory/
├── __init__.py
├── game_memory.py      # 长期记忆
└── replay.py           # 历史棋局回放
```

### game_memory.py - 长期记忆

**功能**: 保存和读取历史棋局及复盘经验。

```python
class GameMemory:
    def __init__(self, path="memory/games.json"):
        self.path = path
        self.games = []
        self.load()

    def load(self):
        """加载历史棋局"""
        ...

    def save(self):
        """保存到文件"""
        ...

    def add_game(self, history, winner, reflection=None):
        """添加一局游戏"""
        game = {
            "time": str(datetime.now()),
            "winner": winner,
            "history": history,
            "reflection": reflection
        }
        self.games.append(game)
        self.save()

    def recent_games(self, limit=5):
        """获取最近几局"""
        return self.games[-limit:]

    def get_lessons(self, limit=5):
        """获取经验教训"""
        lessons = []
        for game in self.games[-limit:]:
            reflection = game.get("reflection")
            if reflection:
                lessons.append(reflection.get("lesson", ""))
        return lessons
```

### replay.py - 历史棋局回放

**功能**: 查看历史棋局。

```python
class Replay:
    def __init__(self, memory):
        self.memory = memory

    def summary(self, limit=5):
        """获取历史棋局摘要"""
        games = self.memory.recent_games(limit)
        ...
```

## 5. Reflection 模块

### 文件结构

```
reflection/
├── __init__.py
└── reflector.py        # 复盘分析
```

### reflector.py - 复盘分析

**功能**: 使用 LLM 分析对局，提取经验教训。

```python
class GameReflector:
    def __init__(self, llm):
        self.llm = llm

    def reflect(self, history, winner):
        """复盘分析"""
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

## 6. Tools 模块

### 文件结构

```
tools/
├── __init__.py
├── mcts_tools.py       # MCTS 落子工具
├── board_tools.py      # 棋盘操作工具
└── strategy_tools.py   # 策略分析工具
```

### mcts_tools.py - MCTS 落子工具

**功能**: 将 MCTS 搜索封装为 LangChain 工具。

```python
def create_mcts_tools(board, strategy=None):
    mcts = MCTS(simulations=300)
    tactical = Tactical()

    @tool
    def mcts_move():
        """
        五子棋AI落子

        优先:
        1. 必胜
        2. 必堵
        3. MCTS搜索
        """
        player = board.current_player
        enemy = board.BLACK if player == board.WHITE else board.WHITE

        # 1. 必胜
        win_move = tactical.find_winning_move(board, player)
        if win_move:
            return {"move": win_move, "type": "win", ...}

        # 2. 必堵
        block_move = tactical.find_block_move(board, enemy)
        if block_move:
            return {"move": block_move, "type": "block", ...}

        # 3. MCTS
        move = mcts.search(board, strategy)
        return {"move": move, "type": "mcts", ...}

    return [mcts_move]
```

## 7. Backend 模块

### 文件结构

```
backend/
├── __init__.py
├── main.py         # 应用入口
└── api.py          # API 路由
```

### main.py - 应用入口

**功能**: 创建 FastAPI 应用。

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import router

app = FastAPI(title="Gomoku Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)
```

### api.py - API 路由

**功能**: 定义所有 API 接口。

```python
router = APIRouter()
game = GameManager()
memory = GameMemory()
reflector = GameReflector(llm)

@router.get("/board")
def board():
    """获取棋盘状态"""
    return game.get_state()

@router.post("/move")
def move(req: MoveRequest):
    """玩家落子"""
    ...

@router.post("/chat")
def chat(req: ChatRequest):
    """与 AI 对话"""
    ...

@router.get("/memory")
def get_memory():
    """获取历史记忆"""
    ...

@router.post("/reflect")
def reflect():
    """手动触发复盘"""
    ...
```

## 8. Frontend 模块

### 文件结构

```
frontend/
├── src/
│   ├── App.jsx           # 主应用组件
│   ├── GomokuBoard.jsx   # 棋盘组件
│   ├── api.js            # API 调用
│   └── main.jsx          # 入口文件
├── index.html            # HTML 模板
├── package.json          # 依赖配置
└── vite.config.js        # Vite 配置
```

### App.jsx - 主应用组件

**功能**: 主应用组件，包含游戏状态和 UI 布局。

```jsx
function App() {
    const [board, setBoard] = useState(empty);
    const [message, setMessage] = useState("");
    const [thinking, setThinking] = useState(false);
    const [winner, setWinner] = useState(null);
    const [chatMessages, setChatMessages] = useState([]);

    async function play(x, y) {
        // 保存状态用于回滚
        const previousBoard = board.map(row => [...row]);

        // 立即显示玩家棋子
        const temp = board.map(row => [...row]);
        temp[x][y] = 1;
        setBoard(temp);

        try {
            const res = await move(x, y);
            setBoard(res.data.board);
            setWinner(res.data.winner);
        } catch (error) {
            // 回滚
            setBoard(previousBoard);
        }
    }

    return (
        <div>
            <GomokuBoard board={board} onMove={play} />
            <InfoPanel />
            <ChatPanel />
        </div>
    );
}
```

### GomokuBoard.jsx - 棋盘组件

**功能**: 渲染五子棋棋盘。

```jsx
function GomokuBoard({ board, onMove, disabled, winningLine, lastMove, winner }) {
    const size = 15;
    const cell = 40;
    const padding = 20;

    // 星位坐标
    const starPoints = [[3,3], [3,11], [7,7], [11,3], [11,11]];

    return (
        <div onClick={click}>
            {/* 网格线 */}
            {/* 星位标记 */}
            {/* 棋子 */}
            {/* 坐标标签 */}
        </div>
    );
}
```

### api.js - API 调用

**功能**: 封装后端 API 调用。

```javascript
const API = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000"
});

export function move(x, y) {
    return API.post("/move", { x, y });
}

export function getBoard() {
    return API.get("/board");
}

export function reset() {
    return API.post("/reset");
}

export function chat(message) {
    return API.post("/chat", { message });
}

export function getMemory() {
    return API.get("/memory");
}
```

# 开发指南

本文档介绍如何参与 GomokuAgent 项目的开发。

## 开发环境搭建

### 1. 克隆项目

```bash
git clone https://github.com/AK993/GomokuAgent.git
cd GomokuAgent
```

### 2. 安装依赖

```bash
# Python 依赖
uv venv
.venv\Scripts\activate
uv pip install -e .

# 前端依赖
cd frontend
npm install
```

### 3. 配置环境

创建 `.env` 文件，添加 API Key。

### 4. 启动开发服务

```bash
# 终端 1：后端
cd backend
uvicorn main:app --reload

# 终端 2：前端
cd frontend
npm run dev
```

## 代码规范

### Python 代码规范

- 遵循 PEP 8 规范
- 使用类型注解
- 编写文档字符串

```python
def evaluate_point(
    self,
    board: Board,
    x: int,
    y: int,
    player: int
) -> float:
    """
    评估某个位置的得分

    Args:
        board: 棋盘对象
        x: 行坐标
        y: 列坐标
        player: 玩家 (1=黑, 2=白)

    Returns:
        float: 评估分数
    """
    ...
```

### JavaScript/React 代码规范

- 使用 ESLint 检查
- 组件使用函数式写法
- 使用 hooks 管理状态

```jsx
function MyComponent({ prop1, prop2 }) {
    const [state, setState] = useState(initialValue);

    useEffect(() => {
        // Effect 逻辑
    }, [dependencies]);

    return (
        <div>
            {/* JSX */}
        </div>
    );
}
```

## 项目结构

```
GomokuAgent/
├── agent/                  # Agent 核心逻辑
│   ├── __init__.py
│   ├── graph.py           # LangGraph 状态图
│   ├── state.py           # 状态定义
│   └── ...
├── game/                   # 游戏引擎
│   ├── __init__.py
│   ├── board.py           # 棋盘
│   ├── rules.py           # 规则
│   ├── evaluator.py       # 评估
│   └── ...
├── mcts/                   # MCTS 算法
│   ├── __init__.py
│   ├── node.py            # 节点
│   └── search.py          # 搜索
├── memory/                 # 记忆系统
│   ├── __init__.py
│   ├── game_memory.py     # 记忆存储
│   └── replay.py          # 回放
├── reflection/             # 复盘系统
│   ├── __init__.py
│   └── reflector.py       # 复盘
├── tools/                  # LangChain 工具
│   ├── __init__.py
│   ├── mcts_tools.py      # MCTS 工具
│   └── ...
├── backend/                # 后端
│   ├── __init__.py
│   ├── main.py            # 入口
│   └── api.py             # API
├── frontend/               # 前端
│   ├── src/
│   │   ├── App.jsx
│   │   ├── GomokuBoard.jsx
│   │   └── api.js
│   └── ...
├── docs/                   # 文档
└── pyproject.toml
```

## 扩展指南

### 添加新工具

1. 在 `tools/` 目录创建新文件

```python
# tools/new_tools.py
from langchain_core.tools import tool

def create_new_tools(board):
    @tool
    def new_tool():
        """工具描述"""
        # 工具逻辑
        return result

    return [new_tool]
```

2. 在 `agent/graph.py` 中使用

```python
from tools.new_tools import create_new_tools

def new_node(state):
    tools = create_new_tools(state["board"])
    result = tools[0].invoke({})
    return {"messages": [result]}
```

### 添加新节点

1. 在 `agent/graph.py` 中定义节点

```python
def new_node(state):
    """新节点功能"""
    # 节点逻辑
    return {"new_field": value}
```

2. 添加到图中

```python
graph.add_node("new_node", new_node)
graph.add_edge("existing_node", "new_node")
```

### 添加新 API

1. 在 `backend/api.py` 中添加路由

```python
@router.get("/new-endpoint")
def new_endpoint():
    """新接口功能"""
    # 业务逻辑
    return {"result": data}
```

2. 在前端添加调用

```javascript
// frontend/src/api.js
export function newEndpoint() {
    return API.get("/new-endpoint");
}
```

### 添加新组件

1. 在 `frontend/src/` 创建新组件

```jsx
// src/NewComponent.jsx
import React from "react";

function NewComponent({ prop1, prop2 }) {
    return (
        <div>
            {/* 组件内容 */}
        </div>
    );
}

export default NewComponent;
```

2. 在 `App.jsx` 中使用

```jsx
import NewComponent from "./NewComponent";

function App() {
    return (
        <div>
            <NewComponent prop1={value1} prop2={value2} />
        </div>
    );
}
```

## 测试

### 运行 Python 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_board.py

# 运行并显示覆盖率
pytest --cov=.
```

### 运行前端测试

```bash
cd frontend

# 运行测试
npm test

# 运行并生成覆盖率报告
npm test -- --coverage
```

### 编写测试

#### Python 测试

```python
# tests/test_board.py
import pytest
from game.board import Board

def test_board_initialization():
    board = Board()
    assert board.size == 15
    assert board.current_player == Board.BLACK

def test_place_stone():
    board = Board()
    board.place(7, 7, Board.BLACK)
    assert board.board[7][7] == Board.BLACK

def test_invalid_move():
    board = Board()
    board.place(7, 7, Board.BLACK)
    with pytest.raises(ValueError):
        board.place(7, 7, Board.WHITE)
```

#### React 测试

```jsx
// src/__tests__/GomokuBoard.test.jsx
import { render, fireEvent } from "@testing-library/react";
import GomokuBoard from "../GomokuBoard";

test("renders board correctly", () => {
    const board = Array(15).fill(Array(15).fill(0));
    render(<GomokuBoard board={board} />);
});

test("handles click events", () => {
    const onMove = jest.fn();
    const board = Array(15).fill(Array(15).fill(0));
    const { container } = render(
        <GomokuBoard board={board} onMove={onMove} />
    );
    fireEvent.click(container.firstChild);
    expect(onMove).toHaveBeenCalled();
});
```

## Git 工作流

### 分支策略

- `main`: 主分支，保持稳定
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: 修复分支

### 提交规范

使用 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型：
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

示例：

```
feat(agent): add new observe node

- Add game phase detection
- Add situation analysis
- Add center control check

Closes #123
```

### 提交流程

```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 开发并提交
git add .
git commit -m "feat(module): add new feature"

# 3. 推送到远程
git push origin feature/new-feature

# 4. 创建 Pull Request

# 5. 代码审查后合并
```

## 调试技巧

### Python 调试

```python
# 使用 print 调试
print(f"Debug: {variable}")

# 使用 logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Debug: {variable}")

# 使用 breakpoint()
def some_function():
    breakpoint()  # Python 3.7+
    ...
```

### 前端调试

```javascript
// 使用 console
console.log("Debug:", variable);
console.table(array);
console.dir(object);

// 使用 React DevTools
// 安装浏览器扩展

// 使用 debugger
function myFunction() {
    debugger;
    ...
}
```

### 网络调试

```bash
# 查看后端日志
uvicorn main:app --log-level debug

# 使用 curl 测试 API
curl -v http://localhost:8000/board

# 使用浏览器 DevTools
# Network 标签查看请求
```

## 性能优化

### Python 优化

```python
# 1. 使用缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(param):
    ...

# 2. 使用生成器
def generate_moves():
    for x in range(15):
        for y in range(15):
            yield (x, y)

# 3. 使用 NumPy（如果需要）
import numpy as np
board = np.zeros((15, 15))
```

### 前端优化

```jsx
// 1. 使用 memo
const MemoizedComponent = React.memo(MyComponent);

// 2. 使用 useMemo
const expensiveResult = useMemo(() => {
    return expensiveCalculation(data);
}, [data]);

// 3. 使用 useCallback
const handleClick = useCallback(() => {
    doSomething(a, b);
}, [a, b]);
```

## 贡献流程

1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 提交代码
5. 创建 Pull Request
6. 等待代码审查
7. 合并到主分支

## 常见问题

### Q: 如何添加新的 LLM API？

A: 在 `agent/graph.py` 中修改 LLM 初始化：

```python
llm = ChatOpenAI(
    model="your-model",
    api_key="your-key",
    base_url="your-base-url",
    temperature=0,
    max_tokens=500
)
```

### Q: 如何调整 MCTS 参数？

A: 修改 `tools/mcts_tools.py`：

```python
mcts = MCTS(simulations=500)  # 增加模拟次数
```

或者修改 `mcts/node.py` 中的 UCT 常数：

```python
def best_child(self, c=1.6):  # 调整探索常数
```

### Q: 如何添加新的棋型检测？

A: 在 `game/evaluator.py` 中添加：

```python
SCORE = {
    ...
    "new_pattern": 2000,
}

def evaluate_point(self, board, x, y, player):
    ...
    if is_new_pattern:
        score += self.SCORE["new_pattern"]
```

### Q: 如何部署到生产环境？

A: 参考 [部署指南](deployment.md) 中的生产部署部分。

## 联系方式

- GitHub Issues: https://github.com/AK993/GomokuAgent/issues

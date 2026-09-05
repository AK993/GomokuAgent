from fastapi import APIRouter

from pydantic import BaseModel


from game.manager import GameManager

from game.board import Board

from agent.graph import create_agent

from memory.game_memory import GameMemory

from reflection.reflector import GameReflector

from langchain_openai import ChatOpenAI

from langchain_core.messages import SystemMessage

from dotenv import load_dotenv

import os

import json



load_dotenv()


router = APIRouter()


# 游戏管理器
game = GameManager()


# 创建 LLM
llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL_NAME"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    temperature=0,
    max_tokens=500
)


# 记忆系统
memory = GameMemory()


# 复盘系统
reflector = GameReflector(llm)


# LangGraph Agent
agent = None


# 最近一次 AI 决策信息
last_ai_decision = {}




def get_agent():
    """懒加载创建 agent"""
    global agent
    if agent is None:
        agent = create_agent(game.board)
    return agent




def save_game_and_reflect(winner):
    """保存棋局并自动复盘"""
    global last_ai_decision


    # 保存棋局
    memory.add_game(
        game.board.history,
        winner,
        None  # 先保存，复盘后更新
    )


    # 自动复盘
    try:
        reflection = reflector.reflect(
            game.board.history,
            winner
        )


        # 更新记忆中的复盘结果
        if memory.games:
            memory.games[-1]["reflection"] = reflection
            memory.save()


        return reflection

    except Exception as e:
        print(f"Reflection error: {e}")
        return None





class MoveRequest(BaseModel):

    x:int

    y:int



class ChatRequest(BaseModel):

    message:str



class NewGameRequest(BaseModel):

    size: int = 15           # 棋盘大小: 9, 13, 15
    difficulty: str = "medium"  # 难度: easy, medium, hard






@router.get("/board")
def board():
    return game.get_state()






@router.post("/reset")
def reset():
    game.reset()
    return game.get_state()


@router.post("/new-game")
def new_game(req: NewGameRequest):
    """创建新游戏，支持选择棋盘大小和难度"""
    global game, agent

    # 验证棋盘大小
    valid_sizes = [9, 13, 15]
    if req.size not in valid_sizes:
        return {"error": f"不支持的棋盘大小，可选: {valid_sizes}"}

    # 验证难度
    valid_difficulties = ["easy", "medium", "hard"]
    if req.difficulty not in valid_difficulties:
        return {"error": f"不支持的难度，可选: {valid_difficulties}"}

    # 创建新游戏
    game = GameManager(size=req.size)

    # 重置 Agent
    agent = None

    # 保存难度设置
    difficulty_map = {
        "easy": 100,
        "medium": 300,
        "hard": 500
    }

    return {
        **game.get_state(),
        "size": req.size,
        "difficulty": req.difficulty,
        "simulations": difficulty_map[req.difficulty],
        "message": f"新游戏已创建: {req.size}×{req.size} 棋盘, {req.difficulty} 难度"
    }






@router.post("/move")
def move(
    req:MoveRequest
):
    global last_ai_decision


    # 玩家黑棋落子
    ok = game.play(
        req.x,
        req.y,
        game.board.BLACK
    )

    if not ok:
        return {
            **game.get_state(),
            "message": "非法位置"
        }

    # 玩家胜利
    if game.game_over:
        reflection = save_game_and_reflect("玩家获胜")
        return {
            **game.get_state(),
            "message": "玩家获胜",
            "reflection": reflection
        }

    # 切换到 AI
    game.board.switch_player()

    # 使用 LangGraph Agent 处理 AI 落子
    try:
        agent = get_agent()
        result = agent.invoke({
            "board": game.board,
            "player": game.board.current_player,
            "messages": [],
            "winner": "",
            "strategy": {},
            "observation": None,
            "lessons": None,
            "phase": None
        })

        # 从 result 中获取策略和落子信息
        strategy = result.get("strategy", {})
        messages = result.get("messages", [])
        observation = result.get("observation", {})

        # 获取 AI 落子结果
        ai_result = None
        if messages:
            ai_result = messages[-1] if messages else None

        # 保存 AI 决策信息供对话使用
        last_ai_decision = {
            "strategy": strategy,
            "observation": observation,
            "result": ai_result
        }

        # AI 落子（通过 GameManager.play 管理状态）
        if ai_result and isinstance(ai_result, dict) and ai_result.get("move"):
            ai_x, ai_y = ai_result["move"]
            game.play(
                ai_x,
                ai_y,
                game.board.WHITE
            )

    except Exception as e:
        # 如果 LangGraph 失败，降级到直接 MCTS
        print(f"LangGraph error: {e}")
        from tools.mcts_tools import create_mcts_tools
        tools = create_mcts_tools(game.board, None)
        ai_result = tools[0].invoke({})

        if ai_result.get("move"):
            ai_x, ai_y = ai_result["move"]
            game.play(
                ai_x,
                ai_y,
                game.board.WHITE
            )

        last_ai_decision = {
            "strategy": {"style": "balance", "priority": "best_move"},
            "observation": {},
            "result": ai_result
        }

    # AI 胜利检测
    if game.game_over:
        reflection = save_game_and_reflect("AI获胜")
        return {
            **game.get_state(),
            "message": ai_result,
            "reflection": reflection
        }

    # 检测平局
    from game.rules import GomokuRules
    rules = GomokuRules(game.board)
    if rules.check_draw():
        game.game_over = True
        game.winner = "平局"
        reflection = save_game_and_reflect("平局")
        return {
            **game.get_state(),
            "message": "平局",
            "reflection": reflection
        }

    # 切回玩家
    game.board.switch_player()

    return {
        **game.get_state(),
        "message": ai_result
    }






@router.post("/chat")
def chat(req: ChatRequest):
    """
    对话接口 - 可以问 AI 关于落子思路的问题
    """
    global last_ai_decision


    # 获取当前棋盘状态
    board_text = game.board.show()


    # 获取 AI 最近决策
    strategy = last_ai_decision.get("strategy", {})
    observation = last_ai_decision.get("observation", {})
    result = last_ai_decision.get("result", {})


    # 获取历史经验
    lessons = memory.get_lessons()


    prompt = f"""
你是五子棋AI助手。用户正在和你下棋，现在问你一个问题。



当前棋盘:
{board_text}



你最近的决策:
- 策略: {json.dumps(strategy, ensure_ascii=False)}
- 落子位置: {result.get('move', 'N/A')}
- 落子类型: {result.get('type', 'N/A')}



局势分析:
{json.dumps(observation, ensure_ascii=False)}



历史经验:
{lessons}



用户问题: {req.message}



请用简洁友好的语言回答用户的问题。如果用户问你为什么下某个位置，
请解释你的思路。如果用户问其他问题，也可以适当回答。

回答限制在200字以内。
"""


    try:
        response = llm.invoke([
            SystemMessage(content=prompt)
        ])


        return {
            "response": response.content,
            "strategy": strategy,
            "observation": observation
        }

    except Exception as e:
        return {
            "response": f"抱歉，我暂时无法回答: {str(e)}",
            "strategy": strategy,
            "observation": observation
        }






@router.post("/reflect")
def reflect():
    """对最近一局进行复盘分析"""
    recent = memory.recent_games(1)
    if not recent:
        return {"error": "没有可复盘的棋局"}

    last_game = recent[0]
    result = reflector.reflect(
        last_game["history"],
        last_game["winner"]
    )

    # 更新记忆中的复盘结果
    memory.games[-1]["reflection"] = result
    memory.save()

    return result






@router.get("/memory")
def get_memory():
    """获取历史棋局记忆"""
    return {
        "games": memory.recent_games(10),
        "lessons": memory.get_lessons(5)
    }






@router.get("/agent/status")
def agent_status():
    """获取 Agent 状态信息"""
    return {
        "memory_count": len(memory.games),
        "recent_lessons": memory.get_lessons(3),
        "last_decision": last_ai_decision
    }


@router.get("/export/game/{index}")
def export_game(index: int = -1, format: str = "json"):
    """
    导出指定棋局的棋谱

    参数:
        index: 棋局索引，默认 -1 表示最后一局
        format: 导出格式，支持 "json" 或 "sgf"
    """
    result = memory.export_game(index, format)

    if result is None:
        return {"error": "没有可导出的棋局"}

    return {
        "format": format,
        "content": result
    }


@router.get("/export/all")
def export_all_games(format: str = "json"):
    """
    导出所有棋局

    参数:
        format: 导出格式，支持 "json" 或 "sgf"
    """
    result = memory.export_all_games(format)

    if result is None:
        return {"error": "没有可导出的棋局"}

    return {
        "format": format,
        "count": len(memory.games),
        "content": result
    }


@router.get("/game-sizes")
def get_game_sizes():
    """获取支持的棋盘大小"""
    return {
        "sizes": [9, 13, 15],
        "default": 15,
        "descriptions": {
            9: "9×9 小棋盘 (快速对局)",
            13: "13×13 中棋盘 (平衡)",
            15: "15×15 标准棋盘 (经典)"
        }
    }


@router.get("/difficulties")
def get_difficulties():
    """获取支持的难度等级"""
    return {
        "difficulties": ["easy", "medium", "hard"],
        "default": "medium",
        "simulations": {
            "easy": 100,
            "medium": 300,
            "hard": 500
        },
        "descriptions": {
            "easy": "简单 (100次模拟, 快速响应)",
            "medium": "中等 (300次模拟, 平衡)",
            "hard": "困难 (500次模拟, 更强棋力)"
        }
    }


@router.get("/openings")
def get_openings():
    """获取所有开局库"""
    from game.opening import OpeningBook
    book = OpeningBook()

    return {
        "count": len(book.get_all_openings()),
        "openings": book.get_all_openings()
    }


@router.get("/opening/current")
def get_current_opening():
    """获取当前开局名称"""
    from game.opening import OpeningBook
    book = OpeningBook()

    opening_name = book.get_opening_name(game.board.history)

    return {
        "opening": opening_name,
        "move_count": len(game.board.history)
    }


class SelfPlayRequest(BaseModel):
    num_games: int = 10
    board_size: int = 15
    simulations: int = 300


@router.post("/self-play")
def run_self_play(req: SelfPlayRequest):
    """
    运行 AI 自我对弈训练

    参数:
        num_games: 对局数量
        board_size: 棋盘大小
        simulations: MCTS 模拟次数
    """
    from tools.self_play import run_training

    # 验证参数
    if req.num_games < 1 or req.num_games > 100:
        return {"error": "对局数量必须在 1-100 之间"}

    if req.board_size not in [9, 13, 15]:
        return {"error": "棋盘大小必须是 9, 13 或 15"}

    if req.simulations < 50 or req.simulations > 1000:
        return {"error": "模拟次数必须在 50-1000 之间"}

    # 运行训练
    results = run_training(
        num_games=req.num_games,
        board_size=req.board_size,
        simulations=req.simulations,
        verbose=False
    )

    return {
        "success": True,
        "results": results
    }


@router.get("/self-play/stats")
def get_self_play_stats():
    """获取自我对弈训练统计"""
    from tools.self_play import SelfPlay

    trainer = SelfPlay()
    stats = trainer.get_training_stats()

    return stats

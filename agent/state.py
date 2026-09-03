from typing import TypedDict, Any, Annotated, List, Optional
from operator import add


class GomokuState(TypedDict):


    # 五子棋棋盘
    board: Any



    # 当前玩家
    player: int



    # 游戏结果（AI落子信息等）
    messages: Annotated[list, add]



    # 游戏结果
    winner: str



    # LLM生成的策略
    strategy: dict



    # 感知结果（局势分析）
    observation: Optional[dict]



    # 历史经验（从记忆中读取）
    lessons: Optional[List[str]]



    # 当前游戏阶段
    phase: Optional[str]  # opening / middle / endgame

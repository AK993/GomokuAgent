from typing import TypedDict



class GomokuStrategy(TypedDict):

    # 进攻、防守、平衡

    style: str


    # 优先目标

    priority: str
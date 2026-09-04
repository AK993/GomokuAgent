"""
开局库模块

功能：
- 存储常见开局模式
- 提供开局查询接口
- 在开局阶段优先使用开局库落子

开局库格式：
{
    "name": 开局名称,
    "moves": [(x1,y1), (x2,y2), ...],  # 前几步落子
    "response": (x, y),                  # AI 应对落子
    "score": 评分                         # 开局评分
}
"""

from typing import List, Tuple, Optional, Dict


class OpeningBook:
    """五子棋开局库"""


    def __init__(self):
        """初始化开局库"""
        self.openings = self._load_openings()


    def _load_openings(self) -> List[Dict]:
        """加载开局库数据"""
        return [
            # ==================== 直指开局 ====================

            # 花月（浦月）
            {
                "name": "花月",
                "description": "黑棋第一手天元，白棋第二手斜线相邻",
                "moves": [(7, 7), (8, 8)],
                "response": (6, 8),  # 黑棋第三手
                "score": 95
            },
            {
                "name": "浦月",
                "description": "黑棋第一手天元，白棋第二手直线相邻",
                "moves": [(7, 7), (8, 7)],
                "response": (6, 7),  # 黑棋第三手
                "score": 93
            },

            # 雨月
            {
                "name": "雨月",
                "description": "黑棋第一手天元，白棋第二手跳一格",
                "moves": [(7, 7), (9, 7)],
                "response": (6, 7),  # 黑棋第三手
                "score": 90
            },

            # ==================== 斜指开局 ====================

            # 岚月
            {
                "name": "岚月",
                "description": "黑棋第一手天元，白棋第二手斜线跳一格",
                "moves": [(7, 7), (9, 9)],
                "response": (6, 8),  # 黑棋第三手
                "score": 88
            },

            # 银月
            {
                "name": "银月",
                "description": "黑棋第一手天元，白棋第二手斜线远端",
                "moves": [(7, 7), (8, 6)],
                "response": (6, 8),  # 黑棋第三手
                "score": 85
            },

            # ==================== 其他常见开局 ====================

            # 寒星
            {
                "name": "寒星",
                "description": "黑棋第一手天元，白棋第二手直线跳二",
                "moves": [(7, 7), (10, 7)],
                "response": (6, 7),  # 黑棋第三手
                "score": 82
            },

            # 溪月
            {
                "name": "溪月",
                "description": "黑棋第一手天元，白棋第二手斜线跳二",
                "moves": [(7, 7), (10, 10)],
                "response": (6, 8),  # 黑棋第三手
                "score": 80
            },

            # 疏星
            {
                "name": "疏星",
                "description": "黑棋第一手天元，白棋第二手直线远端",
                "moves": [(7, 7), (11, 7)],
                "response": (8, 7),  # 黑棋第三手
                "score": 78
            },

            # ==================== 非天元开局 ====================

            # 星位开局
            {
                "name": "星位",
                "description": "黑棋第一手星位（3,3）",
                "moves": [(3, 3)],
                "response": (7, 7),  # 白棋应对：占据天元
                "score": 75
            },
            {
                "name": "星位",
                "description": "黑棋第一手星位（3,11）",
                "moves": [(3, 11)],
                "response": (7, 7),  # 白棋应对：占据天元
                "score": 75
            },
            {
                "name": "星位",
                "description": "黑棋第一手星位（11,3）",
                "moves": [(11, 3)],
                "response": (7, 7),  # 白棋应对：占据天元
                "score": 75
            },
            {
                "name": "星位",
                "description": "黑棋第一手星位（11,11）",
                "moves": [(11, 11)],
                "response": (7, 7),  # 白棋应对：占据天元
                "score": 75
            },

            # 小星位
            {
                "name": "小星位",
                "description": "黑棋第一手小星位（5,5）",
                "moves": [(5, 5)],
                "response": (7, 7),  # 白棋应对：占据天元
                "score": 72
            },
            {
                "name": "小星位",
                "description": "黑棋第一手小星位（5,9）",
                "moves": [(5, 9)],
                "response": (7, 7),  # 白棋应对：占据天元
                "score": 72
            },
            {
                "name": "小星位",
                "description": "黑棋第一手小星位（9,5）",
                "moves": [(9, 5)],
                "response": (7, 7),  # 白棋应对：占据天元
                "score": 72
            },
            {
                "name": "小星位",
                "description": "黑棋第一手小星位（9,9）",
                "moves": [(9, 9)],
                "response": (7, 7),  # 白棋应对：占据天元
                "score": 72
            },
        ]


    def find_opening(
        self,
        history: List[Dict],
        player: int
    ) -> Optional[Tuple[int, int]]:
        """
        查询开局库

        参数:
            history: 棋谱历史
            player: 当前玩家 (1=黑, 2=白)

        返回:
            落子位置 (x, y) 或 None
        """
        if not history:
            # 空棋盘，返回天元
            return (7, 7)

        # 提取己方落子序列
        my_moves = [
            (m["x"], m["y"])
            for m in history
            if m["player"] == player
        ]

        # 查询开局库
        for opening in self.openings:
            moves = opening["moves"]

            # 检查是否匹配开局模式
            if self._match_opening(my_moves, moves):
                # 获取推荐的应对落子
                response = opening["response"]

                # 检查落子位置是否合法
                if self._is_valid_move(history, response):
                    return response

        return None


    def _match_opening(
        self,
        my_moves: List[Tuple[int, int]],
        opening_moves: List[Tuple[int, int]]
    ) -> bool:
        """
        检查是否匹配开局模式

        参数:
            my_moves: 己方落子序列
            opening_moves: 开局库落子序列

        返回:
            是否匹配
        """
        # 开局库落子数量必须大于己方落子数量
        if len(opening_moves) <= len(my_moves):
            return False

        # 检查前几步是否匹配
        for i, move in enumerate(my_moves):
            if i >= len(opening_moves):
                break
            if move != opening_moves[i]:
                return False

        return True


    def _is_valid_move(
        self,
        history: List[Dict],
        move: Tuple[int, int]
    ) -> bool:
        """
        检查落子位置是否合法

        参数:
            history: 棋谱历史
            move: 落子位置

        返回:
            是否合法
        """
        x, y = move

        # 检查边界
        if x < 0 or x >= 15 or y < 0 or y >= 15:
            return False

        # 检查是否已有棋子
        for m in history:
            if m["x"] == x and m["y"] == y:
                return False

        return True


    def get_opening_name(
        self,
        history: List[Dict]
    ) -> Optional[str]:
        """
        获取开局名称

        参数:
            history: 棋谱历史

        返回:
            开局名称或 None
        """
        if len(history) < 2:
            return None

        # 提取前两步
        first_two = [(m["x"], m["y"]) for m in history[:2]]

        # 查询开局库
        for opening in self.openings:
            if opening["moves"][:2] == first_two:
                return opening["name"]

        return None


    def get_all_openings(self) -> List[Dict]:
        """获取所有开局"""
        return self.openings


    def get_opening_by_name(self, name: str) -> List[Dict]:
        """根据名称获取开局"""
        return [o for o in self.openings if o["name"] == name]

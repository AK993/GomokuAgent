import json
import os

from datetime import datetime



class GameMemory:


    """
    五子棋长期记忆

    保存:
    - 棋谱
    - 胜负
    - 复盘经验
    """



    def __init__(
        self,
        path="memory/games.json"
    ):


        self.path = path

        self.games = []

        self.load()



    # =====================
    # 加载历史
    # =====================

    def load(self):


        if not os.path.exists(
            self.path
        ):

            return



        with open(
            self.path,
            "r",
            encoding="utf-8"
        ) as f:


            self.games = json.load(f)




    # =====================
    # 保存
    # =====================

    def save(self):


        folder = os.path.dirname(
            self.path
        )


        if folder:


            os.makedirs(

                folder,

                exist_ok=True

            )



        with open(
            self.path,
            "w",
            encoding="utf-8"
        ) as f:


            json.dump(

                self.games,

                f,

                ensure_ascii=False,

                indent=2

            )




    # =====================
    # 添加一局游戏
    # =====================

    def add_game(
        self,
        history,
        winner,
        reflection=None
    ):


        game = {


            "time":
            str(datetime.now()),



            "winner":
            winner,



            "history":
            history,



            "reflection":
            reflection

        }



        self.games.append(
            game
        )


        self.save()




    # =====================
    # 最近棋局
    # =====================

    def recent_games(
        self,
        limit=5
    ):


        return (
            self.games[-limit:]
        )




    # =====================
    # 获取经验
    # =====================

    def get_lessons(
        self,
        limit=5
    ):


        lessons=[]



        for game in self.games[-limit:]:


            reflection = game.get(
                "reflection"
            )



            if reflection:


                lessons.append(
                    reflection
                )



        return lessons




    # =====================
    # 清空
    # =====================

    def clear(self):


        self.games=[]

        self.save()



    # =====================
    # 导出棋谱
    # =====================

    def export_game(self, index=-1, format="json"):
        """
        导出指定棋局的棋谱

        参数:
            index: 棋局索引，默认 -1 表示最后一局
            format: 导出格式，支持 "json" 或 "sgf"

        返回:
            棋谱字符串
        """
        if not self.games:
            return None

        game = self.games[index]

        if format == "json":
            return json.dumps(game, ensure_ascii=False, indent=2)

        elif format == "sgf":
            return self._to_sgf(game)

        return None


    def _to_sgf(self, game):
        """
        将棋谱转换为 SGF 格式

        SGF (Smart Game Format) 是通用的棋谱格式
        """
        size = 15  # 默认棋盘大小
        if "size" in game:
            size = game["size"]

        sgf = f"(;GM[4]SZ[{size}]"

        # 添加棋步
        for i, move in enumerate(game.get("history", [])):
            x = chr(ord('a') + move["y"])  # 列转换为字母
            y = chr(ord('a') + move["x"])  # 行转换为字母
            player = "B" if move["player"] == 1 else "W"
            sgf += f";{player}[{x}{y}]"

        sgf += ")"

        return sgf


    def export_all_games(self, format="json"):
        """
        导出所有棋局

        参数:
            format: 导出格式

        返回:
            棋谱字符串
        """
        if format == "json":
            return json.dumps(self.games, ensure_ascii=False, indent=2)

        elif format == "sgf":
            sgf_list = []
            for game in self.games:
                sgf_list.append(self._to_sgf(game))
            return "\n".join(sgf_list)

        return None
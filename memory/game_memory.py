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
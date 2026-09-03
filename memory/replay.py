class Replay:


    """
    历史棋局查看
    """



    def __init__(
        self,
        memory
    ):

        self.memory = memory




    def summary(
        self,
        limit=5
    ):


        games = (
            self.memory
            .recent_games(limit)
        )


        if not games:

            return "暂无历史棋局"



        text = []



        for i,game in enumerate(
            games
        ):


            text.append(

                f"""
========
第{i+1}局

时间:
{game["time"]}


胜者:
{game["winner"]}


棋步:
{game["history"]}

"""

            )



        return "\n".join(text)
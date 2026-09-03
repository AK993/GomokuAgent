import json



from langchain_core.messages import SystemMessage




class GameReflector:


    """
    游戏复盘Agent

    分析:
    1. 输在哪里
    2. 哪一步错误
    3. 下次如何改进

    """



    def __init__(
        self,
        llm
    ):


        self.llm = llm




    def reflect(
        self,
        history,
        winner
    ):


        prompt = f"""

你是一个五子棋复盘专家。


请分析下面这局棋。


棋谱:

{history}


结果:

{winner}



请输出JSON:


{{
"mistake":
"本局最大问题",

"good_move":
"做得好的地方",

"lesson":
"下一局应该注意什么"

}}

"""


        response = self.llm.invoke(

            [

                SystemMessage(
                    content=prompt
                )

            ]

        )



        try:

            return json.loads(
                response.content
            )


        except json.JSONDecodeError:


            return {

                "mistake":
                "解析失败",


                "good_move":
                "",


                "lesson":
                ""

            }
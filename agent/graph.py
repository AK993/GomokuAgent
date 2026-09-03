from langgraph.graph import (
    StateGraph,
    END
)


from langchain_openai import ChatOpenAI


from langchain_core.messages import SystemMessage


from dotenv import load_dotenv


import os
import json


from .state import GomokuState


from tools.mcts_tools import create_mcts_tools


from memory.game_memory import GameMemory


from game.evaluator import GomokuEvaluator


from game.rules import GomokuRules



load_dotenv()




def create_agent(board):



    llm = ChatOpenAI(


        model=os.getenv(
            "DEEPSEEK_MODEL_NAME"
        ),


        api_key=os.getenv(
            "DEEPSEEK_API_KEY"
        ),


        base_url=os.getenv(
            "DEEPSEEK_BASE_URL"
        ),


        temperature=0,


        max_tokens=500

    )



    memory = GameMemory()


    evaluator = GomokuEvaluator()





    # ======================
    # Observe节点（感知）
    # ======================

    def observe_node(state):
        """
        感知当前局势，分析：
        1. 当前游戏阶段（开局/中盘/残局）
        2. 双方棋型威胁
        3. 关键位置
        """


        board = state["board"]
        player = board.current_player
        enemy = board.BLACK if player == board.WHITE else board.WHITE


        # 计算棋子数量判断阶段
        stone_count = len(board.history)


        if stone_count < 10:

            phase = "opening"

        elif stone_count < 30:

            phase = "middle"

        else:

            phase = "endgame"


        # 评估双方形势
        my_score = evaluator.evaluate_player(board, player)
        enemy_score = evaluator.evaluate_player(board, enemy)


        # 判断局势
        if my_score > enemy_score * 1.5:

            situation = "advantage"

        elif enemy_score > my_score * 1.5:

            situation = "disadvantage"

        else:

            situation = "balanced"


        # 分析对手最近落子位置
        last_move = board.history[-1] if board.history else None


        observation = {

            "phase": phase,

            "situation": situation,

            "my_score": my_score,

            "enemy_score": enemy_score,

            "stone_count": stone_count,

            "last_move": last_move,

            "center_control": _check_center_control(board)

        }


        return {

            "observation": observation,

            "phase": phase,

            "lessons": memory.get_lessons()

        }




    def _check_center_control(board):
        """检查中心区域控制情况"""
        center = board.size // 2
        center_area = 3
        my_count = 0
        enemy_count = 0


        for x in range(center - center_area, center + center_area + 1):
            for y in range(center - center_area, center + center_area + 1):
                if 0 <= x < board.size and 0 <= y < board.size:
                    if board.board[x][y] == board.current_player:
                        my_count += 1
                    elif board.board[x][y] != board.EMPTY:
                        enemy_count += 1


        return {
            "my_stones": my_count,
            "enemy_stones": enemy_count
        }






    # ======================
    # Strategy节点（策略）
    # ======================

    def strategy_node(state):


        board_text = (

            state["board"]

            .show()

        )


        observation = state.get("observation", {})
        lessons = state.get("lessons", [])
        phase = state.get("phase", "middle")



        prompt=f"""

你是五子棋高级策略AI。



当前棋盘:

{board_text}



游戏阶段: {phase}

局势分析: {observation.get('situation', 'unknown')}

我方得分: {observation.get('my_score', 0)}

对手得分: {observation.get('enemy_score', 0)}



历史经验:

{lessons}



根据当前棋局、局势分析和历史经验，
选择策略风格和优先级。



只返回JSON:


{{
"style": "attack/defense/balance",
"priority": "create_threat/block/best_move",
"reason": "简短说明选择理由"

}}


不要输出其他内容。

"""



        response = llm.invoke(

            [

                SystemMessage(

                    content=prompt

                )

            ]

        )



        try:


            strategy=json.loads(

                response.content

            )


        except json.JSONDecodeError:


            strategy={

                "style": "balance",
                "priority": "best_move",
                "reason": "解析失败，使用默认策略"

            }



        return {

            "strategy":
            strategy

        }




    # ======================
    # MCTS节点（行动）
    # ======================

    def mcts_node(state):


        tools = create_mcts_tools(

            state["board"],

            state["strategy"]

        )


        # 获取推荐落子位置
        result = tools[0].invoke({})


        # 根据推荐位置执行落子
        if result.get("move"):
            x, y = result["move"]
            player = state["board"].current_player
            state["board"].place(x, y, player)



        # 添加策略信息到结果
        result["strategy"] = state.get("strategy", {})
        result["observation"] = state.get("observation", {})



        return {


            "messages":

            [

                result

            ]

        }





    # ======================
    # 构建Graph
    # ======================


    graph = StateGraph(
        GomokuState
    )



    graph.add_node(

        "observe",

        observe_node

    )



    graph.add_node(

        "strategy",

        strategy_node

    )



    graph.add_node(

        "mcts",

        mcts_node

    )



    graph.set_entry_point(

        "observe"

    )



    graph.add_edge(

        "observe",

        "strategy"

    )



    graph.add_edge(

        "strategy",

        "mcts"

    )



    graph.add_edge(

        "mcts",

        END

    )



    return graph.compile()

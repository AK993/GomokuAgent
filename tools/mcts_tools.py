from langchain_core.tools import tool


from mcts.search import MCTS


from game.tactical import Tactical


from game.opening import OpeningBook





def create_mcts_tools(
    board,
    strategy=None,
    simulations=300
):


    mcts = MCTS(
        simulations=simulations
    )


    tactical = Tactical()


    opening_book = OpeningBook()





    @tool
    def mcts_move():

        """
        五子棋AI落子

        优先:
        1. 开局库
        2. 必胜
        3. 必堵
        4. MCTS搜索

        返回推荐的落子位置，由调用方决定是否落子

        """



        player = (
            board.current_player
        )



        enemy = (

            board.BLACK

            if player == board.WHITE

            else board.WHITE

        )







        # =====================
        # 0. 开局库
        # =====================

        # 开局阶段（前10步）优先使用开局库
        if len(board.history) < 10:
            opening_move = opening_book.find_opening(
                board.history,
                player
            )

            if opening_move:
                x, y = opening_move

                return {
                    "move": [x, y],
                    "type": "opening",
                    "message": f"开局库落子 ({x},{y})"
                }






        # =====================
        # 1. 必胜
        # =====================

        win_move = (

            tactical.find_winning_move(

                board,

                player

            )

        )



        if win_move:


            x,y = win_move



            return {

                "move":[

                    x,

                    y

                ],


                "type":

                "win",



                "message":

                f"立即获胜 ({x},{y})"

            }









        # =====================
        # 2. 必堵
        # =====================


        block_move = (

            tactical.find_block_move(

                board,

                enemy

            )

        )



        if block_move:


            x,y = block_move



            return {

                "move":[

                    x,

                    y

                ],


                "type":

                "block",



                "message":

                f"阻止对手 ({x},{y})"

            }











        # =====================
        # 3. MCTS
        # =====================


        move = mcts.search(

            board,

            strategy

        )



        if move is None:


            return {


                "move":

                None,


                "type":

                "none",



                "message":

                "没有可落子位置"

            }







        x,y = move



        return {


            "move":[

                x,

                y

            ],



            "type":

            "mcts",



            "simulations":

            mcts.simulations,



            "message":

            f"MCTS落子 ({x},{y})"

        }


    return [

        mcts_move

    ]

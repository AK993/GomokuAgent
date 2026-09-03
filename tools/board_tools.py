from langchain_core.tools import tool



def create_board_tools(board):


    @tool
    def make_move(
        x:int,
        y:int
    ):
        """
        在五子棋棋盘上下棋

        参数:
        x: 横坐标
        y: 纵坐标
        """

        try:

            board.place(
                x,
                y
            )


            return f"成功落子 ({x},{y})"


        except Exception as e:

            return str(e)



    return [

        make_move

    ]
from typing import List



class Board:
    """
    五子棋棋盘
    """

    EMPTY = 0

    BLACK = 1

    WHITE = 2



    def __init__(
        self,
        size=15
    ):


        self.size = size


        self.current_player = (
            self.BLACK
        )


        # 历史棋谱

        self.history = []



        self.board = [

            [
                self.EMPTY
                for _ in range(size)
            ]

            for _ in range(size)

        ]



    # =====================
    # 落子
    # =====================

    def place(
        self,
        x:int,
        y:int,
        player:int=None
    ):


        if player is None:

            player = (
                self.current_player
            )



        if not self.is_valid_move(
            x,
            y
        ):

            raise ValueError(
                f"非法位置 {x},{y}"
            )



        self.board[x][y] = player



        # 记录棋谱

        self.history.append(

            {
                "x":x,
                "y":y,
                "player":player
            }

        )




    # =====================
    # 判断位置
    # =====================

    def is_valid_move(
        self,
        x,
        y
    ):


        return (

            0 <= x < self.size

            and

            0 <= y < self.size

            and

            self.board[x][y]
            == self.EMPTY

        )



    # =====================
    # 获取棋子
    # =====================

    def get(
        self,
        x,
        y
    ):

        return self.board[x][y]



    # =====================
    # 可下位置
    # =====================

    def available_moves(
        self
    ):


        moves=[]


        for i in range(
            self.size
        ):


            for j in range(
                self.size
            ):


                if self.board[i][j] == self.EMPTY:


                    moves.append(
                        (
                            i,
                            j
                        )
                    )


        return moves




    # =====================
    # 显示棋盘
    # =====================

    def show(self):


        symbols={

            self.EMPTY:".",

            self.BLACK:"X",

            self.WHITE:"O"

        }


        result=[]



        for row in self.board:


            result.append(

                " ".join(

                    symbols[x]

                    for x in row

                )

            )


        return "\n".join(result)



    # =====================
    # 当前玩家切换
    # =====================

    def switch_player(self):


        if self.current_player == self.BLACK:

            self.current_player = self.WHITE


        else:

            self.current_player = self.BLACK




    # =====================
    # MCTS复制棋盘
    # =====================

    def clone(self):


        new_board = Board(
            self.size
        )



        new_board.board = [

            row[:]

            for row in self.board

        ]



        new_board.current_player = (

            self.current_player

        )



        new_board.history = (

            self.history[:]

        )



        return new_board




    def get_history(self):

        return self.history
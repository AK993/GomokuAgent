class MoveGenerator:


    """
    五子棋候选落子生成器
    """


    def __init__(
        self,
        radius=2
    ):

        # 棋子附近范围

        self.radius = radius



    def generate(
        self,
        board
    ):

        """
        生成候选位置
        """


        candidates = set()



        # 如果第一步

        if len(
            board.history
        ) == 0:


            center = board.size // 2


            return [
                (
                    center,
                    center
                )
            ]



        # 围绕已有棋子搜索

        for x in range(
            board.size
        ):


            for y in range(
                board.size
            ):


                if board.board[x][y] != board.EMPTY:


                    self.add_neighbor(

                        board,

                        x,

                        y,

                        candidates

                    )



        # 排序确保结果稳定
        return sorted(
            list(candidates)
        )





    def add_neighbor(
        self,
        board,
        x,
        y,
        candidates
    ):


        for dx in range(
            -self.radius,
            self.radius+1
        ):


            for dy in range(
                -self.radius,
                self.radius+1
            ):


                nx = x + dx

                ny = y + dy



                if (

                    0 <= nx < board.size

                    and

                    0 <= ny < board.size

                    and

                    board.board[nx][ny]
                    == board.EMPTY

                ):


                    candidates.add(
                        (
                            nx,
                            ny
                        )
                    )
class GomokuRules:
    """
    五子棋规则
    """

    DIRECTIONS = [

        (1,0),
        (0,1),
        (1,1),
        (1,-1)

    ]


    def __init__(
        self,
        board
    ):

        self.board = board



    def check_win(
        self,
        x,
        y,
        player
    ):

        for dx,dy in self.DIRECTIONS:


            count = 1


            # 正方向

            nx = x + dx
            ny = y + dy


            while (

                0 <= nx < self.board.size

                and

                0 <= ny < self.board.size

                and

                self.board.board[nx][ny] == player

            ):


                count += 1

                nx += dx

                ny += dy



            # 反方向

            nx = x - dx
            ny = y - dy


            while (

                0 <= nx < self.board.size

                and

                0 <= ny < self.board.size

                and

                self.board.board[nx][ny] == player

            ):


                count += 1

                nx -= dx

                ny -= dy



            if count >= 5:

                return True



        return False





    def get_winning_line(
        self,
        x,
        y,
        player
    ):


        for dx,dy in self.DIRECTIONS:


            line = [

                (x,y)

            ]


            # 正方向

            nx = x + dx
            ny = y + dy


            while (

                0 <= nx < self.board.size

                and

                0 <= ny < self.board.size

                and

                self.board.board[nx][ny] == player

            ):


                line.append(

                    (nx,ny)

                )


                nx += dx

                ny += dy





            # 反方向


            nx = x - dx

            ny = y - dy


            while (

                0 <= nx < self.board.size

                and

                0 <= ny < self.board.size

                and

                self.board.board[nx][ny] == player

            ):


                line.insert(

                    0,

                    (nx,ny)

                )


                nx -= dx

                ny -= dy




            if len(line) >= 5:

                return line[:5]



        return []



    def check_draw(self):
        """
        检查是否平局（棋盘满了）
        """
        for row in self.board.board:
            for cell in row:
                if cell == self.board.EMPTY:
                    return False
        return True
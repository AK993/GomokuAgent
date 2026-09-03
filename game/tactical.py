class Tactical:


    """
    五子棋战术检测

    负责:
    1. 必胜点
    2. 必堵点
    """



    def find_winning_move(
        self,
        board,
        player
    ):


        """
        查找当前玩家一步获胜位置
        """


        for move in board.available_moves():


            temp = board.clone()



            temp.place(

                move[0],

                move[1],

                player

            )



            if self.check_five(

                temp,

                move[0],

                move[1],

                player

            ):


                return move



        return None





    def find_block_move(
        self,
        board,
        enemy
    ):


        """
        查找阻挡敌人的位置
        """


        for move in board.available_moves():


            temp = board.clone()



            temp.place(

                move[0],

                move[1],

                enemy

            )



            if self.check_five(

                temp,

                move[0],

                move[1],

                enemy

            ):


                return move



        return None






    def check_five(
        self,
        board,
        x,
        y,
        player
    ):


        directions = [

            (1,0),

            (0,1),

            (1,1),

            (1,-1)

        ]



        for dx,dy in directions:


            count = 1



            count += self.count(

                board,

                x,

                y,

                dx,

                dy,

                player

            )



            count += self.count(

                board,

                x,

                y,

                -dx,

                -dy,

                player

            )



            if count >=5:

                return True



        return False





    def count(
        self,
        board,
        x,
        y,
        dx,
        dy,
        player
    ):


        count = 0


        x += dx

        y += dy



        while (

            0 <= x < board.size

            and

            0 <= y < board.size

            and

            board.board[x][y] == player

        ):


            count += 1


            x += dx

            y += dy



        return count
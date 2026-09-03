from game.board import Board



class GomokuEvaluator:


    SCORE = {


        "five":100000,

        "open_four":10000,    # 活四：两端都开放

        "half_four":5000,     # 冲四：一端被堵

        "open_three":1000,    # 活三：两端都开放

        "half_three":500,     # 眠三：一端被堵

        "open_two":100,       # 活二

        "stone":10

    }



    def evaluate(
        self,
        board,
        player
    ):


        enemy = (

            board.BLACK

            if player == board.WHITE

            else board.WHITE

        )


        # 自己进攻

        attack_score = (

            self.evaluate_player(

                board,

                player

            )

        )


        # 对手威胁

        defense_score = (

            self.evaluate_player(

                board,

                enemy

            )

        )


        return (

            attack_score

            -

            defense_score * 1.2

        )



    def evaluate_player(
        self,
        board,
        player
    ):


        score = 0



        for x in range(
            board.size
        ):


            for y in range(
                board.size
            ):


                if board.board[x][y] == player:


                    score += self.evaluate_point(

                        board,

                        x,

                        y,

                        player

                    )


        return score




    def evaluate_point(
        self,
        board,
        x,
        y,
        player
    ):


        score = 0



        directions = [

            (1,0),

            (0,1),

            (1,1),

            (1,-1)

        ]



        for dx,dy in directions:


            # 正方向计数
            pos_count, pos_blocked = self.count_direction(

                board, x, y, dx, dy, player

            )

            # 反方向计数
            neg_count, neg_blocked = self.count_direction(

                board, x, y, -dx, -dy, player
            )



            total = 1 + pos_count + neg_count

            blocked = pos_blocked + neg_blocked



            if total >= 5:

                score += self.SCORE["five"]

            elif total == 4:

                if blocked == 0:

                    score += self.SCORE["open_four"]  # 活四
                else:

                    score += self.SCORE["half_four"]  # 冲四

            elif total == 3:

                if blocked == 0:

                    score += self.SCORE["open_three"]  # 活三
                else:

                    score += self.SCORE["half_three"]  # 眠三

            elif total == 2:

                if blocked == 0:

                    score += self.SCORE["open_two"]  # 活二

            else:

                score += self.SCORE["stone"]



        return score



    def count_direction(
        self,
        board,
        x,
        y,
        dx,
        dy,
        player
    ):
        """
        沿一个方向计算连续棋子数和是否被堵
        返回 (count, is_blocked)
        """
        count = 0
        blocked = False

        x += dx
        y += dy

        while (
            0 <= x < board.size
            and
            0 <= y < board.size
        ):

            if board.board[x][y] == player:
                count += 1
                x += dx
                y += dy
            else:
                # 遇到空格或对手
                if board.board[x][y] != board.EMPTY:
                    blocked = True  # 被对手堵住
                break

        # 到达边界也算被堵
        if not (0 <= x < board.size and 0 <= y < board.size):
            blocked = True

        return count, blocked
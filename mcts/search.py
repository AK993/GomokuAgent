import random


from .node import MCTSNode


from game.rules import GomokuRules


from game.evaluator import GomokuEvaluator


from game.move_generator import MoveGenerator




class MCTS:



    def __init__(
        self,
        simulations=300
    ):


        self.simulations = simulations


        self.evaluator = (
            GomokuEvaluator()
        )


        self.move_generator = (
            MoveGenerator()
        )



    # ======================
    # 搜索入口
    # ======================

    def search(
        self,
        board,
        strategy=None
    ):


        root = MCTSNode(
            board
        )



        for _ in range(
            self.simulations
        ):



            # Selection

            node = self.selection(
                root
            )



            # Expansion

            if not node.is_terminal():

                node = node.expand()



            # Simulation

            winner = self.simulate(

                node.board

            )



            # Backpropagation

            self.backpropagate(

                node,

                winner

            )



        return self.best_move(

            root,

            strategy

        )




    # ======================
    # Selection
    # ======================

    def selection(
        self,
        node
    ):


        while (

            node.fully_expanded()

            and

            not node.is_terminal()

        ):


            node = node.best_child()



        return node




    # ======================
    # Simulation
    # ======================

    def simulate(
        self,
        board
    ):


        temp = board.clone()



        rules = GomokuRules(
            temp
        )



        max_steps = 60



        for _ in range(
            max_steps
        ):



            moves = (
                self.move_generator.generate(
                    temp
                )
            )



            if not moves:

                return 0



            move = self.select_move(

                temp,

                moves

            )



            player = (
                temp.current_player
            )



            temp.place(

                move[0],

                move[1],

                player

            )



            if rules.check_win(

                move[0],

                move[1],

                player

            ):


                return player



            temp.switch_player()



        return 0




    # ======================
    # 使用Evaluator选择模拟动作
    # ======================

    def select_move(
        self,
        board,
        moves
    ):


        best_move = None


        best_score = -float(
            "inf"
        )



        player = (
            board.current_player
        )



        for move in moves:



            temp = board.clone()



            temp.place(

                move[0],

                move[1],

                player

            )



            score = (
                self.evaluator.evaluate(
                    temp,
                    player
                )
            )



            if score > best_score:


                best_score = score


                best_move = move



        return best_move




    # ======================
    # 回传
    # ======================

    def backpropagate(
        self,
        node,
        winner
    ):


        while node:



            node.visits += 1



            # 只有当获胜方是当前节点的决策玩家时才加分
            if winner and winner == node.player:


                node.wins += 1



            node = node.parent




    # ======================
    # 最终选择
    # ======================

    def best_move(
        self,
        root,
        strategy=None
    ):


        best = None


        best_score = -float(
            "inf"
        )



        for child in root.children:



            if child.visits == 0:

                rate = 0

            else:

                rate = (

                    child.wins /

                    child.visits

                )



            strategy_score = (
                self.strategy_score(
                    child.move,
                    root.board,
                    strategy
                )
            )



            score = (

                rate

                +

                strategy_score

            )



            if score > best_score:


                best_score = score


                best = child.move



        return best





    # ======================
    # LLM策略影响
    # ======================

    def strategy_score(
        self,
        move,
        board,
        strategy
    ):


        if not strategy:

            return 0



        style = strategy.get(
            "style",
            "balance"
        )

        priority = strategy.get(
            "priority",
            "best_move"
        )



        x, y = move
        player = board.current_player
        enemy = board.BLACK if player == board.WHITE else board.WHITE



        # 评估落子后的棋盘
        temp = board.clone()
        temp.place(x, y, player)

        attack_score = self.evaluator.evaluate_player(temp, player)
        defense_score = self.evaluator.evaluate_player(temp, enemy)



        # 根据 style 调整权重
        if style == "attack":

            # 进攻：重视自己的进攻得分
            base_score = attack_score - defense_score * 0.5

        elif style == "defense":

            # 防守：重视阻挡对手
            base_score = attack_score * 0.5 - defense_score

        else:

            # 平衡：攻守兼备
            base_score = attack_score - defense_score



        # 根据 priority 调整
        if priority == "create_threat":

            # 优先创造威胁（活三、活四）
            base_score *= 1.2

        elif priority == "block":

            # 优先阻挡对手
            base_score *= 1.1



        # 归一化到较小范围，避免影响 UCT 选择过大
        return base_score / 10000
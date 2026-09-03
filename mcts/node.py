import math

from game.move_generator import MoveGenerator
from game.rules import GomokuRules




class MCTSNode:


    def __init__(
        self,
        board,
        parent=None,
        move=None
    ):


        # 当前棋盘

        self.board = board



        # 父节点

        self.parent = parent



        # 到达该节点的动作

        self.move = move



        # 子节点

        self.children = []



        # 访问次数

        self.visits = 0



        # 胜利次数

        self.wins = 0



        # 记录当前节点是哪个玩家的决策
        # 用于回传时判断胜负归属
        self.player = board.current_player



        # 使用候选点生成器

        generator = MoveGenerator()



        # 未扩展动作

        self.untried_moves = (
            generator.generate(
                board
            )
        )



    # ======================
    # 判断结束
    # ======================

    def is_terminal(self):

        # 棋盘满了
        if len(self.board.available_moves()) == 0:
            return True


        # 检查是否有五连（上一步落子导致胜利）
        if self.board.history:
            last = self.board.history[-1]
            rules = GomokuRules(self.board)
            if rules.check_win(last["x"], last["y"], last["player"]):
                return True


        return False



    # ======================
    # 是否扩展完成
    # ======================

    def fully_expanded(self):


        return (

            len(
                self.untried_moves
            )

            == 0

        )



    # ======================
    # 扩展节点
    # ======================

    def expand(self):


        if not self.untried_moves:

            return self



        # 取一个候选动作

        move = (
            self.untried_moves.pop()
        )



        # 复制棋盘

        new_board = (
            self.board.clone()
        )



        # 落子

        new_board.place(

            move[0],

            move[1],

            new_board.current_player

        )



        # 切换玩家

        new_board.switch_player()



        child = MCTSNode(

            board=new_board,

            parent=self,

            move=move

        )



        self.children.append(
            child
        )


        return child



    # ======================
    # UCT选择
    # ======================

    def best_child(
        self,
        c=1.4
    ):


        best_score = -float(
            "inf"
        )


        best_node = None



        for child in self.children:



            if child.visits == 0:


                score = float(
                    "inf"
                )


            else:


                exploit = (

                    child.wins /

                    child.visits

                )



                explore = (

                    c *

                    math.sqrt(

                        math.log(
                            self.visits
                        )

                        /

                        child.visits

                    )

                )



                score = (

                    exploit

                    +

                    explore

                )



            if score > best_score:


                best_score = score


                best_node = child



        return best_node
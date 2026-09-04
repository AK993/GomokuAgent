from game.board import Board

from game.rules import GomokuRules





class GameManager:


    def __init__(self, size=15):


        self.size = size
        self.board = Board(size)


        self.winner = None


        self.game_over = False


        self.winning_line = []


        self.last_move = None





    def reset(self):


        self.board = Board(self.size)


        self.winner = None


        self.game_over = False


        self.winning_line = []


        self.last_move = None






    def play(
        self,
        x,
        y,
        player
    ):


        if self.game_over:

            return False



        if not self.board.is_valid_move(
            x,
            y
        ):

            return False




        self.board.place(

            x,

            y,

            player

        )



        self.last_move = [

            x,

            y

        ]




        rules = GomokuRules(

            self.board

        )



        line = rules.get_winning_line(

            x,

            y,

            player

        )



        if line:


            self.winner = player


            self.game_over = True


            self.winning_line = line




        return True





    def get_state(self):


        return {


            "board":

            self.board.board,



            "winner":

            self.winner,



            "game_over":

            self.game_over,



            "winning_line":

            self.winning_line,



            "last_move":

            self.last_move


        }
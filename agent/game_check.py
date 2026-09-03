from game.rules import GomokuRules
def game_check_node(state):


    board = state["board"]


    rules = GomokuRules(
        board
    )


    if len(board.history)==0:

        return {
            "winner":""
        }



    last = board.history[-1]


    win = rules.check_win(

        last["x"],

        last["y"],

        last["player"]

    )


    if win:

        return {

            "winner":
            f"玩家{last['player']}胜利"

        }


    if rules.check_draw():

        return {

            "winner":
            "平局"

        }


    return {

        "winner":""

    }
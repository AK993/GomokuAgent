from langchain_core.tools import tool



def create_strategy_tools():


    @tool
    def analyze_strategy():

        """
        分析当前五子棋策略。

        返回:
        attack:
            进攻

        defense:
            防守

        balance:
            均衡
        """


        return {

            "style":"balance",

            "priority":"best_move"

        }


    return [

        analyze_strategy

    ]
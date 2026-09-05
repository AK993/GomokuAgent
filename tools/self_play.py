"""
AI 自我对弈模块

功能：
- AI 和自己下棋
- 自动记录棋局
- 积累经验提升棋力
- 支持批量训练
"""

import sys
import os
from typing import List, Dict, Optional
from datetime import datetime


# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.board import Board
from game.rules import GomokuRules
from game.evaluator import GomokuEvaluator
from mcts.search import MCTS
from memory.game_memory import GameMemory


class SelfPlay:
    """AI 自我对弈训练器"""


    def __init__(
        self,
        simulations: int = 300,
        save_games: bool = True
    ):
        """
        初始化自我对弈器

        参数:
            simulations: MCTS 模拟次数
            save_games: 是否保存棋局
        """
        self.simulations = simulations
        self.save_games = save_games
        self.memory = GameMemory()
        self.evaluator = GomokuEvaluator()


    def play_one_game(
        self,
        board_size: int = 15,
        verbose: bool = False
    ) -> Dict:
        """
        进行一局自我对弈

        参数:
            board_size: 棋盘大小
            verbose: 是否输出详细信息

        返回:
            对局结果
        """
        board = Board(board_size)
        rules = GomokuRules(board)

        # 创建两个 MCTS 实例（模拟两个玩家）
        mcts_black = MCTS(simulations=self.simulations)
        mcts_white = MCTS(simulations=self.simulations)

        move_count = 0
        max_moves = board_size * board_size  # 最大步数

        if verbose:
            print(f"开始自我对弈 ({board_size}x{board_size})")
            print("=" * 50)

        while move_count < max_moves:
            # 当前玩家
            player = board.current_player

            # 选择 MCTS 实例
            mcts = mcts_black if player == Board.BLACK else mcts_white

            # 搜索最佳落子
            move = mcts.search(board)

            if move is None:
                # 没有合法落子
                break

            x, y = move

            # 落子
            board.place(x, y, player)

            move_count += 1

            if verbose and move_count % 10 == 0:
                print(f"第 {move_count} 步: 玩家 {'黑' if player == Board.BLACK else '白'} 落子 ({x},{y})")

            # 检查是否获胜
            if rules.check_win(x, y, player):
                winner = "黑棋" if player == Board.BLACK else "白棋"

                if verbose:
                    print(f"\n{winner}获胜！共 {move_count} 步")
                    print(board.show())

                # 保存棋局
                if self.save_games:
                    self.memory.add_game(
                        board.history,
                        winner,
                        None
                    )

                return {
                    "winner": winner,
                    "winner_code": player,
                    "move_count": move_count,
                    "history": board.history,
                    "board_size": board_size
                }

            # 切换玩家
            board.switch_player()

        # 平局
        if verbose:
            print(f"\n平局！共 {move_count} 步")

        if self.save_games:
            self.memory.add_game(
                board.history,
                "平局",
                None
            )

        return {
            "winner": "平局",
            "winner_code": 0,
            "move_count": move_count,
            "history": board.history,
            "board_size": board_size
        }


    def play_multiple_games(
        self,
        num_games: int = 10,
        board_size: int = 15,
        verbose: bool = False
    ) -> Dict:
        """
        进行多局自我对弈

        参数:
            num_games: 对局数量
            board_size: 棋盘大小
            verbose: 是否输出详细信息

        返回:
            训练统计
        """
        results = {
            "black_wins": 0,
            "white_wins": 0,
            "draws": 0,
            "total_moves": 0,
            "games": []
        }

        print(f"开始 {num_games} 局自我对弈训练...")
        print("=" * 50)

        for i in range(num_games):
            if verbose:
                print(f"\n第 {i+1}/{num_games} 局:")

            result = self.play_one_game(board_size, verbose)

            # 统计结果
            if result["winner_code"] == Board.BLACK:
                results["black_wins"] += 1
            elif result["winner_code"] == Board.WHITE:
                results["white_wins"] += 1
            else:
                results["draws"] += 1

            results["total_moves"] += result["move_count"]
            results["games"].append(result)

            # 进度显示
            if not verbose:
                progress = (i + 1) / num_games * 100
                print(f"\r进度: {progress:.1f}% ({i+1}/{num_games})", end="", flush=True)

        print("\n" + "=" * 50)
        print("训练完成！")
        print(f"黑棋胜: {results['black_wins']}")
        print(f"白棋胜: {results['white_wins']}")
        print(f"平局: {results['draws']}")
        print(f"平均每局步数: {results['total_moves'] / num_games:.1f}")

        return results


    def analyze_games(self) -> Dict:
        """
        分析历史棋局

        返回:
            分析结果
        """
        games = self.memory.games

        if not games:
            return {"message": "没有历史棋局"}

        # 统计
        total = len(games)
        black_wins = sum(1 for g in games if g.get("winner") == "黑棋")
        white_wins = sum(1 for g in games if g.get("winner") == "白棋")
        draws = sum(1 for g in games if g.get("winner") == "平局")

        # 平均步数
        total_moves = sum(len(g.get("history", [])) for g in games)
        avg_moves = total_moves / total if total > 0 else 0

        # 常见开局
        opening_stats = {}
        for game in games:
            history = game.get("history", [])
            if len(history) >= 2:
                opening = f"({history[0]['x']},{history[0]['y']})-({history[1]['x']},{history[1]['y']})"
                opening_stats[opening] = opening_stats.get(opening, 0) + 1

        # 排序
        sorted_openings = sorted(
            opening_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            "total_games": total,
            "black_wins": black_wins,
            "white_wins": white_wins,
            "draws": draws,
            "black_win_rate": black_wins / total * 100 if total > 0 else 0,
            "white_win_rate": white_wins / total * 100 if total > 0 else 0,
            "avg_moves": avg_moves,
            "top_openings": sorted_openings
        }


    def get_training_stats(self) -> Dict:
        """
        获取训练统计

        返回:
            训练统计信息
        """
        analysis = self.analyze_games()

        return {
            "memory_count": len(self.memory.games),
            "analysis": analysis
        }


def run_training(
    num_games: int = 10,
    board_size: int = 15,
    simulations: int = 300,
    verbose: bool = False
) -> Dict:
    """
    运行训练的便捷函数

    参数:
        num_games: 对局数量
        board_size: 棋盘大小
        simulations: MCTS 模拟次数
        verbose: 是否输出详细信息

    返回:
        训练结果
    """
    trainer = SelfPlay(simulations=simulations)
    results = trainer.play_multiple_games(num_games, board_size, verbose)

    # 添加分析
    results["analysis"] = trainer.analyze_games()

    return results


if __name__ == "__main__":
    # 命令行运行
    import argparse

    parser = argparse.ArgumentParser(description="AI 自我对弈训练")
    parser.add_argument("-n", "--num-games", type=int, default=10, help="对局数量")
    parser.add_argument("-s", "--board-size", type=int, default=15, help="棋盘大小")
    parser.add_argument("--simulations", type=int, default=300, help="MCTS 模拟次数")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    results = run_training(
        num_games=args.num_games,
        board_size=args.board_size,
        simulations=args.simulations,
        verbose=args.verbose
    )

    print("\n训练统计:")
    print(f"总对局: {results['analysis']['total_games']}")
    print(f"黑棋胜率: {results['analysis']['black_win_rate']:.1f}%")
    print(f"白棋胜率: {results['analysis']['white_win_rate']:.1f}%")
    print(f"平均每局步数: {results['analysis']['avg_moves']:.1f}")

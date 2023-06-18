import random

import bot_lib
import game


def main():
    seed = 642281
    random.seed(seed)
    player = game.Player('trev-bot', 0, bot_lib.choose_action_with_bot)
    board = game.Board([1,1,1,1,1,1])
    game_engine = game.GameEngine(
        players=[player],
        board=board,
        score_to_win=0,
    )

    points = []
    for _ in range(10_000):
        outcome = game_engine.play()
        points.append(outcome.winner.score)

    print(sum(points) / len(points))


main()


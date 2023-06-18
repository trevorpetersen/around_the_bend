import random

import bot
import game


def main():
    seed = random.randint(0, 1_000_000)
    # seed = 642281
    print(seed)
    random.seed(seed)
    player = game.Player('trev-bot', 0, bot.choose_action_with_bot)
    board = game.Board([1,1,1,1,1,1])
    game_engine = game.GameEngine(
        players=[player],
        board=board,
        score_to_win=0,
    )

    outcome = game_engine.play()

    print(outcome)

main()


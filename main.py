import random

import bot_lib
import game


def main():
    seed = random.randint(0, 1_000_000)
    seed = 536354
    print(seed)
    random.seed(seed)
    bot = game.Player('trev-bot', 0, bot_lib.choose_action_with_bot)
    player = game.Player('trevor', 0, game.choose_action_with_keyboard)
    board = game.Board([1,1,1,1,1,1])
    print('Start game!')
    game_engine = game.GameEngine(
        players=[bot],
        board=board,
        score_to_win=0,
    )

    outcome = game_engine.play()

    print(outcome)

main()


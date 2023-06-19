import random

import bot_lib
import game


def main():
    seed = random.randint(0, 1_000_000)
    seed = 253140
    print(seed)
    random.seed(seed)
    player = game.Player('trevor', 0, game.choose_action_with_keyboard)
    bot = game.Player('trev-bot', 0, bot_lib.choose_action_with_bot)
    board = game.Board([1,1,1,1,1,1])
    print('Start game!')
    game_engine = game.GameEngine(
        players=[bot],
        board=board,
        score_to_win=0,
    )

    outcome = game_engine.play()

    print(outcome)


    # turn_state = game.TurnState(turn_score=100, can_end_turn=False, available_dice=[1, 1, 3, 5, 6])
    # game_state = game.GameState(score_to_win_has_been_reached=False, current_players_state=game.PlayerState(score=100), opponents_states=[])
    # bot_lib.choose_action_with_bot(turn_state, game_state)

main()


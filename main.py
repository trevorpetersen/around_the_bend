import bot_lib
import game

PLAYER_NAME = 'Trevor'
SCORE_TO_WIN = 5000

def main():
    player = game.Player(PLAYER_NAME, 0, game.choose_action_with_keyboard)
    bot = game.Player('Trev-bot', 0, bot_lib.choose_action_with_bot)
    board = game.Board([1,1,1,1,1,1])
    game_engine = game.GameEngine(
        players=[player, bot],
        board=board,
        score_to_win=SCORE_TO_WIN,
    )

    game_engine.play()

main()


from abc import ABC, abstractmethod
from collections import deque
import dataclasses
from operator import attrgetter
import random
from typing import Callable, Dict, List, Optional


@dataclasses.dataclass(frozen=True)
class KeepSet:
    """A set of dice that is valid to keep along with its associated score."""
    score: int
    dice: List[int]

    def copy(self) -> 'KeepSet':
        return KeepSet(self.score, self.dice.copy())


VALID_KEEP_SETS = [
    KeepSet(50, [5]),
    KeepSet(100, [1]),
    KeepSet(200, [2,2,2]),
    KeepSet(300, [3,3,3]),
    KeepSet(400, [4,4,4]),
    KeepSet(500, [5,5,5]),
    KeepSet(600, [6,6,6]),
    KeepSet(1000, [1,2,3,4,5,6]),
]


def choose_action_with_keyboard(turn_state: 'TurnState', game_state: 'GameState') -> 'Action':
    dice = turn_state.available_dice
    dice.sort()
    print(dataclasses.replace(turn_state, available_dice=dice))

    while True:
        try:
            action_string = input('Action: ')

            if action_string == '':
                raise ValueError()

            if action_string.lower() in ('e', 'end'):
                return Actions.end_turn()
            elif action_string.lower() in ('r', 'rr'):
                return Actions.reroll()
            else:
                action_string = action_string.strip()
                action_string = action_string.replace(' ', '')
                action_string = action_string.replace(',', '')
                action_string = list(action_string)
                return Actions.keep_dice(list(map(lambda dice_value: int(dice_value), action_string)))
        except Exception:
            print('Input not understood. Try again')

def get_score(keep_sets: List[KeepSet]) -> int:
    return sum(map(lambda keep_set: keep_set.score, keep_sets))

def subtract_dice(dice: List[int], to_subtract: List[int]) -> List[int]:
    new_dice = dice.copy()

    for die in to_subtract:
        new_dice.remove(die)

    return new_dice


def _get_dice_hash(dice: List[int]) -> str:
    dice_copy = dice.copy()
    dice_copy.sort()

    return str(dice_copy)

def _get_dice_tally(dice: List[int]) -> Dict[int, int]:
    tally = {i+1: 0 for i in range(6)}

    for die in dice:
        tally[die] += 1

    return tally


def get_keep_set_or_die(dice_to_keep: List[int]) -> KeepSet:
    keep_set = get_keep_set(dice_to_keep)
    if not keep_set:
        raise RuntimeError()

    return keep_set

def get_keep_set(dice_to_keep: List[int]) -> Optional[KeepSet]:
    for keep_set in VALID_KEEP_SETS:
        if _get_dice_hash(dice_to_keep) == _get_dice_hash(keep_set.dice):
            return keep_set.copy()

    return None


def _is_valid_keep_set(dice_to_keep: List[int]) -> bool:
    return get_keep_set(dice_to_keep) is not None


def _are_valid_dice_values(dice: List[int]) -> bool:
    for die in dice:
        if die < 1 or die > 6:
            return False

    return True


@dataclasses.dataclass(frozen=True)
class PlayerState:
    score: int

@dataclasses.dataclass(frozen=True)
class GameState:
    score_to_win_has_been_reached: bool
    current_players_state: PlayerState
    opponents_states: List[PlayerState]

@dataclasses.dataclass(frozen=True)
class TurnState:
    turn_score: int
    can_end_turn: bool
    available_dice: List[int]

@dataclasses.dataclass(frozen=True)
class PlayOutcome:
    winner: 'Player'

@dataclasses.dataclass(frozen=True)
class TurnOutcome:
    score: int
    kept_all_dice: bool

class Action(ABC):
    @abstractmethod
    def perform_action(self, board: 'Board') -> TurnState:
        raise NotImplementedError()


class EndTurn(Action):
    def perform_action(self, board: 'Board') -> TurnState:
        return TurnState(
            turn_score=get_score(board.get_kept_dice()),
            can_end_turn=False,
            available_dice=board.get_available_dice(),
        )

    def __str__(self) -> str:
        return 'EndTurn'


class KeepDice(Action):
    def __init__(self, dice: List[int]) -> None:
        super().__init__()
        self._dice = dice


    def perform_action(self, board: 'Board') -> TurnState:
        board.keep_dice(self._dice)

        return TurnState(
            turn_score=get_score(board.get_kept_dice()),
            can_end_turn=True,
            available_dice=board.get_available_dice(),
        )

    def __str__(self) -> str:
        return f'KeepDice{self._dice}'


class Reroll(Action):
    def perform_action(self, board: 'Board') -> TurnState:
        board.reroll()

        return TurnState(
            turn_score=get_score(board.get_kept_dice()),
            can_end_turn=False,
            available_dice=board.get_available_dice(),
        )

    def __str__(self) -> str:
        return 'Reroll'


class Actions:
    @classmethod
    def keep_dice(cls, dice: List[int]) -> 'KeepDice':
        return KeepDice(dice)

    @classmethod
    def reroll(cls) -> 'Reroll':
        return Reroll()

    @classmethod
    def end_turn(cls) -> 'EndTurn':
        return EndTurn()


@dataclasses.dataclass(frozen=False)
class Player:
    name: str
    score: int
    choose_action: Callable[[TurnState, GameState], Action]




class GameEngine:
    def __init__(self, players: List[Player], board: 'Board', score_to_win: int) -> None:
        self._players = players
        self._board = board
        self._score_to_win = score_to_win

    def play(self) -> PlayOutcome:
        for player in self._players:
            player.score = 0

        turn_queue = deque(self._players)

        while turn_queue:
            self._print_scoreboard()
            self._board.reset()
            current_player = turn_queue.popleft()
            print(f'It\'s {current_player.name}\'s ({current_player.score}) turn!')

            turn_outcome = self._take_turn(current_player, self._board)
            print(turn_outcome)

            current_player.score += turn_outcome.score
            if turn_outcome.kept_all_dice:
                turn_queue.appendleft(current_player)
            elif not self._player_has_reached_score_to_win():
                turn_queue.append(current_player)

        return PlayOutcome(
            winner=max(self._players, key=attrgetter('score'))
        )

    def _player_has_reached_score_to_win(self) -> bool:
        return max(self._players, key=attrgetter('score')).score >= self._score_to_win


    def _take_turn(self, current_player: Player,  board: 'Board') -> TurnOutcome:
        last_action = None
        game_state = self._calculate_game_state(current_player)
        turn_state=TurnState(
            turn_score=get_score(board.get_kept_dice()),
            can_end_turn=False,
            available_dice=board.get_available_dice(),
        )

        while True:
            if isinstance(last_action, EndTurn):
                print('Ended manually')
                return TurnOutcome(get_score(board.get_kept_dice()), False)

            if len(board.get_available_dice()) == 0:
                print('Around the bend')
                return TurnOutcome(get_score(board.get_kept_dice()), True)

            if not self._player_can_take_action(self._board, turn_state):
                print('Cannot act')
                return TurnOutcome(0, False)

            action = current_player.choose_action(turn_state, game_state)
            print(f'Performing action {action}')
            turn_state = action.perform_action(board)
            game_state = self._calculate_game_state(current_player)

            last_action = action

    def _player_can_take_action(self, board: 'Board', turn_state: TurnState) -> bool:
        return len(board.get_available_keep_sets()) > 0 or turn_state.can_end_turn


    def _calculate_game_state(self, current_player: Player) -> GameState:
        opponents = list(filter(lambda player: player != current_player, self._players))

        return GameState(
            score_to_win_has_been_reached=self._player_has_reached_score_to_win(),
            current_players_state=PlayerState(
                score=current_player.score,
            ),
            opponents_states=list(map(lambda opponent: PlayerState(score=opponent.score), opponents))
        )


    def setup_game(self) -> None:
        self._board.reset()
        for player in self._players:
            player.score = 0

    def _print_scoreboard(self) -> None:
        print('***** Scores *****')
        for player in self._players:
            print(f'{player.name} - {player.score}')
        print('******************')


class Board:
    MAX_DICE = 6

    def __init__(self, dice: Optional[List[int]] = None) -> None:
        self._available_dice: List[int] = []
        self._kept_dice: List[KeepSet] = []

        # if dice is not None and (len(dice) != self.MAX_DICE or not _are_valid_dice_values(dice)):
        #     raise ValueError(f'Dice are an invalid board state: {dice}')

        if dice is not None:
            self._available_dice = dice.copy()
        else:
            self.reset()

    def get_available_dice(self) -> List[int]:
        return self._available_dice.copy()

    def get_kept_dice(self) -> List[KeepSet]:
        return list(map(lambda kept_set: kept_set.copy(), self._kept_dice))

    def is_valid_to_keep(self, dice: List[int]) -> bool:
        return _is_valid_keep_set(dice) and self._dice_are_available(dice)

    def get_available_keep_sets(self) -> List[List[int]]:
        """Returns all valid sets of dice that can be kept."""
        available_keep_sets = []
        for keep_set in VALID_KEEP_SETS:
            if self.is_valid_to_keep(keep_set.dice):
                available_keep_sets.append(keep_set.dice.copy())

        return available_keep_sets

    def keep_dice(self, dice: List[int]) -> List[int]:
        """Keeps the given dice and return the leftover available dice."""
        if not self.is_valid_to_keep(dice):
            raise ValueError(f'Invalid keep: To Keep={dice} Avail={self._available_dice}')

        keep_set = get_keep_set(dice)
        if not keep_set:
            raise ValueError(f'Invalid keep: To Keep={dice} Avail={self._available_dice}')


        self._available_dice = subtract_dice(self._available_dice, dice)
        self._kept_dice.append(keep_set)

        return self._available_dice.copy()

    def reroll(self) -> None:
        self._available_dice = list(map(lambda _: random.randint(1, 6), self._available_dice))


    def reset(self) -> None:
        self._available_dice = []
        self._kept_dice = []

        for _ in range(self.MAX_DICE):
            self._available_dice.append(random.randint(1, 6))

    def _dice_are_available(self, dice: List[int]) -> bool:
        available_dice_tally = _get_dice_tally(self._available_dice)
        dice_tally = _get_dice_tally(dice)

        for i in range(6):
            if dice_tally[i+1] > available_dice_tally[i+1]:
                return False

        return True

    def __str__(self) -> str:
        return str(f'Avail={self._available_dice} Kept={self._kept_dice}')

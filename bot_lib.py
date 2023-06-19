import dataclasses
import itertools
from typing import List, Tuple

import game


_SEEN_VALUES = {}
_SEEN_REROLL = {}

def get_expected_rr_value(state: 'State') -> int:
    re_roll_hash = f'{len(state.dice)}'

    if re_roll_hash in _SEEN_REROLL:
        return _SEEN_REROLL[re_roll_hash] + state.points

    dice_lists = []
    for _ in range(len(state.dice)):
        dice_lists.append([1,2,3,4,5,6])

    possible_dice_sets = list(itertools.product(*dice_lists))
    non_bust_sets = list(filter(lambda dice_set: game.Board(list(dice_set)).get_available_keep_sets(), possible_dice_sets))

    point_sum = 0
    for non_bust_set in non_bust_sets:
        possible_state = State(
            points=state.points,
            dice=list(non_bust_set),
            can_reroll=False,
            can_end=False,
            recursion_level=state.recursion_level,
        )

        point_sum += possible_state.get_value()

    value = point_sum // len(possible_dice_sets) if len(possible_dice_sets) > 0 else 0

    _SEEN_REROLL[re_roll_hash] = value - state.points

    return value

@dataclasses.dataclass(frozen=True)
class State:
    points: int
    dice: List[int]
    can_reroll: bool
    can_end: bool
    recursion_level: int = 0

    def get_value(self) -> int:
        self.dice.sort()

        state_hash = str(self)

        if state_hash in _SEEN_VALUES:
            return _SEEN_VALUES[state_hash]

        possible_values = []
        if self.can_reroll:
            possible_values.append(get_expected_rr_value(self))
        if self.can_end:
            possible_values.append(self.points)

        board = game.Board(self.dice)

        keep_states: List[State] = []
        available_keep_sets = board.get_available_keep_sets()
        for keep_set_dice in available_keep_sets:
            new_dice = game.subtract_dice(self.dice, keep_set_dice)
            keep_states.append(State(
                points=self.points + game.get_score([game.get_keep_set_or_die(keep_set_dice)]),
                dice=new_dice,
                can_reroll=len(new_dice) > 0,
                can_end=True,
                recursion_level=self.recursion_level,
            ))

        keep_states_values = list(map(lambda state: state.get_value(), keep_states))

        possible_values += keep_states_values

        value = max(possible_values)
        # If you get around the bend, then you get to go again. To approximate this value, add on the expected value
        # of having another turn.
        if len(self.dice) == 0 and self.recursion_level < 0:
            # This is just a hacky state for "you get to roll all the dice again"
            value += get_expected_rr_value(State(
                points=0,
                dice=[2,3,4,2,3,4],
                can_reroll=True,
                can_end=False,
                recursion_level=self.recursion_level + 1
            ))
        _SEEN_VALUES[state_hash] = value

        return value


def choose_action_with_bot(turn_state: game.TurnState, game_state: game.GameState) -> game.Action:
    print('')
    dice = turn_state.available_dice
    dice.sort()
    print(dataclasses.replace(turn_state, available_dice=dice))
    board = game.Board(turn_state.available_dice)

    possible_actions: List[Tuple[game.Action, int]] = []

    if not _should_not_consider_ending_turn(turn_state, game_state):
            possible_actions.append((game.Actions.end_turn(), turn_state.turn_score))

    if turn_state.can_reroll and not _should_not_consider_rerolling_turn(turn_state, game_state):
        possible_actions.append((game.Actions.reroll(), get_expected_rr_value(State(
            points=turn_state.turn_score,
            dice=turn_state.available_dice,
            can_reroll=True,
            can_end=False,
        ))))

    available_keep_sets = board.get_available_keep_sets()
    for keep_set_dice in available_keep_sets:
        new_dice = game.subtract_dice(turn_state.available_dice, keep_set_dice)
        possible_state = State(
            points=turn_state.turn_score + game.get_score([game.get_keep_set_or_die(keep_set_dice)]),
            dice=new_dice,
            can_reroll=len(new_dice) > 0,
            can_end=True,
        )

        possible_actions.append((game.Actions.keep_dice(keep_set_dice), possible_state.get_value()))

    print(list(map(lambda tup: (str(tup[0]), tup[1]), possible_actions)))

    best = possible_actions[0]
    for possible_action in possible_actions:
        if possible_action[1] > best[1]:
            best = possible_action

    return best[0]

def _should_not_consider_ending_turn(turn_state: game.TurnState, game_state: game.GameState) -> bool:
    """Don't end your turn if the opponent would win. Go for the Hail Marry!"""
    if not game_state.opponents_states:
        return False

    if not game_state.score_to_win_has_been_reached:
        return False

    score_to_beat = max(map(lambda opponent: opponent.score, game_state.opponents_states))
    return game_state.current_players_state.score + turn_state.turn_score < score_to_beat

def _should_not_consider_rerolling_turn(turn_state: game.TurnState, game_state: game.GameState) -> bool:
    """Don't reroll if it could lose you the game."""
    if not game_state.opponents_states:
        return False

    if not game_state.score_to_win_has_been_reached:
        return False

    score_to_beat = max(map(lambda opponent: opponent.score, game_state.opponents_states))
    return game_state.current_players_state.score + turn_state.turn_score > score_to_beat

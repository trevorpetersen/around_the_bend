import unittest

import bot


class StateTest(unittest.TestCase):
    def test_constructor(self):
        self.assertEqual(bot.State(
            points=0,
            dice=[2],
            can_reroll=False,
            can_end=True,
            ).get_value(), 0)

        self.assertEqual(bot.State(
            points=100,
            dice=[2],
            can_reroll=False,
            can_end=True,
            ).get_value(), 100)

        self.assertEqual(bot.State(
            points=0,
            dice=[2],
            can_reroll=True,
            can_end=False,
            ).get_value(), 25)

        self.assertEqual(bot.State(
            points=0,
            dice=[2,3,4,2,3,4],
            can_reroll=True,
            can_end=False,
            ).get_value(), 5)

if __name__ == '__main__':
    unittest.main()
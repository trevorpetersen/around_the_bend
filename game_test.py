import unittest

import game


class BoardTest(unittest.TestCase):
    def test_constructor(self):
        game.Board()
        game.Board([1,2,3,4,5,6])

    def test_constructor_invalid(self):
        with self.assertRaises(ValueError):
            game.Board([])
        with self.assertRaises(ValueError):
            game.Board([1,2,3,4,5])
        with self.assertRaises(ValueError):
            game.Board([1,2,3,4,5,7])

    def test_is_valid_to_keep(self):
        board = game.Board([1,2,3,4,5,6])
        self.assertTrue(board.is_valid_to_keep([1]))
        self.assertTrue(board.is_valid_to_keep([5]))
        self.assertFalse(board.is_valid_to_keep([7]))
        self.assertFalse(board.is_valid_to_keep([4]))
        self.assertFalse(board.is_valid_to_keep([1,1]))
        self.assertFalse(board.is_valid_to_keep([1,2]))

        board = game.Board([1,1,1,2,2,2])
        self.assertTrue(board.is_valid_to_keep([1]))
        self.assertTrue(board.is_valid_to_keep([2,2,2]))
        self.assertFalse(board.is_valid_to_keep([5]))
        self.assertFalse(board.is_valid_to_keep([1,1,1]))
        self.assertFalse(board.is_valid_to_keep([5,5,5]))

    def test_keep_dice(self):
        self.assertEqual(game.Board([1,2,3,4,5,6]).keep_dice([1]), [2,3,4,5,6])
        self.assertEqual(game.Board([1,2,3,4,4,4]).keep_dice([4,4,4]), [1,2,3])
        self.assertEqual(game.Board([1,2,3,4,5,6]).keep_dice([5]), [1,2,3,4,6])

if __name__ == '__main__':
    unittest.main()
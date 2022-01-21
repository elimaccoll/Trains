import sys
import unittest

sys.path.append('../../../')
from Trains.Common.map import City, Color, Connection
from Trains.Other.Util.test_utils import (IsAcquireConnectionMove,
                                          IsDrawCardMove)
from Trains.Player.moves import (AcquireConnectionMove, DrawCardMove,
                                 IPlayerMove, IPlayerMoveVisitor)


class SwapMove(IPlayerMoveVisitor[IPlayerMove]):
    """Test visitor for swapping PlayerMove types."""

    def __init__(self, connection: Connection) -> None:
        super().__init__()
        self._connection = connection

    def visitDrawCards(self, _: DrawCardMove) -> IPlayerMove:
        return AcquireConnectionMove(self._connection)

    def visitAcquireConnection(self, _: AcquireConnectionMove) -> IPlayerMove:
        return DrawCardMove()


class TestPlayerMove(unittest.TestCase):
    def test_move_types(self):
        boston = City("Boston", 70, 20)
        new_york = City("New York", 60, 30)
        conn1 = Connection(frozenset({boston, new_york}), Color.BLUE, 5)
        draw_move = DrawCardMove()
        acquire_move = AcquireConnectionMove(conn1)

        self.assertTrue(draw_move.accepts(IsDrawCardMove()))
        self.assertFalse(acquire_move.accepts(IsDrawCardMove()))

        self.assertTrue(acquire_move.accepts(IsAcquireConnectionMove()))
        self.assertFalse(draw_move.accepts(IsAcquireConnectionMove()))

        self.assertEqual(draw_move.accepts(SwapMove(conn1)),
                         AcquireConnectionMove(conn1))
        self.assertEqual(acquire_move.accepts(SwapMove(conn1)), DrawCardMove())

        # Invalid input
        self.assertRaises(TypeError, AcquireConnectionMove, boston)


if __name__ == '__main__':
    unittest.main()

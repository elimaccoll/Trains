import sys
from typing import Optional

sys.path.append('../../../')
from Trains.Common.map import Connection
from Trains.Player.moves import (AcquireConnectionMove, DrawCardMove, IPlayerMoveVisitor)


class IsDrawCardMove(IPlayerMoveVisitor[bool]):
    """Test visitor for checking if a PlayerMove is a DrawCardsMove."""

    def visitDrawCards(self, _: DrawCardMove) -> bool:
        return True

    def visitAcquireConnection(self, _: AcquireConnectionMove) -> bool:
        return False


class IsAcquireConnectionMove(IPlayerMoveVisitor[bool]):
    """Test visitor for checking if a PlayerMove is an AcquireConnectionMove.

    If called with a constructor argument, the visitor will also check that the AcquireConnectionMove has a matching connection."""
    _connection: Optional[Connection]

    def __init__(self, connection: Optional[Connection] = None) -> None:
        super().__init__()
        self._connection = connection

    def visitDrawCards(self, _: DrawCardMove) -> bool:
        return False

    def visitAcquireConnection(self, move: AcquireConnectionMove) -> bool:
        if self._connection is None:
            return True

        return self._connection == move.connection

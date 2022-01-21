import sys
from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

sys.path.append('../../')
from Trains.Common.map import Connection

T = TypeVar("T")


class IPlayerMoveVisitor(Generic[T]):
    # Interpretation:
    """A Visitor interface for IPlayerMoves (`DrawCardMove` and `AcquireConnectionMove`)"""

    # We chose to implement a visitor pattern on PlayerMoves for the following reasons:
    # - There are many unrelated operations on PlayerMoves (checking legality, serialization, etc.).
    # - The concrete classes of a PlayerMove are known and not expected to change.
    # - New operations may need to be added frequently.

    @abstractmethod
    def visitDrawCards(
        self, move: 'DrawCardMove') -> T: raise NotImplementedError

    @abstractmethod
    def visitAcquireConnection(
        self, move: 'AcquireConnectionMove') -> T: raise NotImplementedError


class IPlayerMove(metaclass=ABCMeta):
    """
    Parent class that represents a player move.  Defaults move type to 'None' since
    a player's action on their turn will always dictate the move type.
    """

    @abstractmethod
    def accepts(self, visitor: IPlayerMoveVisitor[T]) -> T:
        """Accept a visitor to dispatch the "virtual operation" to."""
        raise NotImplementedError


class DrawCardMove(IPlayerMove):
    """
    Child class of IPlayerMove that represents the player action of drawing colored cards.
    """

    def accepts(self, visitor: IPlayerMoveVisitor[T]) -> T:
        return visitor.visitDrawCards(self)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, DrawCardMove)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)


class AcquireConnectionMove(IPlayerMove):
    """
    Child class of PlayerMove that represents the player action of attempting to acquire a connection.
    """

    _connection: Connection

    def __init__(self, connection: Connection) -> None:
        """
        Constructor for creating a player move that represents acquiring a given connection.
            Parameters:
                connection (Connection):
        """
        super().__init__()

        if type(connection) != Connection:
            raise TypeError("AcquireConnectionMove must be given a Connection")
        self._connection = connection

    @property
    def connection(self) -> Connection:
        return self._connection

    def accepts(self, visitor: IPlayerMoveVisitor[T]) -> T:
        return visitor.visitAcquireConnection(self)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, AcquireConnectionMove) and (o._connection == self._connection)

    def __hash__(self) -> int:
        return hash(self._connection)

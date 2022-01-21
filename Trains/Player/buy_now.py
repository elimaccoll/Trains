import sys
from typing import Iterable, List, Optional, Set, TypeVar

sys.path.append('../../')

from Trains.Common.map import Connection, Destination, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Other.Util.func_utils import flatten_set
from Trains.Other.Util.gs_utils import can_acquire_connection
from Trains.Other.Util.map_utils import get_lexicographic_order_of_connections
from Trains.Player.moves import (AcquireConnectionMove, DrawCardMove,
                                 IPlayerMove)
from Trains.Player.strategy import AbstractPlayerStrategy


class Buy_Now(AbstractPlayerStrategy):
    """
    Represents the following strategy:
    - Always attempt to acquire a connection first.
    - If there are no acquireable connections, then draw cards.
    """
    def _sort_destinations(self, destinations: List[Destination]) -> List[Destination]:
        """Sorts destinations in reverse lexicographical order."""
        sorted_dests = super()._sort_destinations(destinations)
        sorted_dests.reverse()
        return sorted_dests

    def _select_connection(self, pgs: PlayerGameState, game_map: Map) -> Optional[Connection]:
        """
        Buy_Now player strategy for selecting the connection to acquire when attempting to make a connection on their turn.
        Selects the first connection from the lexicographically sorted list of given connections (unacquired connections)
        that the player has the necessary resources to acquire.
            Parameters:
                resources (PlayerGameState): the resources the player implementing this strategy has
            Returns:
                Connection to acquire if possible, None otherwise
        """

        all_acquired_connections = flatten_set([*pgs.other_acquisitions, pgs.connections])
        unacquired_connections: Set[Connection] = game_map.connections - all_acquired_connections
        sorted_connections = get_lexicographic_order_of_connections(
            list(unacquired_connections))

        for connection in sorted_connections:
            if can_acquire_connection(pgs, connection):
                return connection
        return None

    def get_player_move(self, pgs: PlayerGameState, game_map: Map) -> IPlayerMove:
        """
        Polls the Buy_Now player strategy for a move.  The logic here follows the strategy described
        above in the Hold_10 Class purpose statement.
            Return:
                A PlayerMove indicating a player's intended move
        """
        # Always attempt to acquire a connection
        desired_connection = self._select_connection(pgs, game_map)
        # If there are no acquireable connections then draw cards
        if desired_connection is None:
            return DrawCardMove()
        # Otherwise acquire the connection
        else:
            return AcquireConnectionMove(desired_connection)

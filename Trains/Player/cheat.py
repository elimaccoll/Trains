import sys

sys.path.append('../../')
from Trains.Common.map import City, Color, Connection, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.buy_now import Buy_Now
from Trains.Player.moves import AcquireConnectionMove, IPlayerMove


class Cheat(Buy_Now):
    """The Cheat strategy is like the Buy_Now strategy, but it attempts to acquire a non-existent
    connection the very first time a player is granted a turn."""

    _first_turn: bool

    def __init__(self) -> None:
        super().__init__()
        self._first_turn = True

    def _select_connection(self, player_game_state: PlayerGameState) -> Connection:
        """
        Returns a bogus connection that does not exist on a Map. This is considered an illegal move by the Referee.
            Returns:
                Connection that does not exist.
        """
        # A map can never contain a city with negative coordinates
        city1 = City("Asgard", -5, -5)
        city2 = City("Hades", -1, -1)
        return Connection(frozenset({city1, city2}), Color.BLUE, 5)

    def get_player_move(self, pgs: PlayerGameState, game_map: Map) -> IPlayerMove:
        """
        Attempts to acquire non-existent connection returned from the select_connection method
            Return:
                A PlayerMove indicating a player's intended move
        """
        if self._first_turn:
            self._first_turn = False

            desired_connection = self._select_connection(pgs)
            return AcquireConnectionMove(desired_connection)

        return super().get_player_move(pgs)

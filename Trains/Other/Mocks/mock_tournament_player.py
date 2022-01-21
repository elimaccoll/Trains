import sys
from typing import Optional

sys.path.append("../../../")
from Trains.Common.map import Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Other.Util.constants import DEFAULT_MAP
from Trains.Player.hold_10 import Hold_10
from Trains.Player.moves import IPlayerMove
from Trains.Player.player import StrategicPlayer
from Trains.Player.strategy import PlayerStrategyInterface


class MockTournamentPlayer(StrategicPlayer):
    """
    Mock Tournament Player used for testing that can be provided with a move to return on 'play', 
    a map to return on 'start', and a strategy to utilize during a game of Trains.
    """

    _move: Optional[IPlayerMove]
    _is_winner: Optional[bool]
    _is_tournament_winner: Optional[bool]

    def __init__(self, name: str, move: Optional[IPlayerMove] = None, start_game_map: Optional[Map] = None, strategy: PlayerStrategyInterface = Hold_10()):
        """
        Initializes an instance of a mock player
            Parameters:
                name (str): Player name
                move (IPlayerMove): Player's move to return on 'play'
                start_game_map (Map): Map to suggest on 'start'
                strategy (PlayerStrategyInterface): Player's strategy
        """
        super().__init__(name, strategy)
        self._move = move
        self._start_game_map = start_game_map if start_game_map is not None else DEFAULT_MAP
        self._is_winner = None
        self._is_tournament_winner = None

    def play(self, game_state: PlayerGameState) -> IPlayerMove:
        """
        The overridden play method for a mock player
            Parameters:
                game_state (PlayerGameState): the player game state
            Returns:
                (PlayerMove) the given move initialized in the constructor
        """
        if self.game_map is None:
            raise RuntimeError("Setup must be called before play.")

        if self._move is None:
            return self.strategy.get_player_move(game_state, self.game_map)
        return self._move

    def win(self, winner: bool) -> None:
        """
        Sets the is_winner field to given 'winner' boolean
            Parameters:
                winner (bool): Whether or not the player won (True) or lost (False)
        """
        self._is_winner = winner

    def start(self):
        return self._start_game_map

    def end(self, winner: bool):
        self._is_tournament_winner = winner


class MockTournamentPlayerNoMap(MockTournamentPlayer):
    """ Tournament player used for testing that always returns None on 'start' instead of a Map. """
    def start(self) -> Map:
        return None


class MockTournamentCheaterStart(MockTournamentPlayer):
    """ Tournament player used for testing that always raises a TimeoutError on 'start """
    def start(self) -> Map:
        raise TimeoutError


class MockTournamentCheaterEnd(MockTournamentPlayer):
    """ Tournament player used for testing that always raises a TimeoutError on 'end """
    def end(self, winner: bool) -> None:
        raise TimeoutError

import sys
from typing import Optional, Dict, Set

sys.path.append("../../../")
from Trains.Common.map import Destination, Map, Color
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.hold_10 import Hold_10
from Trains.Player.moves import DrawCardMove, IPlayerMove
from Trains.Player.player import StrategicPlayer


class MockBadSetUpPlayer(StrategicPlayer):
    """
    Mock Player used for testing.  Always raises TimeoutError on 'setup'
    """
    _move: IPlayerMove
    _is_winner: Optional[bool]

    def __init__(self, name: str):
        """
        Initializes an instance of a mock player
            Parameters:
                name (str): Player name
                age (int): Player age
        """
        super().__init__(name, Hold_10())
        self._move = DrawCardMove()
        self._is_winner = None

    def setup(self, map: Map, rails: int, cards: Dict[Color, int]) -> None:
        raise TimeoutError

    def play(self, player_game_state: PlayerGameState) -> IPlayerMove:
        """
        The overriden play method for a mock player
            Parameters:
                game_state (PlayerGameState): the player game state
            Returns:
                (PlayerMove) the given move initialized in the constructor
        """
        return self._move

    def win(self, winner: bool) -> None:
        """
        Sets the is_winner field to given 'winner' boolean
            Parameters:
                winner (bool): Whether or not the player won (True) or lost (False)
        """
        self._is_winner = winner

    def pick(self, destination_options: Set[Destination]) -> Set[Destination]:
        """
        Picks the first two destinations.
        """
        return set(list(destination_options)[:2])

import sys
from typing import Optional

sys.path.append("../../../")
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.buy_now import Buy_Now
from Trains.Player.hold_10 import Hold_10
from Trains.Player.moves import IPlayerMove
from Trains.Player.player import StrategicPlayer


class MockConfigurablePlayer(StrategicPlayer):
    """
    Mock Player used for testing.  Always returns the given PlayerMove.
    """

    _move: IPlayerMove
    _is_winner: Optional[bool]

    def __init__(self, name: str, move: IPlayerMove) -> None:
        """
        Initializes an instance of a mock player
            Parameters:
                name (str): Player name
                move (IPlayerMove): Player move to return on 'play'
        """
        super().__init__(name, Hold_10())
        self._move = move
        self._is_winner = None

    def play(self, player_game_state: PlayerGameState) -> IPlayerMove:
        """
        The overridden play method for a mock player
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


class MockBuyNowPlayer(StrategicPlayer):
    """
    Represents a player with the BuyNow strategy:
    - Always attempt to acquire a connection first
    - If there are no acquireable connections, then draw cards
    """

    _move: IPlayerMove
    _is_winner: Optional[bool]

    def __init__(self, name: str) -> None:
        """
        Constructor for the Buy_Now player strategy that takes in player name and player age.
        Uses the AbstractPlayer class constructor.
            Parameters:
                name (str): player name
                age (int): player age
        """
        super().__init__(name, Buy_Now())
        self._is_winner = None
        self._booted = False

    def win(self, winner: bool) -> None:
        """
        Sets the is_winner field to given 'winner' boolean
            Parameters:
                winner (bool): Whether or not the player won (True) or lost (False)
        """
        self._is_winner = winner

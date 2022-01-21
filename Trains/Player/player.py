import sys
from typing import Dict, Set, List, Optional

sys.path.append('../../')

from Trains.Common.map import Map, Color, Destination
from Trains.Common.player_game_state import PlayerGameState
from Trains.Other.Util.constants import DEFAULT_MAP
from Trains.Player.buy_now import Buy_Now
from Trains.Player.hold_10 import Hold_10
from Trains.Player.player_interface import PlayerInterface
from Trains.Player.strategy import (IPlayerMove, PlayerStrategyInterface,
                                    create_strategy_from_file_path)


class StrategicPlayer(PlayerInterface):
    """
    Abstract player class that contains methods relevant to all player for the setup of the game,
    gameplay during the game, and the end of the game.
    """
    NUMBER_OF_DESTINATIONS = 2

    strategy: PlayerStrategyInterface
    game_map: Optional[Map]

    def __init__(self, name: str, strategy: PlayerStrategyInterface) -> None:
        """
        Constructor for AbstractPlayer that takes in a player name and player age (some metric to determine turn order).
            Parameters:
                name (str): Player name
                age (int): Player age
        """
        if type(name) != str:
            raise TypeError("Name must be a string")

        self.name = name

        # The PlayerGameState for a given player that is initialized by Referee at start of game
        self.strategy = strategy
        self.game_map = None

    def setup(self, game_map: Map, rails: int, cards: Dict[Color, int]) -> None:
        """
        Sets the player up with a map, a number of rails, and a hand of cards.
            Parameters:
                - map (Map): The map of the game.
                - rails (int): The number of rails the player will start with.
                - cards (dict): The hand of cards the player starts with.
        """
        self.game_map = game_map

    def pick(self, destinations: Set[Destination]) -> Set[Destination]:
        """
        Given a set of destinations, the player picks two destinations and the three
        that were not chosen are returned.
            Parameters:
                destinations (set(Destination)): Set of five destinations to choose from.
            Return:
                A set(Destination) containing the three destinations the player did not pick.
        """
        chosen_destinations = self.strategy.select_destinations(
            destinations, self.NUMBER_OF_DESTINATIONS)
        return self._compute_destinations_to_return(destinations, chosen_destinations)

    def _compute_destinations_to_return(self, destinations_given: Set[Destination], destinations_chosen: Set[Destination]):
        """
        Given the destinations obtained by the player from the referee to pick from and the destinations
        the player chose, return a set containing the destinations the player will give back to the referee.
            Parameters:
                destinations_given (set(Destination)): The set of destinations the player picked from.
                destinations_chosen (set(Destination)): The set of destinations the player chose out of the ones given to them.
            Return:
                A set(Destination) the player will return to the referee.
        """
        return destinations_given - destinations_chosen

    def play(self, active_game_state: PlayerGameState) -> IPlayerMove:
        """
        Polls the player strategy for a move.
            Parameters:
                active_game_state (PlayerGameState): The game state of this player when they've become active.
            Return:
                A PlayerMove indicating a player's intended move
        """
        if self.game_map is None:
            raise RuntimeError("Setup must be called before play.")

        return self.strategy.get_player_move(active_game_state, self.game_map)

    def win(self, winner: bool) -> None:
        """
        Informs player that the game is over.  Tells players whether or not they won the game.
        ONLY CALLED ONCE(PER PLAYER) AT THE END OF THE GAME
            Parameters:
                winner (bool): True if this player won, False otherwise
        """
        pass

    def start(self) -> Map:
        return DEFAULT_MAP

    def more(self, cards: List[Color]) -> None:
        pass

    def end(self, winner: bool) -> None:
        pass

    def get_name(self) -> str:
        return self.name

    @staticmethod
    def create_player_from_strategy_file_path(file_path: str, name: str) -> 'StrategicPlayer':
        strategy = create_strategy_from_file_path(file_path)
        player = StrategicPlayer(name, strategy)
        return player


class Hold_10_Player(StrategicPlayer):
    """
    Represents a player with the following strategy:
    - Draw colored cards if the player contains 10 or fewer colored cards
    - If the player has more than 10 colored cards, then attempt to acquire a connection
    - If there are no acquireable connections for the player, then draw colored cards
    """

    def __init__(self, name: str) -> None:
        """
        Constructor for the Hold_10 player strategy that takes in player name and player age.
        Uses the AbstractPlayer class constructor.
            Parameters:
                name (str): player name
                age (int): player age
        """
        super().__init__(name, Hold_10())


class Buy_Now_Player(StrategicPlayer):
    """
    Represents a player with the following strategy:
    - Always attempt to acquire a connection first
    - If there are no acquireable connections, then draw cards
    """

    def __init__(self, name: str) -> None:
        """
        Constructor for the Buy_Now player strategy that takes in player name and player age.
        Uses the AbstractPlayer class constructor.
            Parameters:
                name (str): player name
                age (int): player age
        """
        super().__init__(name, Buy_Now())

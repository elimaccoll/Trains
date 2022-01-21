import sys
from abc import ABCMeta, abstractmethod
from typing import List, Set

sys.path.append('../../')
from Trains.Common.map import Destination, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Other.Util.func_utils import load_class_from_file
from Trains.Other.Util.map_utils import get_lexicographic_order_of_destinations
from Trains.Player.moves import IPlayerMove


class PlayerStrategyInterface(metaclass=ABCMeta):

    @abstractmethod
    def get_player_move(self, game_state: PlayerGameState, game_map: Map) -> IPlayerMove:
        """
        Returns move according to strategy.
            Return:
                A PlayerMove indicating a player's intended move
        """
        pass

    @abstractmethod
    def select_destinations(self, destinations: set, num_destinations: int) -> Set[Destination]:
        """
        Strategy for selecting their 2 destinations during the setup of the game.
            Parameters:
                destinations (set(Destination)): Destinations to choose 2 from according to the strategy above.
                num_destinations (int): number of destinations to pick, num_destinations <= len(destination)
            Returns:
                set(Destination): The set of destinations selected
            Throws:
                ValueError: num_destinations must be less than set size
        """
        pass


class AbstractPlayerStrategy(PlayerStrategyInterface):
    def select_destinations(self, destinations: Set[Destination], num_destinations: int) -> Set[Destination]:
        """
        Strategy for selecting their 2 destinations during the setup of the game.
            Parameters:
                destinations (set(Destination)): Destinations to choose 2.
                num_destinations (int): number of destinations to pick
            Returns:
                set(Destination): The set of destinations selected
            Throws:
                ValueError: num_destinations must be less than set size
        """

        if len(destinations) < num_destinations:
            raise ValueError(
                f"Given list of Destinations needs to contain at least {num_destinations} Destinations")

        sorted_dests = self._sort_destinations([*destinations])
        return {*sorted_dests[:num_destinations]}

    def _sort_destinations(self, destinations: List[Destination]) -> List[Destination]:
        """Sorts destinations. Can be overridden to change which destinations a strategy will select."""
        return get_lexicographic_order_of_destinations(destinations)


def create_strategy_from_file_path(file_path: str) -> PlayerStrategyInterface:
    StrategyClass = load_class_from_file(file_path)

    # assert the the discovered class inherits from IStrategy
    if not issubclass(StrategyClass, PlayerStrategyInterface):
        raise ValueError(
            "The class within the provided file must inherit from IStrategy")

    # assert the the discovered class is concrete (non-abstract)
    if not _is_concrete(StrategyClass):
        raise ValueError(
            "The class within the provided file must be concrete.")

    try:
        strategy = StrategyClass()  # type: ignore
    except:
        raise RuntimeError(
            f"Encountered error instantiating IStrategy provided at {file_path}")

    return strategy


def _is_concrete(cls: type) -> bool:
    return getattr(cls, "__abstractmethods__", set()) == set()

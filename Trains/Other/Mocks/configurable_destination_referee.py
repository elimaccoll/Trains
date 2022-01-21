import sys
from typing import Deque, List, Optional, Set

sys.path.append("../../../")
from Trains.Admin.referee import Referee
from Trains.Common.map import Color, Destination, Map
from Trains.Other.Util.map_utils import get_lexicographic_order_of_destinations
from Trains.Player.player_interface import PlayerInterface


class ConfigurableDestinationReferee(Referee):
    """
    A Referee with deterministic destination options when players are picking their destinations.
    Used by the ConfigurableDestinationManager to make tournament games deterministic.
    """
    def __init__(self, game_map: Map, players: List[PlayerInterface], deck: Optional[Deque[Color]] = None):
        super().__init__(game_map, players, deck)

    def get_destination_selection(self, feasible_destinations: Set[Destination], number_of_destinations: int) -> Set[Destination]:
        """
        Gets the subset of feasible destinations that a player will choose their destinations from on setup.
        This subset of destinations consists of the first `number_of_destinations` destinations in the
        lexicographical ordering of the given feasible destinations.
            Parameters:
                feasible_destinations (set(Destination)): Set of all feasible destinations on a game map
                number_of_destinations (int): The number of destinations that a player can select from
            Returns:
                (set(Destination)) The set of destinations that a player will select from
        """
        sorted_destinations = get_lexicographic_order_of_destinations(
            list(feasible_destinations))
        destination_options = set(sorted_destinations[:number_of_destinations])
        return destination_options

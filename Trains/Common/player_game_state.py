import json
import sys
from typing import Any, Dict, List, Set

sys.path.append('../../')
from Trains.Common.map import Color, Connection, Destination
from Trains.Other.Util.map_utils import (
    get_lexicographic_order_of_connections,
    get_lexicographic_order_of_destinations)


class PlayerGameState:
    """
    Represents a player game state through the resources available to a player, their
    acquired connections, destinations, and knowledge of other players.
        Parameters:
            connections (set): Set of a player's connections
            colored_cards (dict): Dictionary of a player's colored cards
            rails (int): The number of rail segments a player has
            destinations (set): A set of a player's 2 destinations
            other_acquisitions (list): A list of sets that tracks other players's connections.
    """
    _connections: Set[Connection]
    _colored_cards: Dict[Color, int]
    _rails: int
    _destinations: Set[Destination]
    _other_acquisitions: List[Set[Connection]]

    @property
    def connections(self) -> Set[Connection]:
        return {*self._connections}

    @property
    def colored_cards(self) -> Dict[Color, int]:
        return {**self._colored_cards}

    @property
    def rails(self) -> int:
        return self._rails

    @property
    def destinations(self) -> Set[Destination]:
        return {*self._destinations}

    @property
    def other_acquisitions(self) -> List[Set[Connection]]:
        return [{*acquired} for acquired in self._other_acquisitions]

    def __init__(self, connections: Set[Connection], colored_cards: Dict[Color, int], rails: int, \
        destinations: Set[Destination], other_acquisitions: List[Set[Connection]]) -> None:
        """
        Checks the validity of the PlayerResources dataclass fields
            Throws:
                ValueError:
                    - Connections must be a set
                    - Colored cards must be a dictionary
                    - Player game state must have 0 or more of a certain colored card
                    - Player game state must have 0 or more rails
                    - Destination must be a set
                    - game info must be a dictionary
                    - opponent info must be a list of dictionaries
        """
        if type(connections) is not set:
            raise TypeError("Connections must be a set")
        if type(colored_cards) is not dict:
            raise TypeError("Colored cards must be a dictionary")
        else:
            for num in colored_cards.values():
                if num < 0:
                    raise ValueError(
                        "The number of cards for a color cannot be negative")
        if rails < 0:
            raise ValueError("Player must have 0 or more rails")
        if type(destinations) is not set:
            raise TypeError("Destinations must be in a set")
        for destination in list(destinations):
            if type(destination) is not Destination:
                raise TypeError("Destinations must be of type Destination")
        if type(other_acquisitions) is not list:
            raise TypeError("other_acquisitions argument must be a list")
        else:
            if any(type(item) is not set for item in other_acquisitions):
                raise TypeError(
                    "All entries in the other_acquisitions list must be a set of connections.")

        self._connections = {*connections}
        self._colored_cards = {**colored_cards}
        self._rails = rails
        self._destinations = {*destinations}
        self._other_acquisitions = [{*acquired}
                                    for acquired in other_acquisitions]

    def get_total_cards(self) -> int:
        """
        Gets the total number of colored cards the player game state has.
            Returns:
                total (int): The total number of colored cards in the player game state
        """
        return sum(count for count in self.colored_cards.values())

    def get_as_json(self) -> str:
        """
        Returns the JSON string of PlayerResources dataclass
        Will put alphanumerically first connection/destination first in JSON
        """
        sorted_destination_list = get_lexicographic_order_of_destinations(
            list(self.destinations))
        destinations_as_cities = []
        for destination in sorted_destination_list:
            dest_cities = sorted(city.name for city in destination)
            destinations_as_cities.append(dest_cities)

        this_player: Dict[str, Any] = dict()
        this_player["destination1"] = destinations_as_cities[0]
        this_player["destination2"] = destinations_as_cities[1]
        this_player["rails"] = self.rails
        json_colored_cards = {color.value: amount for (
            color, amount) in self.colored_cards.items()}
        this_player["cards"] = json_colored_cards
        # Sort the 'this' acquireds lexicographically
        sorted_connections: List[Connection] = get_lexicographic_order_of_connections(
            list(self.connections))
        this_player["acquired"] = [json.loads(
            connection.get_as_json()) for connection in sorted_connections]

        opponent_acquireds: List[List[List[Any]]] = []
        for opp_acquisitions in self._other_acquisitions:
            # TODO: Haven't tested this when the field isn't an empty list
            sorted_one_opp_acquireds: List[Connection] = get_lexicographic_order_of_connections(
                list(opp_acquisitions))
            json_acquireds: List[List[Any]] = [json.loads(
                acquired.get_as_json()) for acquired in sorted_one_opp_acquireds]
            opponent_acquireds.append(json_acquireds)

        player_state: Dict[str, Any] = dict()
        player_state["this"] = this_player
        player_state["acquired"] = opponent_acquireds

        return json.dumps(player_state)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, PlayerGameState):
            return (o._other_acquisitions == self._other_acquisitions) \
                and (o._connections == self._connections) and (o._colored_cards == self._colored_cards) \
                and (o._rails == self._rails) and (o._destinations == self._destinations)
        return False

    def __hash__(self) -> int:
        connections_hash = sum(hash(conn)
                               for conn in self._connections)
        cc_hash = sum(hash((color, amount))
                      for color, amount in self._colored_cards.items())
        acquisitions_hash = sum(hash(conn)
                                for acquired in self._other_acquisitions for conn in acquired)
        dests_hash = sum(hash(dest)
                         for dest in self._destinations)
        return hash((connections_hash, acquisitions_hash, cc_hash, self._rails, dests_hash))

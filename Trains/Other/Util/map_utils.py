import sys
from functools import cmp_to_key
from typing import List

sys.path.append('../../')
from Trains.Common.map import Connection, Destination, Map


def verify_game_map(game_map: Map, num_players: int, num_destination_options: int, num_destinations_per_player: int) -> bool:
    """
    Verifies whether or not a given map can be used by a given number of players based on the number of.
    feasible destinations that can be formed.
        Parameters:
            game_map (Map): the game map that is being verified
            num_players (int): The number of players that would be using the given map
            num_destination_options (int): The number of destinations a player gets to choose from
            num_destinations_per_player (int): The number of destinations that a player chooses
        Returns:
            True if the map can be used with the given number of players. False Otherwise.
    """
    return len(game_map.get_all_feasible_destinations()) \
        >= num_destination_options + (num_destinations_per_player * (num_players - 1))


def get_lexicographic_order_of_destinations(destinations: List[Destination]) -> List[Destination]:
    """
    Gets the lexicographic order of a given list of destinations.  Initially sorts by the first city in each destination, and resorts
    to the second city name in each destination if the first city names are equal.
        Parameters:
            destinations (list(Destination)): The list of destinations to sort in lexicographic order
        Returns:
            The lexicographically sorted list of given destinations
    """
    # Uses the special method __lt__ (less than) written in the Destination dataclass to sort
    destinations.sort(key=cmp_to_key(Destination.__lt__))
    return destinations


def get_lexicographic_order_of_connections(connections: List[Connection]) -> List[Connection]:
    """
    Gets the lexicographic order of a given list of connections.  Initially sorts by the first city in each connection, and resorts
    to the second city name in each connection if the first city names are equal.  If both pairs of city names are equal, then the order is
    determined by ascending order of number of segments (length of the connections), and finally the lexicographic order of the string
    representations of the connection color ("red", "green", "white", and "blue") if a tie-breaker for number of segments is required.
        Parameters:
            connections (list(Connection)): The list of connections to sort in lexicographic order
        Returns:
            The lexicographically sorted list of given connections
    """
    # Uses the special method __lt__ (less than) written in the Connection dataclass to sort
    connections.sort(key=cmp_to_key(Connection.__lt__))
    return connections

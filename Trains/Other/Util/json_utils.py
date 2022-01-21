import json
import math
import sys
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast

sys.path.append('../../')
from Trains.Common.map import City, Color, Connection, Destination, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Other.Mocks.mock_tournament_player import MockTournamentPlayer
from Trains.Player.player_interface import PlayerInterface
from Trains.Player.strategy import create_strategy_from_file_path

JSONMap = Dict[str, Any]
"""JSONMap is:
::

    {"width"        : Width,
    "height"       : Height,
    "cities"       : [City,..,City],
    "connections"  : JSONConnections }
"""

JSONSegment = Dict[str, int]
"""A Segment is an object whose domain elements are Colors
and whose range elements are Lengths.

CONSTRAINT: The Colors must be pairwise distinct.

INTERPRETATION: specifies the color and length of a connection"""

JSONTarget = Dict[str, JSONSegment]
"""A Target is an object whose domain elements are Names
and whose range elements are Segments.

CONSTRAINT: Every Name must be a member of the Names in the "cities" field.

INTERPRETATION: specifies where a connection goes (domain)
and their nature (range)"""

JSONConnections = Dict[str, JSONTarget]
"""JSONConnections is an object whose domain elements are Names
and whose range elements are Targets.

CONSTRAINT: Every Name must be a member of the Names in the "cities" field.
The domain name must be string<? to the range's name.

INTERPRETATION: specifies from where connection originates (domain),
to where they go and the nature of the connection (range)"""

JSONCity = Tuple[str, Tuple[int, int]]
"""JSONCity is
::

    [Name, [X, Y]]

where X is a natural number
in [0,W] and Y is a natural number in [0,H] with W and H as specified
in the map object's "width" and "height" fields, respectively.

CONSTRAINT: No two cities may have the same name or occupy the same spot.

INTERPRETATION: specifies a city's name and location on the map"""

JSONPlayerState = Dict[str, Any]
"""JSONPlayerState is an object: ::

      { "this" : JSONThisPlayer, "acquired" : [JSONPlayer, ..., JSONPlayer]}

INTERPRETATION: The object describes the state of the now-active player itself and
as much as it can know about the remaining players, plus the order in which
hey take turns.
This information is exactly what is available to every player in a physical
version of the game. If your game state represents more information than that,
your deserialization program must compute it from here."""

JSONThisPlayer = Dict[str, Any]
"""ThisPlayer is an object: ::

    {"destination1" : JSONDestination,
    "destination2" : JSONDestination,
    "rails"        : Natural,
    "cards"        : JSONColor*
    "acquired"     : JSONPlayer}

INTERPRETATION: describes the state of the player: its chosen destination
cards, its number of rails, its colored cards, and its acquired connections
"""

JSONAcquired = List[Any]
"""Acquired is ::

[Name, Name, Color, Length]"""

JSONPlayer = List[JSONAcquired]
"""Player is a JSON array of `JSONAcquireds`."""

JSONDestination = List[str]
"""Destination is a: ::

[Name, Name]"""

JSONColor = str
"""JSONColor is a Json string representing a color:
::

    - "blue"
    - "red"
    - "white"
    - "green"
"""

JSONCards = Dict[JSONColor, int]
"""JSONCards is an object whose domain elements are Colors
and whose range elements are natural numbers."""

JSONAction = Union[str, JSONAcquired]
"""An JSONAction is one of:
::
    - the string "more cards"
    - a JSONAcquired.
"""
JSONPlayerName = str
"""A JSONPlayerName is a non-empty String of maximally 50
lower- or upper-case alphabetical chars ([A-Za-z]).
"""


class JSONStrategy(str, Enum):
    """A JSONStrategy is one of the following three JSON strings:
    ::
        - "Hold-10"
        - "Buy-Now"
        - "Cheat"
    """
    HOLD10 = "Hold-10"
    BUYNOW = "Buy-Now"
    CHEAT = "Cheat"


JSONPlayerInstance = List[str]
"""A JSONPlayerInstance is a JSON array of two values:
::
      [JSONPlayerName, JSONStrategy]"""

JSONRank = List[JSONPlayerName]
""" A JSONRank is a JSON array of JSONPlayerNames sorted according to `string<?`."""

JSONRanking = List[JSONRank]
"""A JSONRanking is an array of JSONRanks.
INTERPRETATION: The ith array contains the PlayerNames of all
ith-place finishers. An ith-place finisher is a player that has the ith-highest score."""

JSONColors = List[JSONColor]
"""A JSONColors is a list of JSONColor"""


def separate_json_inputs(input: str) -> List[str]:
    """
    Separates JSON values from given input source.
        Parameters:
            input (str): Series of JSON values
        Returns:
            List of JSON values
    """
    open_objects = 0
    open_lists = 0
    starting_place = 0
    in_string = False
    outputs = []

    for i in range(len(input)):
        if input[i] == "\"":
            in_string = not in_string
        elif input[i] == "{" and not in_string:
            open_objects += 1
        elif input[i] == "}" and not in_string:
            open_objects -= 1
        elif input[i] == "[" and not in_string:
            open_lists += 1
        elif input[i] == "]" and not in_string:
            open_lists -= 1
        elif input[i] == " " and not in_string and open_lists == 0 and open_objects == 0:
            outputs.append(input[starting_place:i])
            starting_place = i + 1

    outputs.append(input[starting_place:])
    return outputs


def convert_dict_hand_to_json_hand(dict_hand: Dict[Color, int]) -> str:
    list_hand: List[str] = []
    for color, num in dict_hand.items():
        list_hand.extend([color.value] * num)
    json_hand = json.dumps(list_hand)
    return json_hand


def convert_json_map_to_data_map(json_map: JSONMap) -> Map:
    """
    Parses the given map into existing internal data definitions.
        Parameters:
            json_map (dict): Map from given input
        Returns:
            Internal Map data definition of given_map
    """
    width: int = json_map["width"]
    height: int = json_map["height"]
    json_cities: List[JSONCity] = json_map["cities"]
    json_connections: JSONConnections = json_map["connections"]
    cities = set()
    cities_dict = {}
    for json_city in json_cities:
        city_struct = City(json_city[0], math.floor(
            json_city[1][0] * 100 / width), math.floor(json_city[1][1] * 100 / height))
        cities.add(city_struct)
        cities_dict[json_city[0]] = city_struct
    connections = set()
    for connection, target in json_connections.items():
        city1 = cities_dict[connection]
        for city in target.keys():
            city2 = cities_dict[city]
            for color in target[city].keys():
                color_str = cast(str, color)
                connections.add(Connection(
                    frozenset({city1, city2}), Color(color_str), target[city][color]))
    return Map(cities, connections, height, width)


def convert_json_city_to_data(city_name: str, game_map: Map) -> City:
    """
    Uses a given city name and a given map to create a City object representation of the city name and it's corresponding information (position).
        Parameters:
            city_name (str): The name of the city being converted to a City object
            game_map (Map): The Map that the city_name is from
        Returns:
            The City object representation of the given city name
        Raises:
            ValueError when the city name is no associated with the given map
    """
    for city in game_map.get_all_cities():
        if city.name == city_name:
            return city
    raise ValueError("City not on map")


def convert_json_destinations_to_data(json_destination: JSONDestination, destinations: Set[Destination]) -> Destination:
    """
    Uses a given dictionary representation of a player state and the corresponding Map to create an internal data representation of a player destination
        Parameters:
            json_player_state (dict): The dictionary representation of a player game state being using to create a set of the player's destinations
            destinations (set(Destination)): The possible destinations on a game map that the given json_destination is associated with
        Returns:
            Destination from the given json destination
    """
    if len(json_destination) != 2:
        raise ValueError("Bad JSON Destination")

    dest_names = set(json_destination)
    for destination in destinations:
        destination_name_set = {city.name for city in destination}
        if dest_names == destination_name_set:
            return destination
    raise ValueError("Destination is not in given destination")


def convert_json_connection_to_data(json_connection: JSONAcquired, game_map: Map) -> Connection:
    """
    Creates an internal data representation of a Connection using a given json representation of a connection and the Map it is associated with
        Parameters:
            json_connection (list): The list representation of a connection [Name, Name, Color, Length]
            game_map (Map): The Map that the given connection is associated with
        Returns:
            Connection representation of the given json_connection
    """
    city1, city2, color_str, length = json_connection
    city1 = convert_json_city_to_data(city1, game_map)
    city2 = convert_json_city_to_data(city2, game_map)
    return Connection(frozenset({city1, city2}), Color(color_str), length)


def convert_data_connection_to_acquired(data_connection: Connection) -> str:
    """
    Converts a Connection to a JSONAcquired, which is string reprsentation of Connection that looks like: [Name, Name, Color, Length].
    """
    city1, city2 = list(data_connection.cities)

    if city1.name < city2.name:
        name1 = city1.name
        name2 = city2.name
    else:
        name1 = city2.name
        name2 = city1.name

    color = data_connection.color.value
    length = data_connection.length

    return f"[\"{name1}\", \"{name2}\", \"{color}\", {length}]"


def convert_json_this_player_to_data(json_player_state: JSONPlayerState, game_map: Map) -> PlayerGameState:
    """
    Uses a given dictionary representation of a player state and the corresponding Map to create an 
    internal data representation of a player game state (PlayerGameState).
        Parameters:
            json_player_state (dict): The dictionary representation of a player game state 
                                      being using to create a PlayerGameState object.
            game_map (Map): The Map that the given player game state is associated with.
        Returns:
            PlayerGameState representation of the given json_player_state
    """
    this_player: JSONThisPlayer = json_player_state["this"]

    all_feasible_destinations = game_map.get_all_feasible_destinations()
    destination1 = convert_json_destinations_to_data(
        this_player["destination1"], all_feasible_destinations)
    destination2 = convert_json_destinations_to_data(
        this_player["destination2"], all_feasible_destinations)
    destinations = set({destination1, destination2})

    rails: int = this_player["rails"]
    colored_cards = {Color.RED: 0, Color.BLUE: 0,
                     Color.GREEN: 0, Color.WHITE: 0}

    card_amounts: List[Tuple[str, int]] = this_player["cards"].items()
    for color_str, amount in card_amounts:
        colored_cards[Color(color_str)] = amount

    this_acquireds = this_player["acquired"]
    connections = {convert_json_connection_to_data(
        acquired, game_map) for acquired in this_acquireds}
    available_connections = game_map.get_all_connections() - connections

    opponents: List[JSONAcquired] = json_player_state["acquired"]
    other_acquisitions: List[Set[Connection]] = []
    for opponent in opponents:
        one_opponent_connections = set()
        for acquired in opponent:
            connection = convert_json_connection_to_data(
                acquired, game_map)
            one_opponent_connections.add(connection)
            available_connections = available_connections - set({connection})
        other_acquisitions.append(one_opponent_connections)

    return PlayerGameState(connections, colored_cards, rails, destinations, other_acquisitions)


def convert_json_player_state_to_data(json_player_state: JSONPlayerState, game_map: Map) -> Tuple[PlayerGameState, Set[Connection]]:
    """
    Uses a given dictionary representation of a player state and the corresponding Map to create an internal data representation of a
    player game state (PlayerGameState).  Also uses the list of acquired connections in the given json_player_state to create internal
    data representations of Connections for those acquired connections.
        Parameters:
            json_player_state (dict): The dictionary representation of a player game state
            game_map (Map): The Map that the given player game state is associated with
        Returns:
            PlayerGameState representation of the given json_player_state, set of Connections
            representing the acquired connections according to the given json_player_state
    """
    player_resources = convert_json_this_player_to_data(
        json_player_state, game_map)
    other_connections = set()
    for json_connection in json_player_state["acquired"]:
        for sub_connection in json_connection:
            connection = convert_json_connection_to_data(
                sub_connection, game_map)
            other_connections.add(connection)
    return player_resources, other_connections


def convert_json_players_to_player_list(json_player_instances: List[JSONPlayerInstance], game_map: Optional[Map] = None) -> List[PlayerInterface]:
    """
    Given a list of JSON representation Player instances, convert that list (contains player and strategy names)
    to a list of Players to hand to a Referee.
        Parameters:
            json_player_instances (list): A list of length-two arrays containing a Player name and Strategy name, in that order.
            game_map (Map): An optional parameter that represents the map for the player to suggest to the manager in a tournament
        Returns:
            A list of Players in the order of the given instance list to hand to a Referee.
    """
    return [_create_configured_player_from_player_instance(player_instance, game_map)
            for player_instance in json_player_instances]


def _create_configured_player_from_player_instance(player_instance: JSONPlayerInstance, start_game_map: Optional[Map] = None) -> PlayerInterface:
    player_name, strategy_type = player_instance
    strategy = create_strategy_from_file_path(
        get_strategy_file_path(strategy_type))

    return MockTournamentPlayer(player_name, start_game_map=start_game_map, strategy=strategy)


def get_strategy_file_path(strategy: str) -> str:
    PATH_START = "../Trains/Player/"
    file_name: str
    if strategy == "Hold-10":
        file_name = "hold_10"
    elif strategy == "Buy-Now":
        file_name = "buy_now"
    elif strategy == "Cheat":
        file_name = "cheat"
    else:
        raise ValueError(f"Unknown strategy type: {strategy}")

    return PATH_START + file_name + ".py"


def convert_json_colored_cards_list_to_colored_cards_dict(colors: JSONColors) -> Dict[Color, int]:
    result = {Color.RED: 0, Color.GREEN: 0, Color.BLUE: 0, Color.WHITE: 0}
    for color in colors:
        result[Color(color)] += 1
    return result

# def convert_connections_to_json_acquired(connections: Set[Connection]) -> List[str, str, str, int]:
#     json_acquired = []
#     for connection in connections:
#         connection_city_names = [city.name for city in connection.cities]
#         connection_city_names.sort()
#         json_connection = [connection_city_names[0],
#                         connection_city_names[1], connection.color.value, connection.length]
#         json_acquired.append(json_connection)
#     return json.dumps(json_acquired)

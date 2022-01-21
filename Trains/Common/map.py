import functools
import json
import sys
from collections import deque
from dataclasses import dataclass
from enum import Enum
from math import floor
from typing import Deque, Dict, FrozenSet, Iterable, List, Set

sys.path.append('../../')
from Trains.Other.Util.func_utils import memoize


class Color(Enum):
    """
    A enumeration of the possible connection colors in Trains
    """
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    WHITE = "white"

    @property
    def value(self) -> str:
        """Returns the string representation of the color.

        Asserts that `.value` returns a string."""
        return super().value

    def get_as_json(self):
        return json.dumps(self.value)

    @classmethod
    def number_of_colors(cls) -> int:
        return len(cls)


@dataclass(frozen=True)
class City:
    """A city represented by its name and its relative position
    within the bounding box of a Map."""

    name: str
    x: float
    y: float

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("City name must be a string")

    def get_as_json(self) -> str:
        """
        Returns the JSON string of City dataclass
        """
        return f"[\"{self.name}\", [{self.x}, {self.y}]]"


@dataclass(frozen=True)
class Connection:
    """
    Represents a connection by the cities connected, color, and length
    Cities must be 2 distinct cities
    """
    cities: FrozenSet[City]
    color: Color
    length: int

    def __post_init__(self) -> None:
        """
        Checks validity of dataclass fields
            Throws:
                ValueError:
                    - Dataclass fields must be the correct corresponding type
                    - The cities set must contain exactly 2 cities
                    - The color must be a supported color (red, green, blue, or white)
                    - The length must be 3, 4, or 5
        """
        if type(self.cities) is not frozenset:
            raise ValueError("Cities must be a frozen set")
        elif len(self.cities) != 2:
            raise ValueError("Connections conatain exactly 2 distinct cities")
        else:
            for city in self.cities:
                if type(city) != City:
                    raise ValueError("Cities must be of type City")

        if type(self.color) is not Color:
            raise ValueError("Color must be a supported color")

        if self.length not in (3, 4, 5):
            raise ValueError("Length must be one of 3, 4, or 5")

    def __lt__(self, obj: object) -> int:
        """
        Special method for the 'less than' operator when comparing two Connections.
        Comparisons are done by first city name with tie breakers in the following order:
        second city name, connection length, and finally color (string).
            Parameters:
                self (Connection): The first connection
                obj (Connection): The second connection
            Returns:
                -1 if the first connection (self) is less than the other connection (obj), 1 Otherwise
        """
        if type(obj) is not Connection:
            raise ValueError(
                "Cannot compare Connection to something else that is not a Connection.")

        list_self = list(self.cities)
        if list_self[1].name < list_self[0].name:
            list_self[0], list_self[1] = list_self[1], list_self[0]
        list_obj = list(obj.cities)
        if list_obj[1].name < list_obj[0].name:
            list_obj[0], list_obj[1] = list_obj[1], list_obj[0]

        if list_self[0].name < list_obj[0].name:
            return -1
        elif list_self[0].name == list_obj[0].name and list_self[1].name < list_obj[1].name:
            return -1
        elif list_self[0].name == list_obj[0].name and list_self[1].name == list_obj[1].name and self.length < obj.length:
            return -1
        elif list_self[0].name == list_obj[0].name and list_self[1].name == list_obj[1].name and \
                self.length == obj.length and self.color.value < obj.color.value:
            return -1
        else:
            return 1

    def get_as_json(self) -> str:
        """
        Returns the JSON string of Connection dataclass
        Will put alphanumerically first city first in JSON
        """
        connection_city_names = sorted(city.name for city in self.cities)
        json_connection = [connection_city_names[0],
                           connection_city_names[1], self.color.value, self.length]
        return json.dumps(json_connection)


class Destination(FrozenSet[City]):
    """
    A Destination is a set of exactly two distinct cities.  Subclasses the frozenset class.
    """

    def __init__(self, cities: FrozenSet[City]) -> None:
        """
        Checks validity of cities in a destination.
            Throws:
                ValueError: Cities must be a set of exactly 2 cities
        """
        if not isinstance(cities, (frozenset, set)):
            raise TypeError("Cities must be a frozenset")
        if len(cities) != 2:
            raise ValueError("Destinations hold exactly 2 cities")
        else:
            for city in cities:
                if type(city) is not City:
                    raise ValueError("Destinations must contain cities")

    def __lt__(self, obj: object) -> int:
        """
        Special method for the 'less than' operator when comparing two Destinations.
        Sorts the cities in a each destination by name and then compares them by first city name.
        Uses second city name as a tie breaker.
            Parameters:
                self (Destination): The first destination
                obj (Destination): The second destination
            Returns:
                -1 if the first destination (self) is less than the other destination (obj), 1 Otherwise
        """
        if type(obj) is not Destination:
            raise ValueError(
                "Cannot compare Destination to something else that is not a Destination.")

        list_self = list(self)
        if list_self[1].name < list_self[0].name:
            list_self[0], list_self[1] = list_self[1], list_self[0]
        list_obj: List[City] = list(obj)
        if list_obj[1].name < list_obj[0].name:
            list_obj[0], list_obj[1] = list_obj[1], list_obj[0]

        if list_self[0].name < list_obj[0].name:
            return -1
        elif list_self[0].name == list_obj[0].name and list_self[1].name < list_obj[1].name:
            return -1
        else:
            return 1

    def get_as_json(self) -> str:
        """
        Returns the JSON string of Destination dataclass
        Will put alphanumerically first city first in JSON
        """
        return json.dumps(sorted([city.name for city in self]))


class Map:
    """
    Represents the game map for a game of trains. A master map object
    should be held by the Referee and a deep copy of the map should be
    passed to players to prevent tampering. A map also has a width and height,
    which represent its display size.
    """

    _cities: Set[City]
    _connections: Set[Connection]
    _width: int
    _height: int

    @property
    def cities(self) -> Set[City]:
        return {*self._cities}

    @property
    def connections(self) -> Set[Connection]:
        return {*self._connections}

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def __init__(self, cities: Iterable[City], connections: Iterable[Connection], width: int = 800, height: int = 800) -> None:
        """
        Map constructor that checks the validity of arguments before assignment.
            Throws:
                ValueError:
                    - The width and height of the canvas must each be in the range [10, 800]
                    - Cities and connections must be sets
                    - Cities used in connections must be present in the cities set
        """
        if width < 10 or width > 800 or height < 10 or height > 800:
            raise ValueError(
                "Width and height must each be in the range [10, 800]")

        if type(connections) != set:
            raise ValueError("Connections must be a set")
        if type(cities) != set:
            raise ValueError("Cities must be a set")

        if any(is_out_of_bounds(city, width, height) for city in cities):
            raise ValueError(
                "All cities must be within the bounding box the Map.")

        connected_cities = {
            city for conn in connections for city in conn.cities}
        all_connected_cities_known = all(
            city in cities for city in connected_cities)

        if not all_connected_cities_known:
            raise ValueError(
                "Cities in connections must be in cities set")

        self._cities = {*cities}
        self._connections = {*connections}
        self._width = width
        self._height = height

    def get_city_names(self) -> Set[str]:
        """
        Returns the names of all the cities
                Returns
                    (set): All names of cities as a set
        """
        return {city.name for city in self._cities}

    def get_cities_from_connections(self, connections: Set[Connection]) -> Set[City]:
        """
        Returns all the cities in given connections as a set
                Returns
                    (set): All cities as a set
        """

        return {city for conn in connections for city in conn.cities}

    # TODO: Getters may be redundant now that Map is a dataclass
    def get_all_cities(self) -> Set[City]:
        """
        Returns all the cities on the map as a set
                Returns
                    (set): All cities on the map as a set
        """
        return {*self.cities}

    def get_all_connections(self) -> Set[Connection]:
        """
        Returns all the connections on the map as a set
                Returns
                    (set): All connections on the map as a set
        """
        return self.connections

    def get_all_feasible_destinations(self) -> Set[Destination]:
        """
        Returns a copy of all feasible destinations that can be made from the map's connections
            Returns
                (set(Destination)): All possible destinations in the map
        """
        return {*self._get_all_feasible_destinations_memoed()}

    @memoize
    def _get_all_feasible_destinations_memoed(self) -> Set[Destination]:
        """
        Returns all feasible destinations that can be made from the map's connections
        This is an internal memoized version of the function.
            Returns
                (set(Destination)): All possible destinations
        """
        return self.get_feasible_destinations(self._connections)

    def get_feasible_destinations(self, connections: Set[Connection]) -> Set[Destination]:
        """
        Returns all feasible destinations from a subset of map connections
        A Destination is a frozenset of cities that are connected via some
        path on the map.
            Parameters:
                connections (set(Connection)): set of connections on map
            Returns
                (set(Destination)): All possible destinations from subset of connections
        """
        starting_cities = self.get_cities_from_connections(connections)
        destinations: Set[Destination] = set()
        for city in starting_cities:
            terminal_cities = self.get_all_terminal_cities_from_city(
                city, connections)
            for terminal_city in terminal_cities:
                destinations.add(Destination(frozenset({city, terminal_city})))

        return destinations

    def get_all_terminal_cities_from_city(self, city: City, connections: Set[Connection]) -> List[City]:
        """
        Finds the list of cities that can be reached from a given starting city
        within a set of connections
            Parameters:
                city (City): The starting city
                connections (set(Connection)): The connections a player owns
            Returns:
                a list of cities (list(City))
        """
        visit_q: Deque[City] = deque()
        visit_q.append(city)
        visited = []
        all_connection_cities = [
            connection.cities for connection in connections]

        while len(visit_q) > 0:
            current_city = visit_q.popleft()
            visited.append(current_city)

            for connection_cities in all_connection_cities:
                if current_city in connection_cities:
                    for neighbor in connection_cities:
                        if neighbor not in visited:
                            visit_q.append(neighbor)

        visited.remove(city)
        return visited

    def get_as_json(self) -> str:
        """
        Returns the JSON string of Map dataclass
        Will put alphanumerically first city/connection first in JSON
        """
        city_json = []
        for city in self.cities:
            city_json.append(
                f"[\"{city.name}\", [{floor(city.x * self.width / 100)}, {floor(city.y * self.height / 100)}]]")
        city_json.sort()

        connections_dict: Dict[str, Dict[str, Dict[str, int]]] = dict()
        connections_list = list(self.connections)
        connections_list.sort(key=functools.cmp_to_key(Connection.__lt__))
        for connection in connections_list:
            connection_cities_json = []
            for city in connection.cities:
                connection_cities_json.append(city.name)
            connection_cities_json.sort()
            city1 = connection_cities_json[0]
            city2 = connection_cities_json[1]
            if city1 not in connections_dict.keys():
                connections_dict[city1] = {
                    city2: {connection.color.value: connection.length}}
            else:
                if city2 not in connections_dict[city1].keys():
                    connections_dict[city1][city2] = {
                        connection.color.value: connection.length}
                else:
                    connections_dict[city1][city2][connection.color.value] = connection.length

        return f"{{\"cities\": [{', '.join(city_json)}], \"connections\": {json.dumps(connections_dict)}, \"height\": {self.height}, \"width\": {self.width}}}"

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, Map):
            return (obj.cities, obj.connections, obj.width, obj.height) == (self.cities, self.connections, self.width, self.height)
        return False

    def __hash__(self) -> int:
        cities_hash = sum(hash(city) for city in self.cities)
        connections_hash = sum(hash(connection)
                               for connection in self.connections)
        return hash((cities_hash, connections_hash, self.width, self.height))


def is_out_of_bounds(city: City, width: int, height: int) -> bool:
    cx = city.x
    cy = city.y
    return cx < 0 or cx > width or cy < 0 or cy > height

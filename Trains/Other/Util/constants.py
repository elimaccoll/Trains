import sys

sys.path.append('../../')
from Trains.Common.map import City, Color, Connection, Map

# Conversion table from int to Color for generating random colored cards
int2color = {
    1: Color.RED,
    2: Color.BLUE,
    3: Color.GREEN,
    4: Color.WHITE
}

MIN_RAILS_TO_NOT_TRIGGER_LAST_TURN = 3

# Default map for a game of trains if no valid map is provided on Manager 'start'
boston = City("Boston", 70, 80)
new_york = City("New York", 60, 70)
philadelphia = City("Philadelphia", 90, 10)
los_angeles = City("Los Angeles", 0, 10)
austin = City("Austin", 50, 10)
wdc = City("Washington D.C.", 55, 60)
boise = City("Boise", 30, 50)

connection1 = Connection(
    frozenset({boston, new_york}), Color.BLUE, 3)
connection2 = Connection(
    frozenset({boston, new_york}), Color.RED, 3)
connection3 = Connection(
    frozenset({boston, new_york}), Color.GREEN, 3)
connection4 = Connection(
    frozenset({boston, new_york}), Color.WHITE, 3)
connection5 = Connection(
    frozenset({philadelphia, new_york}), Color.RED, 4)
connection6 = Connection(
    frozenset({philadelphia, new_york}), Color.GREEN, 4)
connection7 = Connection(
    frozenset({philadelphia, new_york}), Color.WHITE, 4)
connection8 = Connection(
    frozenset({boston, philadelphia}), Color.GREEN, 4)
connection9 = Connection(
    frozenset({boston, philadelphia}), Color.BLUE, 4)
connection10 = Connection(
    frozenset({austin, los_angeles}), Color.BLUE, 5)
connection11 = Connection(
    frozenset({philadelphia, wdc}), Color.WHITE, 5)
connection12 = Connection(
    frozenset({austin, boise}), Color.RED, 5)
connection13 = Connection(
    frozenset({boise, los_angeles}), Color.GREEN, 5)
connection14 = Connection(
    frozenset({boise, philadelphia}), Color.RED, 5)
connection15 = Connection(
    frozenset({boise, wdc}), Color.GREEN, 5)

cities = {boston, new_york, philadelphia,
          los_angeles, austin, wdc, boise}
connections = {connection1, connection2, connection3, connection4, connection5, connection6, connection7,
               connection8, connection9, connection10, connection11, connection12, connection13, connection14, connection15}
width = 800
height = 800

DEFAULT_MAP = Map(cities, connections, height, width)

# Invalid Small Map
small_connection1 = Connection(
    frozenset({austin, boston}), Color.RED, 5)
small_connection2 = Connection(
    frozenset({boston, new_york}), Color.BLUE, 3)
small_connection3 = Connection(
    frozenset({new_york, philadelphia}), Color.GREEN, 4)

small_cities = {austin, boston, philadelphia, new_york}
small_connections = {small_connection1, small_connection2, small_connection3}
INVALID_SMALL_MAP = Map(small_cities, small_connections, height, width)

# Valid map with several connections, but only one of them is "red"
connection5_blue = Connection(
    frozenset({philadelphia, new_york}), Color.BLUE, 4)
connection12_white = Connection(
    frozenset({austin, boise}), Color.WHITE, 5)
connection14_green = Connection(
    frozenset({boise, philadelphia}), Color.GREEN, 5)

one_red_connection_map_connections = {connection1, connection2, connection3, connection4, connection5_blue, connection6, connection7,
                                      connection8, connection9, connection10, connection11, connection12_white, connection13, connection14_green, connection15}
ONE_RED_CONNECTION_MAP = Map(
    cities, one_red_connection_map_connections, width, height)

import sys

sys.path.append('../../../')

import unittest

from Trains.Common.map import City, Color, Connection, Destination, Map


class TestColors(unittest.TestCase):
    def test_enum_equality(self):
        self.assertEqual(Color.RED, Color.RED)
        self.assertNotEqual(Color.RED, Color.BLUE)

    def test_color_value(self):
        self.assertEqual(Color.RED.value, "red")
        self.assertEqual(Color.BLUE.value, "blue")
        self.assertEqual(Color.GREEN.value, "green")
        self.assertEqual(Color.WHITE.value, "white")

    def test_get_number_of_colors(self):
        self.assertEqual(Color.number_of_colors(), 4)

    def test_get_as_json(self):
        self.assertEqual(Color.RED.get_as_json(), "\"red\"")
        self.assertEqual(Color.BLUE.get_as_json(), "\"blue\"")
        self.assertEqual(Color.GREEN.get_as_json(), "\"green\"")
        self.assertEqual(Color.WHITE.get_as_json(), "\"white\"")


class TestCities(unittest.TestCase):
    def test_constructor(self):
        boston = City("Boston", 70, 80)
        new_york = City("New York", 60, 70)

        self.assertEqual(boston.name, "Boston")
        self.assertEqual(boston.x, 70)
        self.assertEqual(boston.y, 80)

        self.assertEqual(new_york.name, "New York")
        self.assertEqual(new_york.x, 60)
        self.assertEqual(new_york.y, 70)

    def test_constructor_invalid_name_type(self):
        with self.assertRaises(TypeError):
            bad_city = City(1, 50, 60)

    def test_city_as_json(self):
        boston = City("Boston", 70, 80)
        self.assertEqual(boston.get_as_json(), f"[\"Boston\", [70, 80]]")


class TestConnections(unittest.TestCase):
    def setUp(self):
        self.boston = City("Boston", 70, 80)
        self.new_york = City("New York", 60, 70)
        self.philadelphia = City("Philadelphia", 60, 70)
        self.connection1 = Connection(
            frozenset({self.boston, self.new_york}), Color.BLUE, 3)
        self.connection2 = Connection(
            frozenset({self.boston, self.philadelphia}), Color.RED, 4)
        self.connection3 = Connection(
            frozenset({self.boston, self.philadelphia}), Color.GREEN, 4)
        self.connection4 = Connection(
            frozenset({self.boston, self.philadelphia}), Color.RED, 3)
        self.connection5 = Connection(
            frozenset({self.new_york, self.philadelphia}), Color.WHITE, 5)

    def test_constructor(self):
        boston = City("Boston", 70, 80)
        new_york = City("New York", 60, 70)
        test_connection = Connection(
            frozenset({boston, new_york}), Color.BLUE, 3)

        self.assertEqual(test_connection.cities, {new_york, boston})
        self.assertEqual(test_connection.color, Color.BLUE)
        self.assertEqual(test_connection.length, 3)

    def test_invalid_constructor_invalid_length(self):
        with self.assertRaises(ValueError):
            Connection(frozenset([self.boston, self.new_york]), Color.RED, 6)

    def test_invalid_constructor_invalid_color(self):
        with self.assertRaises(ValueError):
            Connection(frozenset([self.boston, self.new_york]), "RED", 3)

    def test_invalid_constructor_too_few_cities(self):
        with self.assertRaises(ValueError):
            Connection(frozenset([self.boston]), Color.RED, 3)

    def test_invalid_constructor_too_many_cities(self):
        with self.assertRaises(ValueError):
            Connection(
                frozenset([self.boston, self.new_york, self.philadelphia]), Color.RED, 3)

    def test_invalid_constructor_repeated_city(self):
        with self.assertRaises(ValueError):
            Connection(frozenset([self.boston, self.boston]), Color.RED, 3)

    def test_invalid_constructor_invalid_cities_type(self):
        with self.assertRaises(ValueError):
            Connection([self.boston, self.new_york], Color.RED, 3)

    def test_connection_as_json(self):
        self.assertEqual(self.connection1.get_as_json(
        ), "[\"Boston\", \"New York\", \"blue\", 3]")

    def test_connection_lt_first_city_name(self):
        self.assertEqual(self.connection1 < self.connection5, -1)

    def test_connection_lt_second_city_name(self):
        self.assertEqual(self.connection1 < self.connection2, -1)

    def test_connection_lt_connection_length(self):
        self.assertEqual(self.connection4 < self.connection3, -1)

    def test_connection_lt_color(self):
        self.assertEqual(self.connection3 < self.connection2, -1)

class TestDestination(unittest.TestCase):
    def setUp(self):
        self.boston = City("Boston", 70, 80)
        self.new_york = City("New York", 60, 70)
        self.philadelphia = City("Philadelphia", 60, 70)
        self.destination1 = Destination(frozenset({self.boston, self.new_york}))
        self.destination2 = Destination(frozenset({self.boston, self.philadelphia}))
        self.destination3 = Destination(frozenset({self.new_york, self.philadelphia}))

    def test_valid_constructor(self):
        self.assertIn(self.boston, self.destination1)
        self.assertIn(self.new_york, self.destination1)
        self.assertNotIn(self.philadelphia, self.destination1)

    def test_invalid_constructor_noncity(self):
        with self.assertRaises(ValueError):
            Destination(frozenset({2, 3}))

    def test_invalid_constructor_too_few_cities(self):
        with self.assertRaises(ValueError):
            Destination(frozenset({self.boston}))

    def test_invalid_constructor_too_many_cities(self):
        with self.assertRaises(ValueError):
            Destination(frozenset({self.boston, self.new_york, self.philadelphia}))

    def test_invalid_constructor_repeat_city(self):
        with self.assertRaises(ValueError):
            Destination(frozenset({self.boston, self.boston}))

    def test_invalid_constructor_invalid_cities_type(self):
        with self.assertRaises(ValueError):
            Destination(frozenset({"city1": self.boston, "city2": self.new_york}))

    def test_destination_as_json(self):
        test_destination = Destination(frozenset({self.boston, self.new_york}))

        self.assertEqual(test_destination.get_as_json(
        ), "[\"Boston\", \"New York\"]")

    def test_destination_lt_first_city_name(self):
        self.assertEqual(self.destination2 < self.destination3, -1)

    def test_destination_lt_second_city_name(self):
        self.assertEqual(self.destination1 < self.destination2, -1)

    def test_destination_lt_equal_city_name(self):
        destination1_copy = Destination(frozenset({self.boston, self.new_york}))
        self.assertEqual(self.destination1 < destination1_copy, 1)

class TestMap(unittest.TestCase):
    def setUp(self):
        self.boston = City("Boston", 70, 80)
        self.new_york = City("New York", 60, 70)
        self.philadelphia = City("Philadelphia", 60, 70)
        self.los_angeles = City("Los Angeles", 0, 10)
        self.austin = City("Austin", 50, 15)
        self.wdc = City("Washington D.C.", 55, 60)
        self.connection1 = Connection(
            frozenset({self.boston, self.new_york}), Color.BLUE, 3)
        self.connection2 = Connection(
            frozenset({self.philadelphia, self.new_york}), Color.RED, 3)
        self.connection3 = Connection(
            frozenset({self.boston, self.philadelphia}), Color.GREEN, 4)
        self.connection4 = Connection(
            frozenset({self.austin, self.los_angeles}), Color.WHITE, 5)
        self.connection5 = Connection(
            frozenset({self.wdc, self.philadelphia}), Color.WHITE, 5)

        self.cities = {self.boston, self.new_york, self.philadelphia}
        self.connections = {self.connection1,
                            self.connection2, self.connection3}
        self.height, self.width = 800, 800
        self.test_map = Map(self.cities, self.connections, self.height, self.width)

        self.DEFAULT_WIDTH = 800
        self.DEFAULT_HEIGHT = 800

    def test_constructor(self):
        width, height = 500, 600
        test_map = Map(self.cities, self.connections, width, height)
        self.assertEqual(test_map.cities, self.cities)
        self.assertEqual(test_map.connections, self.connections)
        self.assertEqual(test_map.width, width)
        self.assertEqual(test_map.height, height)

    def test_constructor_defaults(self):
        test_map = Map(self.cities, self.connections)
        self.assertEqual(test_map.cities, self.cities)
        self.assertEqual(test_map.connections, self.connections)
        self.assertEqual(test_map.width, self.DEFAULT_WIDTH)
        self.assertEqual(test_map.height, self.DEFAULT_HEIGHT)

    def test_constructor_extra_city_in_cities(self):
        test_map = Map({self.boston, self.new_york,
                       self.philadelphia}, {self.connection1})
        for city in self.connection1.cities:
            self.assertIn(city, test_map.cities)

    def test_constructor_extra_city_in_connections(self):
        with self.assertRaises(ValueError):
            Map({self.boston, self.new_york}, {
                self.connection1, self.connection2})

    def test_constructor_extra_city_in_repeated_connections(self):
        with self.assertRaises(ValueError):
            Map({self.boston, self.new_york, self.philadelphia}, [
                self.connection1, self.connection2, self.connection2])

    def test_invalid_constructor_invalid_cities_type(self):
        with self.assertRaises(ValueError):
            Map([self.boston, self.new_york, self.philadelphia],
                {self.connection1, self.connection2})

    def test_invalid_constructor_invalid_connections_type(self):
        with self.assertRaises(ValueError):
            Map([self.boston, self.new_york, self.philadelphia],
                [self.connection1, self.connection2])

    def test_get_city_names(self):
        names1 = {"Boston", "New York", "Philadelphia"}
        names2 = {"New York", "Philadelphia", "Boston"}

        self.assertEqual(self.test_map.get_city_names(), names1)
        self.assertEqual(self.test_map.get_city_names(), names2)

    def test_get_cities_from_connections_multiple_connections(self):
        self.assertEqual(self.test_map.get_cities_from_connections(
            {self.connection1, self.connection2}), {self.boston, self.new_york, self.philadelphia})

    def test_get_cities_from_connections(self):
        self.assertEqual(self.test_map.get_cities_from_connections(
            {self.connection1}), {self.boston, self.new_york})

    def test_get_all_cities(self):
        self.assertEqual(self.test_map.get_all_cities(), {
                         self.boston, self.new_york, self.philadelphia})

    def test_get_all_cities_no_cities(self):
        test_map = Map(set(), set(), 500, 500)
        self.assertEqual(test_map.get_all_cities(), set())

    def test_get_all_connections(self):
        self.assertEqual(self.test_map.get_all_connections(), {
                         self.connection1, self.connection2, self.connection3})

    def test_get_all_connections_no_connections(self):
        test_map = Map(self.cities, set(), 500, 500)
        self.assertEqual(test_map.get_all_connections(), set())

    def test_get_all_terminal_cities_from_city_direct(self):
        self.assertEqual(set(self.test_map.get_all_terminal_cities_from_city(
            self.boston, self.test_map.connections)), {self.new_york, self.philadelphia})

    def test_get_all_terminal_cities_from_city_indirect_all_connected(self):
        cities = {self.boston, self.new_york, self.philadelphia, self.wdc}
        connections = {self.connection1, self.connection2,
                       self.connection3, self.connection5}
        test_map = Map(cities, connections)
        self.assertEqual(set(test_map.get_all_terminal_cities_from_city(
            self.boston, test_map.connections)), {self.new_york, self.philadelphia, self.wdc})

    def test_get_all_terminal_cities_from_city_indirect_not_all_connected(self):
        cities = {self.boston, self.new_york, self.philadelphia,
                  self.wdc, self.los_angeles, self.austin}
        connections = {self.connection1, self.connection2,
                       self.connection3, self.connection4, self.connection5}
        test_map = Map(cities, connections)
        self.assertEqual(set(test_map.get_all_terminal_cities_from_city(
            self.boston, test_map.connections)), {self.new_york, self.philadelphia, self.wdc})

    def test_get_feasible_destinations_simple(self):
        dest1 = Destination({self.new_york, self.philadelphia})
        dest2 = Destination({self.new_york, self.boston})
        dest3 = Destination({self.boston, self.philadelphia})

        self.assertEqual(self.test_map.get_feasible_destinations(self.test_map.connections),
                         {dest1, dest2, dest3})

    def test_get_feasible_destinations_disjoint_connections(self):
        dest1 = Destination({self.new_york, self.philadelphia})
        dest2 = Destination({self.new_york, self.boston})
        dest3 = Destination({self.boston, self.philadelphia})
        dest4 = Destination({self.los_angeles, self.austin})
        dest5 = Destination({self.new_york, self.wdc})
        dest6 = Destination({self.boston, self.wdc})
        dest7 = Destination({self.wdc, self.philadelphia})

        connections = self.test_map.connections
        connections.add(self.connection4)
        connections.add(self.connection5)
        self.assertEqual(self.test_map.get_feasible_destinations(connections),
                         {dest1, dest2, dest3, dest4, dest5, dest6, dest7})

    def test_get_map_as_json(self):
        cities = {self.boston, self.new_york}
        connections = {self.connection1}
        test_map = Map(cities, connections)

        self.assertEqual(test_map.get_as_json(
        ), "{\"cities\": [[\"Boston\", [560, 640]], [\"New York\", [480, 560]]], \"connections\": {\"Boston\": {\"New York\": {\"blue\": 3}}}, \"height\": 800, \"width\": 800}")


if __name__ == '__main__':
    unittest.main()

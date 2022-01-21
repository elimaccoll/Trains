import unittest
from PIL import Image
from io import BytesIO
from math import floor
import sys

sys.path.append('../../../')
from Trains.Editor.map_editor import MapVisualizer
from Trains.Common.map import City, Connection, Color, Map


class TestMapVisualizer(unittest.TestCase):
    # Regex for city names: "[a-zA-Z0-9\\ \\.\\,]+"
    def setUp(self):
        self.boston = City("Boston", 70, 80)
        self.new_york = City("New York", 60, 70)
        self.philadelphia = City("Philadelphia", 90, 10)
        self.los_angeles = City("Los Angeles", 0, 10)
        self.austin = City("Austin", 50, 10)
        self.wdc = City("Washington D.C.", 55, 60)
        self.connection1 = Connection(frozenset({self.boston, self.new_york}), Color.BLUE, 3)
        self.connection2 = Connection(frozenset({self.boston, self.new_york}), Color.RED, 3)
        self.connection3 = Connection(frozenset({self.boston, self.new_york}), Color.GREEN, 3)
        self.connection4 = Connection(frozenset({self.boston, self.new_york}), Color.WHITE, 3)

        self.connection5 = Connection(frozenset({self.philadelphia, self.new_york}), Color.RED, 4)
        self.connection6 = Connection(frozenset({self.philadelphia, self.new_york}), Color.GREEN, 4)
        self.connection7 = Connection(frozenset({self.philadelphia, self.new_york}), Color.WHITE, 4)

        self.connection8 = Connection(frozenset({self.boston, self.philadelphia}), Color.GREEN, 4)
        self.connection9 = Connection(frozenset({self.boston, self.philadelphia}), Color.BLUE, 4)

        self.connection10 = Connection(frozenset({self.austin, self.los_angeles}), Color.BLUE, 5)
        self.connection11 = Connection(frozenset({self.wdc, self.philadelphia}), Color.WHITE, 5)

        self.cities = {self.boston, self.new_york, self.philadelphia, self.los_angeles, self.austin, self.wdc}
        self.connections = {self.connection1, self.connection2, self.connection3, self.connection4, self.connection5, self.connection6, self.connection7, self.connection8, self.connection9, self.connection10, self.connection11}
        self.width = 800
        self.height = 800
        self.test_map = Map(self.cities, self.connections, self.height, self.width)
        self.gui = MapVisualizer(self.test_map, 0)

        self.MAP_CONSTANTS = self.gui.config_map_constants(self.test_map)
        self.average_dimension = (self.width + self.height) / 2
        self.DEFAULT_CITY_RADIUS = 14
        self.DEFAULT_CITY_NAME_SIZE = 14
        self.MIN_CITY_RADIUS = 2
        self.MIN_CITY_NAME_SIZE = 5

    def test_verify_city_names_invalid_characters(self):
        with self.assertRaises(ValueError):
            self.gui.verify_city_name("$%^&*(")

    def test_verify_city_names_too_long(self):
        with self.assertRaises(ValueError):
            self.gui.verify_city_name("abcdefghijklmnopqrstuvwxyz")

    def test_verify_city_names_empty(self):
        with self.assertRaises(ValueError):
            self.gui.verify_city_name("")

    def test_verify_city_names_both_errors(self):
        with self.assertRaises(ValueError):
            self.gui.verify_city_name("abcdefghi%#&jklmnopqrstuvwxyz")

    def test_verify_city_names_exactly_25(self):
        self.assertIsNone(self.gui.verify_city_name("abcdefghijklmnopqrstuvwxy"))

    def test_verify_city_names_with_space(self):
        self.assertIsNone(self.gui.verify_city_name("New York"))

    def test_verify_city_names_with_period(self):
        self.assertIsNone(self.gui.verify_city_name("Washington D.C."))

    def test_verify_city_names_with_comma(self):
        self.assertIsNone(self.gui.verify_city_name("Gary, Indiana"))

    def test_verify_city_names_with_numbers(self):
        self.assertIsNone(self.gui.verify_city_name("city7"))

    def test_verify_city_names_all_lowercase(self):
        self.assertIsNone(self.gui.verify_city_name("city"))

    def test_verify_city_names_all_uppercase(self):
        self.assertIsNone(self.gui.verify_city_name("CITY"))

    def test_verify_city_names_with_all(self):
        self.assertIsNone(self.gui.verify_city_name("Washington, D.C. 8"))

    def test_verify_dimensions_min(self):
        self.assertIsNone(self.gui.verify_dimensions(10, 10))

    def test_verify_dimensions_valid(self):
        self.assertIsNone(self.gui.verify_dimensions(400, 500))

    def test_verify_dimensions_max(self):
        self.assertIsNone(self.gui.verify_dimensions(800, 800))

    def test_verify_dimensions_too_small_both(self):
        with self.assertRaises(ValueError):
            self.gui.verify_dimensions(9, 9)

    def test_verify_dimensions_too_small_x(self):
        with self.assertRaises(ValueError):
            self.gui.verify_dimensions(9, 10)

    def test_verify_dimensions_too_small_y(self):
        with self.assertRaises(ValueError):
            self.gui.verify_dimensions(10, 9)

    def test_verify_dimensions_too_big_both(self):
        with self.assertRaises(ValueError):
            self.gui.verify_dimensions(801, 801)

    def test_verify_dimensions_too_big_x(self):
        with self.assertRaises(ValueError):
            self.gui.verify_dimensions(801, 700)

    def test_verify_dimensions_too_big_y(self):
        with self.assertRaises(ValueError):
            self.gui.verify_dimensions(700, 801)

    def test_scale_map_elements_max_dimensions(self):
        city_radius, city_name_size, line_width = self.gui.scale_map_elements(self.width, self.height)
        exp_city_radius = floor(self.DEFAULT_CITY_RADIUS/(800/self.average_dimension))
        exp_city_name_size = floor(self.DEFAULT_CITY_NAME_SIZE/(800/self.average_dimension))
        exp_line_width = 3
        self.assertEqual(city_radius, exp_city_radius)
        self.assertEqual(city_name_size, exp_city_name_size)
        self.assertEqual(line_width, exp_line_width)

    def test_scale_map_elements_non_extreme_dimensions(self):
        height = 400
        width = 400
        average_dimension = (height + width) / 2
        city_radius, city_name_size, line_width = self.gui.scale_map_elements(width, height)
        exp_city_radius = floor(self.DEFAULT_CITY_RADIUS/(800/average_dimension))
        exp_city_name_size = floor(self.DEFAULT_CITY_NAME_SIZE/(800/average_dimension))
        exp_line_width = 2
        self.assertEqual(city_radius, exp_city_radius)
        self.assertEqual(city_name_size, exp_city_name_size)
        self.assertEqual(line_width, exp_line_width)

    def test_scale_map_elements_min_dimensions(self):
        height = 10
        width = 10
        city_radius, city_name_size, line_width = self.gui.scale_map_elements(width, height)
        exp_city_radius = self.MIN_CITY_RADIUS
        exp_city_name_size = self.MIN_CITY_NAME_SIZE
        exp_line_width = 1
        self.assertEqual(city_radius, exp_city_radius)
        self.assertEqual(city_name_size, exp_city_name_size)
        self.assertEqual(line_width, exp_line_width)

    def test_config_map_constants(self):
        exp_city_radius = floor(self.DEFAULT_CITY_RADIUS/(800/self.average_dimension))
        exp_city_name_size = floor(self.DEFAULT_CITY_NAME_SIZE/(800/self.average_dimension))
        exp_line_width = 3
        MAP_SCALE = 0.85
        CANVAS_COLOR = "black"
        self.assertEqual(self.MAP_CONSTANTS["width"], self.width)
        self.assertEqual(self.MAP_CONSTANTS["height"], self.height)
        self.assertEqual(self.MAP_CONSTANTS["city_radius"], exp_city_radius)
        self.assertEqual(self.MAP_CONSTANTS["city_name_size"], exp_city_name_size)
        self.assertEqual(self.MAP_CONSTANTS["city_name_offset"], 10)
        self.assertEqual(self.MAP_CONSTANTS["line_width"], exp_line_width)
        self.assertEqual(self.MAP_CONSTANTS["segment_gap"], 3)
        self.assertEqual(self.MAP_CONSTANTS["connection_offset"], 6)
        self.assertEqual(self.MAP_CONSTANTS["map_scale"], MAP_SCALE)
        self.assertEqual(self.MAP_CONSTANTS["map_border"], ((1 - MAP_SCALE) / 2))
        self.assertEqual(self.MAP_CONSTANTS["colors"][1], "red")
        self.assertEqual(self.MAP_CONSTANTS["colors"][2], "blue")
        self.assertEqual(self.MAP_CONSTANTS["colors"][3], "green")
        self.assertEqual(self.MAP_CONSTANTS["colors"][4], "white")
        self.assertEqual(self.MAP_CONSTANTS["canvas_color"], CANVAS_COLOR)
        self.assertEqual(self.MAP_CONSTANTS["city_color"], "red")
        self.assertEqual(self.MAP_CONSTANTS["city_name_color"], "white")
        self.assertEqual(self.MAP_CONSTANTS["segment_gap_color"], CANVAS_COLOR)

    def test_count_connections_between_cities(self):
        count_connections = self.gui.count_connections_between_cities(self.connections)
        self.assertEqual(count_connections[frozenset({self.boston, self.new_york})], {self.connection1, self.connection2, self.connection3, self.connection4})
        self.assertEqual(count_connections[frozenset({self.philadelphia, self.new_york})], {self.connection5, self.connection6, self.connection7})
        self.assertEqual(count_connections[frozenset({self.philadelphia, self.boston})], {self.connection8, self.connection9})
        self.assertEqual(count_connections[frozenset({self.austin, self.los_angeles})], {self.connection10})
        self.assertEqual(count_connections[frozenset({self.philadelphia, self.wdc})], {self.connection11})
        
    def test_compute_connection_offsets(self):
        count_connections = self.gui.count_connections_between_cities(self.connections)
        offset_dict = self.gui.compute_connection_offsets(count_connections)
        self.assertEqual(offset_dict[frozenset({self.boston, self.new_york})]["connections"], {self.connection1, self.connection2, self.connection3, self.connection4})
        self.assertEqual(offset_dict[frozenset({self.philadelphia, self.new_york})]["connections"], {self.connection5, self.connection6, self.connection7})
        self.assertEqual(offset_dict[frozenset({self.philadelphia, self.boston})]["connections"], {self.connection8, self.connection9})
        self.assertEqual(offset_dict[frozenset({self.austin, self.los_angeles})]["connections"], {self.connection10})
        self.assertEqual(offset_dict[frozenset({self.philadelphia, self.wdc})]["connections"], {self.connection11})
        
        increment = 1
        num_connections = 4
        first_offset = -floor(num_connections/2)*increment + (increment/2)*((num_connections + 1) % 2)
        offsets = [first_offset, first_offset+increment, first_offset+2*increment, first_offset+3*increment]
        self.assertEqual(offset_dict[frozenset({self.boston, self.new_york})]["offsets"], offsets)
        num_connections = 3
        first_offset = -floor(num_connections/2)*increment + (increment/2)*((num_connections + 1) % 2)
        offsets = [first_offset, first_offset+increment, first_offset+2*increment]
        self.assertEqual(offset_dict[frozenset({self.philadelphia, self.new_york})]["offsets"], offsets)
        num_connections = 2
        first_offset = -floor(num_connections/2)*increment + (increment/2)*((num_connections + 1) % 2)
        offsets = [first_offset, first_offset+increment]
        self.assertEqual(offset_dict[frozenset({self.philadelphia, self.boston})]["offsets"], offsets)
        num_connections = 1
        first_offset = -floor(num_connections/2)*increment + (increment/2)*((num_connections + 1) % 2)
        offsets = [first_offset]
        self.assertEqual(offset_dict[frozenset({self.austin, self.los_angeles})]["offsets"], offsets)
        self.assertEqual(offset_dict[frozenset({self.philadelphia, self.wdc})]["offsets"], offsets)
        
    def test_normalize_city_coordindates(self):
        # self.boston = City("Boston", 70, 80)
        boston_x = 70
        boston_y = 80
        city_x_normalized, city_y_normalized = self.gui.normalize_city_coordinates(self.boston.x, self.boston.y, self.MAP_CONSTANTS)
        exp_city_x_normalized = self.MAP_CONSTANTS["map_scale"]*self.MAP_CONSTANTS["width"]*boston_x/100 + self.MAP_CONSTANTS["map_border"]*self.MAP_CONSTANTS["width"]
        exp_city_y_normalized = self.MAP_CONSTANTS["map_scale"]*self.MAP_CONSTANTS["height"]*boston_y/100 + self.MAP_CONSTANTS["map_border"]*self.MAP_CONSTANTS["height"]
        self.assertEqual(city_x_normalized, exp_city_x_normalized)
        self.assertEqual(city_y_normalized, exp_city_y_normalized)

    def test_calculate_offset_coordinates_offset_x(self):
        # self.boston = City("Boston", 70, 80)
        # self.new_york = City("New York", 60, 70)
        increment = 1
        num_connections = 4
        first_offset = -floor(num_connections/2)*increment + (increment/2)*((num_connections + 1) % 2)
        offsets = [first_offset, first_offset+increment, first_offset+2*increment, first_offset+3*increment]
        for offset in offsets:
            x1, y1, x2, y2 = self.gui.calculate_offset_coordinates(self.boston.x, self.boston.y, self.new_york.x, self.new_york.y, offset, self.MAP_CONSTANTS)
            exp_x1 = self.boston.x + offset*self.MAP_CONSTANTS["connection_offset"]
            exp_x2 = self.new_york.x + offset*self.MAP_CONSTANTS["connection_offset"]
            self.assertEqual(x1, exp_x1)
            self.assertEqual(x2, exp_x2)
            self.assertEqual(y1, self.boston.y)
            self.assertEqual(y2, self.new_york.y)

    # def test_display_gui_1_second_timeout(self):
    #     timeout = 1
    #     MapVisualizer(self.test_map, timeout)

    # def test_draw_map(self):
    #     GREEN = (0, 128, 0) if sys.platform == 'win32' else (0, 255, 0)
    #     json_map = "{\"cities\": [{\"name\": \"St. Louis\", \"x\": 50, \"y\": 50}, {\"name\": \"New York\", \"x\": 80, \"y\": 30}, {\"name\": \"Boston\", \"x\": 90, \"y\": 20}, {\"name\": \"Trenton\", \"x\": 100, \"y\": 40}], \"connections\": [{\"cities\": [{\"name\": \"St. Louis\", \"x\": 50, \"y\": 50}, {\"name\": \"New York\", \"x\": 80, \"y\": 30}], \"color\": 3, \"length\": 5}, {\"cities\": [{\"name\": \"Boston\", \"x\": 90, \"y\": 20}, {\"name\": \"New York\", \"x\": 80, \"y\": 30}], \"color\": 2, \"length\": 3}, {\"cities\": [{\"name\": \"Boston\", \"x\": 90, \"y\": 20}, {\"name\": \"New York\", \"x\": 80, \"y\": 30}], \"color\": 4, \"length\": 3}, {\"cities\": [{\"name\": \"Boston\", \"x\": 90, \"y\": 20}, {\"name\": \"New York\", \"x\": 80, \"y\": 30}], \"color\": 3, \"length\": 3}, {\"cities\": [{\"name\": \"Boston\", \"x\": 90, \"y\": 20}, {\"name\": \"New York\", \"x\": 80, \"y\": 30}], \"color\": 1, \"length\": 3}, {\"cities\": [{\"name\": \"New York\", \"x\": 80, \"y\": 30}, {\"name\": \"Trenton\", \"x\": 100, \"y\": 40}], \"color\": 2, \"length\": 4}], \"width\": 800, \"height\": 800}"
    #     # test_canvas = self.gui.draw_map(json_map, True)
    #     # if testing:
    #     #     bg = canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill='black')
    #     #     canvas.tag_lower(bg)
    #     #     return canvas
    #     self.gui.draw_map(json_map, timeout=1)
    #     test_canvas = self.gui.test_map
    #     test_canvas.update()
    #     ps = test_canvas.postscript(colormode='color')
    #     img = Image.open(BytesIO(ps.encode('utf-8')))
    #     # The background should be black
    #     self.assertEqual(img.getpixel((0, 0)), (0, 0, 0))
    #     self.assertEqual(img.getpixel((599, 599)), (0, 0, 0))
    #     # Cities should be red
    #     self.assertEqual(img.getpixel((300, 300)),  (255, 0, 0))
    #     self.assertEqual(img.getpixel((453, 200)),  (255, 0, 0))
    #     self.assertEqual(img.getpixel((555, 250)),  (255, 0, 0))
    #     self.assertEqual(img.getpixel((500, 150)),  (255, 0, 0))
    #     # The connections should be their respective color
    #     self.assertEqual(img.getpixel((350, 265)), GREEN)
    #     self.assertEqual(img.getpixel((490, 215)), (0, 0, 255))
    #     self.assertEqual(img.getpixel((480, 165)), GREEN)
    #     self.assertEqual(img.getpixel((480, 170)), (0, 0, 255))
    #     self.assertEqual(img.getpixel((480, 175)), (255, 255, 255))
    #     self.assertEqual(img.getpixel((480, 180)), (255, 0, 0))
    #     # There should be gaps between segments of connections
    #     self.assertEqual(img.getpixel((360, 260)), (0, 0, 0))
    #     self.assertEqual(img.getpixel((390, 240)), (0, 0, 0))
    #     self.assertEqual(img.getpixel((470, 180)), (0, 0, 0))
    #     img.close()


if __name__ == '__main__':
    unittest.main()

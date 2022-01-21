from tkinter import Tk, Canvas
import re
from typing import Any, Dict, Union, Tuple, Set, FrozenSet
from math import floor
import sys
sys.path.append('../../')
from Trains.Common.map import Connection, Map, City


class MapVisualizer:
    """
    A map visualizer that contains methods to draw and display a given map with drawn elements
    that are scaled according the given size of the given map.
    """

    game_map: Map
    timeout: Union[int, None]
    MAP_CONSTANTS: Dict[str, Any]
    window: Tk
    canvas: Canvas

    def __init__(self, game_map: Map, timeout: int = None) -> None:
        """
        MapVisualizer Constructor that takes a game map to be drawn and displayed and an optional timeout
        for how long the window will be displayed.  Defaults to no timeout.
            Parameters:
                game_map (Map): Map object that represents the game map being drawn
                timeout (int): Optional timeout for the gui (in seconds)
        """
        if type(game_map) != Map:
            raise TypeError("Given game map must be of type Map")
        if timeout is not None:
            if timeout < 0:
                raise TypeError("Timeout must be a natural number")

        # Verify city names
        for city in game_map.cities:
            self.verify_city_name(city.name)
        # Get map constants for drawing scaled elements
        MAP_CONSTANTS = self.config_map_constants(game_map)
        # Calculate all of the offsets for drawing connections
        count_connections = self.count_connections_between_cities(game_map.connections)
        connections_and_offsets = self.compute_connection_offsets(count_connections)
        # Create the GUI, draw the map, and display the map
        window, canvas = self.create_gui_elements(MAP_CONSTANTS)
        self.draw_map_to_canvas(canvas, game_map.cities, connections_and_offsets, MAP_CONSTANTS)
        self.display_map(window, timeout)

    def config_map_constants(self, game_map: Map) -> Dict[str, Any]:
        """
        Packages all of the map constants into a single dictionary to be passed around as needed.
        Calculates and sets the scaled constants used to visualize the map.
            Parameters:
                game_map (Map): game map being drawn/used to scale values and set them as map constants
            Returns:
                MAP_CONSTANTS (dict): Dictionary of all map constants that are used to visualize the map
        """
        WIDTH = game_map.width
        HEIGHT = game_map.height
        self.verify_dimensions(WIDTH, HEIGHT)
        # Obtain values for constants that are dependent on the size of the map (scaling)
        CITY_RADIUS, CITY_NAME_SIZE, LINE_WIDTH = self.scale_map_elements(WIDTH, HEIGHT)

        SEGMENT_GAP = 3
        CONNECTION_OFFSET = 6
        MAP_SCALE = 0.85
        MAP_CONSTANTS = {
            "width": WIDTH,
            "height": HEIGHT,
            "city_radius": CITY_RADIUS,
            "city_name_size": CITY_NAME_SIZE,
            "city_name_offset": 10,
            "line_width": LINE_WIDTH,
            "segment_gap": SEGMENT_GAP,
            "connection_offset": CONNECTION_OFFSET,
            "map_scale": MAP_SCALE,
            "map_border": ((1 - MAP_SCALE) / 2),
            "colors": {
                1: "red",
                2: "blue",
                3: "green",
                4: "white"
            },
            "canvas_color": "black",
            "city_color": "red",
            "city_name_color": "white"
        }
        MAP_CONSTANTS["segment_gap_color"] = MAP_CONSTANTS["canvas_color"]
        return MAP_CONSTANTS

    def scale_map_elements(self, width: int, height: int) -> Tuple[int, int, int]:
        """
        Scales drawn map elements (Size of cities, fontsize of city names, and connection line
        segment size) according to the canvas size.
        THIS METHOD MUTATES CITY_RADIUS, CITY_NAME_SIZE, and LINE_WIDTH
            Parameters:
                width (int): width of the canvas
                height (int): height of the canvas
            Returns:
                The scaled integers of the values representing city_radius, city_name_size, and line_width 
        """
        DEFAULT_CITY_RADIUS = 14
        DEFAULT_CITY_NAME_SIZE = 14
        MIN_CITY_RADIUS = 2
        MIN_CITY_NAME_SIZE = 5
        average_dimension = (width + height) / 2
        # Scale city size
        city_radius = floor(DEFAULT_CITY_RADIUS/(800/average_dimension))
        if city_radius < MIN_CITY_RADIUS:
            city_radius = MIN_CITY_RADIUS
        # Scale city name size
        city_name_size = floor(DEFAULT_CITY_NAME_SIZE/(800/average_dimension))
        if city_name_size < MIN_CITY_NAME_SIZE:
            city_name_size = MIN_CITY_NAME_SIZE
        # Scale connection line width size
        if average_dimension <= 300:
            line_width = 1
        elif average_dimension <= 500:
            line_width = 2
        else:
            line_width = 3
        return city_radius, city_name_size, line_width

    def create_gui_elements(self, MAP_CONSTANTS: Dict[str, Any]) -> Tuple[Tk, Canvas]:
        """
        Creates the GUI elements to visualize the map (tkinter window and canvas).
            Parameters:
                MAP_CONSTANTS (dict): Package of map constants used to visualize the map
            Returns:
                The GUI window and the window's canvas to draw the map on
        """
        window = Tk()
        canvas = Canvas(window, bg=MAP_CONSTANTS["canvas_color"], width=MAP_CONSTANTS["width"], height=MAP_CONSTANTS["height"], highlightthickness=0, border=False)
        return window, canvas

    def verify_dimensions(self, width: int, height: int) -> None:
        """
        Verifies the validity of the dimensions of the map.
            Parameters:
                width (int): The width of the map
                height (int): The height of the map
            Throws:
                ValueError: The width and height dimensions must be in [10,800] and [10,800]
        """
        if width < 10 or width > 800 or height < 10 or height > 800:
            raise ValueError("Invalid map dimensions")

    def verify_city_name(self, name: str) -> None:
        """
        Verifies the validity of a given city name.
            Parameters:
                name (str): The city name
            Throws:
                ValueError: A city's name must satisfy the regular expression "[a-zA-Z0-9\\ \\.\\,]+"
                            and have at most 25 ASCII chracters.
        """
        if len(name) > 25:
            raise ValueError("Invalid city name")
        pattern = "[a-zA-Z0-9\\ \\.\\,]+"
        result = re.match(pattern, name)
        if result is None or result.span()[1] != len(name):
            raise ValueError("Invalid city name")

    def count_connections_between_cities(self, connections: Set[Connection]) -> Dict[FrozenSet[City], Set[Connection]]:
        """
        Counts the number of connections between cities that are connected (Cities with 1 or more connections between them).
            Parameters:
                connections (set(Connection)): connections used to count (presumably all connections in the game map being visualized)
            Returns:
                count_connections (dict): Dictionary of sets of connected cities (keys) to the connections between those cities (value(s))
        """
        # Count the number of connections between two cities that are connected
        count_connections: Dict[FrozenSet[City], Set[Connection]] = {}
        for connection in connections:
            connection_key = frozenset(connection.cities)
            if connection_key in count_connections.keys():
                count_connections[connection_key].add(connection)
            else:
                count_connections[connection_key] = set({connection})
        return count_connections

    def compute_connection_offsets(self, count_connections: Dict[FrozenSet[City], Set[Connection]]) -> Dict[FrozenSet[City], Dict[str, Any]]:
        """
        Computes all of the offsets needed for drawing the connections based on the number of connections between two connected cities.
            Parameters:
                count_connections (dict): Dictionary of sets of connected cities (keys) to the connections between those cities (value(s))
            Returns:
                offset_dict (dict): A dictionary of sets of connected cities (keys) to a dictionary with the fields 'connections' that represents
                the connections between those key cities, and 'offsets' which is a list of the offsets for the connections in the 'connections' field
        """
        offset_dict: Dict[FrozenSet[City], Dict[str, Any]] = dict()
        # Arbitrary offset increment that prevents connections overlapping when drawn next to each other
        increment = 1
        for connection_key, connections in count_connections.items():
            # Calculates first offset to start incrementing from (handles even and odd number of connections)
            offset = -floor(len(connections)/2)*increment + (increment/2)*((len(connections) + 1) % 2)
            connection_offsets = []
            # Calcluate the list of offsets for connections between two connected cities
            for _ in range(len(connections)):
                connection_offsets.append(offset)
                offset += increment
            offset_dict[connection_key] = {"connections": connections, "offsets": connection_offsets}
        return offset_dict

    def normalize_city_coordinates(self, city_x: float, city_y: float, MAP_CONSTANTS: Dict[str, Any]) -> Tuple[float, float]:
        """
        Normalizes city coordiantes from range [0, 100] to corresponding map coordinates with consideration of a map border.
            Parameters:
                city_x (int): x coordinate of the city
                city_y (int): y coordinate of the city
                MAP_CONSTANTS (dict): Package of map constants used to visualize the map
            Returns:
                Normalized x coordinate of the city, normalized y coordinate of the city
        """
        city_x_normalized = MAP_CONSTANTS["map_scale"]*MAP_CONSTANTS["width"]*city_x/100 + MAP_CONSTANTS["map_border"]*MAP_CONSTANTS["width"]
        city_y_normalized = MAP_CONSTANTS["map_scale"]*MAP_CONSTANTS["height"]*city_y/100 + MAP_CONSTANTS["map_border"]*MAP_CONSTANTS["height"]
        return city_x_normalized, city_y_normalized

    def draw_cities(self, canvas: Canvas, cities: Set[City], MAP_CONSTANTS: Dict[str, Any]) -> None:
        """
        Draws cities (circles) and corresponding city names (text) on a given canvas.
            Parameters:
                canvas (Canvas): canvas to draw on
                cities (set(City)): cities to draw
                MAP_CONSTANTS (dict): Package of map constants used to visualize the map
        """
        for city in cities:
            city_x, city_y = self.normalize_city_coordinates(city.x, city.y, MAP_CONSTANTS)
            canvas.create_oval(city_x - MAP_CONSTANTS["city_radius"], city_y - MAP_CONSTANTS["city_radius"], city_x + MAP_CONSTANTS["city_radius"], city_y + MAP_CONSTANTS["city_radius"], fill=MAP_CONSTANTS["city_color"])
            canvas.create_text(city_x, city_y - MAP_CONSTANTS["city_name_offset"], text=city.name, fill=MAP_CONSTANTS["city_name_color"], font=("Purisa", MAP_CONSTANTS["city_name_size"]))

    def calculate_offset_coordinates(self, x1: float, y1: float, x2: float, y2: float, offset: float, \
        MAP_CONSTANTS: Dict[str, Any]) -> Tuple[float, float, float, float]:
        """
        Determines which coordinates the offset and calculates the offset coordinates for drawing connections using a 
        given offset and map constants for connection offset.
            Parameters:
                x1 (float): x coordinate of city 1
                y1 (float): y coordinate of city 1
                x2 (float): x coordinate of city 2
                y2 (float): y coordinate of city 2
                offset (float): offset used to calculate the offset coordinates
                MAP_CONSTANTS (dict): Package of map constants used to visualize the map
            Returns:
                The coordinates (either x's or y's will be offset) x1, y1, x2, y2
        """
        # Apply different offset for different connection angles
        if abs(x1 - x2) <= 300:
            x1 += offset*MAP_CONSTANTS["connection_offset"]
            x2 += offset*MAP_CONSTANTS["connection_offset"]
        else:
            y1 += offset*MAP_CONSTANTS["connection_offset"]
            y2 += offset*MAP_CONSTANTS["connection_offset"]
        return x1, y1, x2, y2

    def draw_segmented_line(self, canvas: Canvas, x1: float, y1: float, x2: float, y2: float, segments: int, \
        color: str, MAP_CONSTANTS: Dict[str, Any]) -> None:
        """
        Draws a segmented line on a given canvas that represents a connection bewteen two cities.
            Parameters:
                canvas (Canvas): The canvas being drawn on
                x1 (float): The x position of city 1
                y1 (float): The y position of city 1
                x2 (float): The x position of city 2
                y2 (float): The y position of city 2
                segments (int): Number of segments to break the line into
                color (str): Color of the line being drawn
                MAP_CONSTANTS (dict): Package of map constants used to visualize the map
        """
        # Calculate segment length
        xdiff = (x2 - x1) / segments
        ydiff = (y2 - y1) / segments
        # Draw line between the connected cities
        canvas.create_line(x1, y1, x2, y2, width=MAP_CONSTANTS["line_width"], fill=color)
        # Draw the gaps over the line at specific points to create a segmented line
        for n in range(1, segments):
            canvas.create_oval(x1 + n*xdiff - MAP_CONSTANTS["segment_gap"], y1 + n*ydiff - MAP_CONSTANTS["segment_gap"], x1 + n*xdiff + MAP_CONSTANTS["segment_gap"], y1 + n*ydiff + MAP_CONSTANTS["segment_gap"], fill=MAP_CONSTANTS["segment_gap_color"])

    def draw_connections(self, canvas: Canvas, connections_and_offsets: Dict[FrozenSet[City], Dict[str, Any]], \
        MAP_CONSTANTS: Dict[str, Any]):
        """
        Draws given connections using their corresponding offsets on a given canvas using the given map constants.
            Parameters:
                canvas (Canvas): canvas to draw on
                connections_and_offsets (dict): Dictionary with fields 'connections' as the connections to draw
                                                'offsets' which is the corresponding list of offsets for the connections
                MAP_CONSTANTS (dict): Package of map constants used to visualize the map
        """
        for connection_info in connections_and_offsets.values():
            offset_index = 0
            offsets = connection_info["offsets"]
            for connection in connection_info["connections"]:
                cities = list(connection.cities)
                city1_x, city1_y = self.normalize_city_coordinates(cities[0].x, cities[0].y, MAP_CONSTANTS)
                city2_x, city2_y = self.normalize_city_coordinates(cities[1].x, cities[1].y, MAP_CONSTANTS)
                x1, y1, x2, y2 = self.calculate_offset_coordinates(city1_x, city1_y, city2_x, city2_y, offsets[offset_index], MAP_CONSTANTS)
                self.draw_segmented_line(canvas, x1, y1, x2, y2, connection.length, connection.color.value, MAP_CONSTANTS)
                offset_index += 1

    def draw_map_to_canvas(self, canvas: Canvas, cities: Set[City], connections_and_offsets: Dict[FrozenSet[City], \
        Dict[str, Any]], MAP_CONSTANTS: Dict[str, Any]) -> None:
        """
        Draws a game map to the given canvas using the given cities, connections and offsets, and given map constants.
            Parameters:
                canvas (Canvas): Canvas to draw on 
                cities (set(City)): Cities to draw
                connections_and_offsets (dict): Connections to draw using their corresponding offsets
                MAP_CONSTANTS (dict): Package of map constants used to visualize the map
        """
        self.draw_connections(canvas, connections_and_offsets, MAP_CONSTANTS)
        self.draw_cities(canvas, cities, MAP_CONSTANTS)
        canvas.pack()

    def display_map(self, window: Tk, timeout: int) -> None:
        """
        Displays a drawn map.  Closes after 'timeout' seconds (Default is no timeout).
            Parameters:
                window (Tk window): GUI window containing the canvas with the drawn map
                timeout (int): Timeout (in seconds) to close the GUI window after
        """
        if timeout is not None:
            window.after(timeout*1000, lambda: window.destroy())
        window.mainloop()
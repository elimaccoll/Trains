import sys
import unittest

sys.path.append('../../../')
from Trains.Common.map import City, Color, Connection, Destination, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.buy_now import Buy_Now
from Trains.Player.hold_10 import Hold_10
from Trains.Player.moves import AcquireConnectionMove, DrawCardMove


class TestStrategyHold10(unittest.TestCase):
    def setUp(self):
        self.boston = City("Boston", 70, 20)
        self.new_york = City("New York", 60, 30)
        self.austin = City("Austin", 50, 80)
        self.houston = City("Houston", 50, 90)
        self.philadelphia = City("Philadelphia", 60, 70)
        self.los_angeles = City("Los Angeles", 0, 10)
        self.wdc = City("Washington D.C.", 55, 60)
        self.cities = {self.boston, self.new_york, self.austin,
                       self.houston, self.philadelphia, self.los_angeles, self.wdc}

        self.connection1 = Connection(
            frozenset({self.boston, self.new_york}), Color.BLUE, 4)
        self.connection2 = Connection(
            frozenset({self.new_york, self.philadelphia}), Color.GREEN, 3)
        self.connection3 = Connection(
            frozenset({self.boston, self.philadelphia}), Color.GREEN, 4)
        self.connection4 = Connection(
            frozenset({self.austin, self.los_angeles}), Color.BLUE, 5)
        self.connection5 = Connection(
            frozenset({self.philadelphia, self.wdc}), Color.WHITE, 3)
        self.connection6 = Connection(
            frozenset({self.philadelphia, self.wdc}), Color.WHITE, 4)
        self.connection7 = Connection(
            frozenset({self.philadelphia, self.wdc}), Color.RED, 4)
        self.connection8 = Connection(
            frozenset({self.austin, self.los_angeles}), Color.GREEN, 5)
        self.all_connections = {self.connection1, self.connection2, self.connection3, self.connection4,
                                self.connection5, self.connection6, self.connection7, self.connection8}

        self.game_map = Map(self.cities, self.all_connections)

        self.dest1 = Destination(frozenset({self.austin, self.new_york}))
        self.dest2 = Destination(frozenset({self.boston, self.houston}))
        self.dest3 = Destination(frozenset({self.austin, self.houston}))
        self.dest4 = Destination(frozenset({self.new_york, self.philadelphia}))
        self.dest5 = Destination(frozenset({self.los_angeles, self.wdc}))

        self.destination_options = {self.dest1, self.dest2, self.dest3, self.dest4, self.dest5}

        self.NUM_DESTINATIONS_TO_SELECT = 2
        self.NUM_DESTINATIONS_OPTIONS = 5

        self.h10_strat = Hold_10()

    def test_select_destinations_select_two_hold_10(self):
        destinations = self.h10_strat.select_destinations(
            self.destination_options, self.NUM_DESTINATIONS_TO_SELECT)
        self.assertEqual(destinations, {self.dest1, self.dest3})

    def test_select_destinations_select_three_hold_10(self):
        number_of_destination = 3
        destinations = self.h10_strat.select_destinations(
            self.destination_options, number_of_destination)
        self.assertEqual(destinations, {self.dest1, self.dest2, self.dest3})

    def test_get_player_move_draw_cards(self):
        cc = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        pgs = PlayerGameState(set(), cc, 45, set(), list())
        # Given player game state has 10 or less cards, so draw
        self.assertEqual(self.h10_strat.get_player_move(pgs, self.game_map), DrawCardMove())

    def test_get_player_move_draw_cards_exactly_10_cards(self):
        cc = {Color.RED: 1, Color.BLUE: 5, Color.GREEN: 3, Color.WHITE: 1}
        pgs = PlayerGameState(set(), cc, 45, set(), list())
        # Given player game state has 10 or less cards, so draw
        self.assertEqual(self.h10_strat.get_player_move(pgs, self.game_map), DrawCardMove())

    def test_get_player_move_acquire_connection(self):
        cc = {Color.RED: 10, Color.BLUE: 10, Color.GREEN: 10, Color.WHITE: 10}
        pgs = PlayerGameState(set(), cc, 45, set(), list())
        # Given player game state has more than 10 cards, so acquire a connection
        # self.connection4 comes first lexicographically and the pgs has the necessary resources
        self.assertEqual(self.h10_strat.get_player_move(pgs, self.game_map), \
            AcquireConnectionMove(self.connection4))

    def test_get_player_move_acquire_connection_not_enough_cards_for_first_avaialable_connection(self):
        cc = {Color.RED: 10, Color.BLUE: 0, Color.GREEN: 10, Color.WHITE: 10}
        pgs = PlayerGameState(set(), cc, 45, set(), list())
        # Given player game state has more than 10 cards, so acquire a connection
        # self.connection4 comes first lexicographically but the pgs does the necessary blue cards
        # The strategy resorts to self.connection8, which is the next acquireable connection lexicographically
        self.assertEqual(self.h10_strat.get_player_move(pgs, self.game_map), \
            AcquireConnectionMove(self.connection8))

    def test_get_player_move_acquire_connection_first_avaialable_connection_already_acquired(self):
        cc = {Color.RED: 10, Color.BLUE: 10, Color.GREEN: 10, Color.WHITE: 10}
        pgs = PlayerGameState(set(), cc, 45, set(), [{self.connection4}])
        # Given player game state has more than 10 cards, so acquire a connection
        # self.connection4 comes first lexicographically but the pgs has knowledge that another player has already acquired it
        # The strategy resorts to self.connection8, which is the next acquireable connection lexicographically
        self.assertEqual(self.h10_strat.get_player_move(pgs, self.game_map), \
            AcquireConnectionMove(self.connection8))

    def test_get_player_move_acquire_connection_no_acquireable_connections(self):
        cc = {Color.RED: 10, Color.BLUE: 10, Color.GREEN: 10, Color.WHITE: 10}
        pgs = PlayerGameState(set(), cc, 45, set(), [self.all_connections])
        # Given player game state has more than 10 cards, so acquire a connection
        # All connections are already acquired according to the pgs other acquisitions, so draw cards
        self.assertEqual(self.h10_strat.get_player_move(pgs, self.game_map), DrawCardMove())
        

class TestStrategyBuyNow(unittest.TestCase):
    def setUp(self):
        self.boston = City("Boston", 70, 20)
        self.new_york = City("New York", 60, 30)
        self.austin = City("Austin", 50, 80)
        self.houston = City("Houston", 50, 90)
        self.philadelphia = City("Philadelphia", 60, 70)
        self.los_angeles = City("Los Angeles", 0, 10)
        self.wdc = City("Washington D.C.", 55, 60)
        self.cities = {self.boston, self.new_york, self.austin,
                       self.houston, self.philadelphia, self.los_angeles, self.wdc}

        self.connection1 = Connection(
            frozenset({self.boston, self.new_york}), Color.BLUE, 4)
        self.connection2 = Connection(
            frozenset({self.new_york, self.philadelphia}), Color.GREEN, 3)
        self.connection3 = Connection(
            frozenset({self.boston, self.philadelphia}), Color.GREEN, 4)
        self.connection4 = Connection(
            frozenset({self.austin, self.los_angeles}), Color.BLUE, 5)
        self.connection5 = Connection(
            frozenset({self.philadelphia, self.wdc}), Color.WHITE, 3)
        self.connection6 = Connection(
            frozenset({self.philadelphia, self.wdc}), Color.WHITE, 4)
        self.connection7 = Connection(
            frozenset({self.philadelphia, self.wdc}), Color.RED, 4)
        self.connection8 = Connection(
            frozenset({self.austin, self.los_angeles}), Color.GREEN, 5)
        self.all_connections = {self.connection1, self.connection2, self.connection3, self.connection4,
                                self.connection5, self.connection6, self.connection7, self.connection8}

        self.game_map = Map(self.cities, self.all_connections)

        self.dest1 = Destination(frozenset({self.austin, self.new_york}))
        self.dest2 = Destination(frozenset({self.boston, self.houston}))
        self.dest3 = Destination(frozenset({self.austin, self.houston}))
        self.dest4 = Destination(frozenset({self.new_york, self.philadelphia}))
        self.dest5 = Destination(frozenset({self.los_angeles, self.wdc}))

        self.destination_options = {self.dest1, self.dest2, self.dest3, self.dest4, self.dest5}

        self.NUM_DESTINATIONS_TO_SELECT = 2
        self.NUM_DESTINATIONS_OPTIONS = 5

        self.bn_strat = Buy_Now()

    def test_select_destinations_select_two(self):
        # Buy now picks the back of the lexicographical ordering of destinations
        destinations = self.bn_strat.select_destinations(
            self.destination_options, self.NUM_DESTINATIONS_TO_SELECT)
        self.assertEqual(destinations, {self.dest4, self.dest5})

    def test_select_destinations_select_three(self):
        number_of_destination = 3
        destinations = self.bn_strat.select_destinations(
            self.destination_options, number_of_destination)
        self.assertEqual(destinations, {self.dest2, self.dest4, self.dest5})

    def test_get_player_move_draw_cards(self):
        cc = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        pgs = PlayerGameState(set(), cc, 45, set(), list())
        # Attempt to acquire connection, but doesn't have the necessary cards. Draw cards instead.
        self.assertEqual(self.bn_strat.get_player_move(pgs, self.game_map), DrawCardMove())

    def test_get_player_move_acquire_connection_exactly_enough_cards(self):
        cc = {Color.RED: 0, Color.BLUE: 5, Color.GREEN: 0, Color.WHITE: 0}
        pgs = PlayerGameState(set(), cc, 45, set(), list())
        # self.connection4 comes first lexicographically and the pgs has the necessary resources
        self.assertEqual(self.bn_strat.get_player_move(pgs, self.game_map), \
            AcquireConnectionMove(self.connection4))

    def test_get_player_move_acquire_connection_not_enough_cards_for_first_available_connection(self):
        cc = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 4, Color.WHITE: 0}
        pgs = PlayerGameState(set(), cc, 45, set(), list())
        # self.connection4 comes first lexicographically but the pgs does the necessary blue cards
        # The strategy resorts to self.connection3, which is the next acquireable connection lexicographically
        self.assertEqual(self.bn_strat.get_player_move(pgs, self.game_map), \
            AcquireConnectionMove(self.connection3))

    def test_get_player_move_acquire_connection_first_available_connection_already_acquired(self):
        cc = {Color.RED: 0, Color.BLUE: 4, Color.GREEN: 4, Color.WHITE: 0}
        pgs = PlayerGameState(set(), cc, 45, set(), [{self.connection4}])
        # self.connection4 comes first lexicographically but the pgs has knowledge that another player has already acquired it
        # The strategy resorts to self.connection1, which is the next acquireable connection lexicographically
        self.assertEqual(self.bn_strat.get_player_move(pgs, self.game_map), \
            AcquireConnectionMove(self.connection1))

    def test_get_player_move_acquire_connection_no_acquireable_connections(self):
        cc = {Color.RED: 10, Color.BLUE: 10, Color.GREEN: 10, Color.WHITE: 10}
        pgs = PlayerGameState(set(), cc, 45, set(), [self.all_connections])
        # All connections are already acquired according to the pgs other acquisitions, so draw cards
        self.assertEqual(self.bn_strat.get_player_move(pgs, self.game_map), DrawCardMove())

    # Select connection is the same for Hold 10 and Buy Now
    def test_select_connection(self):
        cc = {Color.RED: 10, Color.BLUE: 10, Color.GREEN: 10, Color.WHITE: 10}
        pgs = PlayerGameState(set(), cc, 45, set(), [{self.connection4, self.connection8}])
        connection = self.bn_strat._select_connection(pgs, self.game_map)
        exp_connection = self.connection1
        self.assertEqual(connection, exp_connection)

    def test_select_connection_second_city_name_tie_breaker(self):
        cc = {Color.RED: 0, Color.BLUE: 5, Color.GREEN: 6, Color.WHITE: 0}
        pgs = PlayerGameState(set(), cc, 45, set(), [{self.connection4, self.connection8}])
        connection = self.bn_strat._select_connection(pgs, self.game_map)
        exp_connection = self.connection1
        # Chooses between connection 1 (boston to new york) and 3 (boston to philly)
        self.assertEqual(connection, exp_connection)
    
    def test_select_connection_length_tie_breaker(self):
        cc = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 12}
        pgs = PlayerGameState(set(), cc, 45, set(), [])
        connection = self.bn_strat._select_connection(pgs, self.game_map)
        exp_connection = self.connection5
        # Chooses between connections from philly and wdc with different lengths
        # Connection 5 (length 3) and connection 6 (length 4)
        self.assertEqual(connection, exp_connection)

    def test_select_connection_color_tie_breaker(self):
        cc = {Color.RED: 10, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 12}
        pgs = PlayerGameState(set(), cc, 45, set(), [{self.connection5}])
        connection = self.bn_strat._select_connection(pgs, self.game_map)
        exp_connection = self.connection7
        # Chooses between connections from philly and wdc with same lengths and different
        # colors. Connection 6 (white) and connection 7 (red).
        self.assertEqual(connection, exp_connection)

    def test_select_connection_all_connections_acquired(self):
        cc = {Color.RED: 10, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 12}
        pgs = PlayerGameState(set(), cc, 45, set(), [self.all_connections])
        connection = self.bn_strat._select_connection(pgs, self.game_map)
        # All connections are already acquired, so return none
        self.assertIsNone(connection)

    def test_select_connection_no_acquireable_connections_not_enough_cards(self):
        cc = {Color.RED: 2, Color.BLUE: 10, Color.GREEN: 10, Color.WHITE: 2}
        pgs = PlayerGameState(set(), cc, 45, set(), [{self.connection1, self.connection2, \
            self.connection3, self.connection4, self.connection8}])
        connection = self.bn_strat._select_connection(pgs, self.game_map)
        # All connections are already acquired, so return none
        self.assertIsNone(connection)

    def test_select_connection_no_acquireable_connections_not_enough_rails(self):
        num_rails = 2
        cc = {Color.RED: 12, Color.BLUE: 10, Color.GREEN: 10, Color.WHITE: 12}
        pgs = PlayerGameState(set(), cc, num_rails, set(), [])
        connection = self.bn_strat._select_connection(pgs, self.game_map)
        # All connections are already acquired, so return none
        self.assertIsNone(connection)

    def test_select_connection_no_acquireable_connections_this_player_acquired_already(self):
        cc = {Color.RED: 12, Color.BLUE: 10, Color.GREEN: 10, Color.WHITE: 12}
        pgs = PlayerGameState(self.all_connections, cc, 45, set(), [])
        connection = self.bn_strat._select_connection(pgs, self.game_map)
        # All connections are already acquired, so return none
        self.assertIsNone(connection)

if __name__ == '__main__':
    unittest.main()

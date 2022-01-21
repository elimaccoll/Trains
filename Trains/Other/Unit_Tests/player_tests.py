import os
import sys
import unittest

sys.path.append('../../../')
from Trains.Common.map import City, Color, Connection, Destination, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Other.Util.gs_utils import can_acquire_connection
from Trains.Other.Util.test_utils import (IsAcquireConnectionMove,
                                          IsDrawCardMove)
from Trains.Other.Util.constants import DEFAULT_MAP
from Trains.Player.buy_now import Buy_Now
from Trains.Player.hold_10 import Hold_10
from Trains.Player.moves import DrawCardMove
from Trains.Player.player import (Buy_Now_Player, Hold_10_Player,
                                  StrategicPlayer)
from Trains.Player.player_interface import PlayerInterface


class TestPlayerHold10(unittest.TestCase):
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
            frozenset({self.philadelphia, self.new_york}), Color.GREEN, 3)
        self.connection3 = Connection(
            frozenset({self.boston, self.philadelphia}), Color.GREEN, 4)
        self.connection4 = Connection(
            frozenset({self.austin, self.los_angeles}), Color.BLUE, 5)
        self.connection5 = Connection(
            frozenset({self.wdc, self.philadelphia}), Color.WHITE, 3)
        self.connection6 = Connection(
            frozenset({self.wdc, self.philadelphia}), Color.WHITE, 4)
        self.connection7 = Connection(
            frozenset({self.wdc, self.philadelphia}), Color.RED, 4)
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

        self.name = "h10"
        self.h10 = Hold_10_Player(self.name)
        self.h10_initial_cards = {Color.RED: 0,
                                  Color.BLUE: 4, Color.GREEN: 0, Color.WHITE: 0}
        self.h10_initial_rails = 45
        self.h10_destinations = {self.dest1, self.dest2, self.dest3}
        self.h10_other_acquisitions = [set(), set()]

    def test_hold_10_constructor(self):
        test_player = Hold_10_Player(self.name)

        self.assertEqual(test_player.name, self.name)
        self.assertEqual(type(test_player.strategy), Hold_10)

    def test_hold_10_constructor_invalid_name_type(self):
        with self.assertRaises(TypeError):
            Hold_10_Player(1)

    def test_setup(self):
        self.h10.setup(DEFAULT_MAP, self.h10_initial_rails, self.h10_initial_cards)
        self.assertEqual(self.h10.game_map, DEFAULT_MAP)

    def test_hold_10_pick(self):
        not_chosen = self.h10.pick(self.destination_options)
        exp_chosen = {self.dest3, self.dest1}
        exp_not_chosen = self.destination_options - exp_chosen
        self.assertEqual(not_chosen, exp_not_chosen)

    def test_compute_destinations_to_return(self):
        exp_chosen = {self.dest3, self.dest1}
        exp_not_chosen = self.destination_options - exp_chosen
        not_chosen = self.h10._compute_destinations_to_return(self.destination_options, exp_chosen)
        self.assertEqual(not_chosen, exp_not_chosen)

    def test_play_called_before_setup(self):
        cards = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        pgs = PlayerGameState(set(), cards, self.h10_initial_rails,
                              self.h10_destinations, self.h10_other_acquisitions)
        with self.assertRaises(RuntimeError):
            self.h10.play(pgs)

    def test_play_hold_10_draw_cards(self):
        cards = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        self.h10.setup(
            self.game_map, self.h10_initial_rails, self.h10_initial_cards)
        pgs = PlayerGameState(set(), cards, self.h10_initial_rails,
                              self.h10_destinations, self.h10_other_acquisitions)
        move = self.h10.play(pgs)
        self.assertTrue(move.accepts(IsDrawCardMove()))

    def test_play_hold_10_draw_exactly_10_cards(self):
        cards = {Color.RED: 5, Color.BLUE: 3, Color.GREEN: 1, Color.WHITE: 1}
        self.h10.setup(
            self.game_map, self.h10_initial_rails, self.h10_initial_cards)
        pgs = PlayerGameState(set(), cards, self.h10_initial_rails,
                              self.h10_destinations, self.h10_other_acquisitions)
        move = self.h10.play(pgs)
        self.assertTrue(move.accepts(IsDrawCardMove()))

    def test_play_hold_10_more_than_10_cards(self):
        cards = {Color.RED: 5, Color.BLUE: 3, Color.GREEN: 2, Color.WHITE: 1}
        self.h10.setup(
            self.game_map, self.h10_initial_rails, self.h10_initial_cards)
        pgs = PlayerGameState(set(), cards, self.h10_initial_rails,
                              self.h10_destinations, self.h10_other_acquisitions)
        move = self.h10.play(pgs)
        # Has 10 or more cards, so will attempt to acquire a connection
        # Connection 7 is the only connection that the pgs has the necessary cards to acquire.
        self.assertTrue(move.accepts(
            IsAcquireConnectionMove(self.connection7)))

    def test_get_move_hold_10_break_tie_with_length(self):
        cards = {Color.RED: 5, Color.BLUE: 1, Color.GREEN: 0, Color.WHITE: 5}
        self.h10.setup(
            self.game_map, self.h10_initial_rails, self.h10_initial_cards)

        pgs = PlayerGameState(set(), cards, self.h10_initial_rails,
                              self.h10_destinations, self.h10_other_acquisitions)

        move = self.h10.play(pgs)
        self.assertTrue(move.accepts(
            IsAcquireConnectionMove(self.connection5)))

    def test_get_move_hold_10_break_tie_with_color(self):
        cards = {Color.RED: 5, Color.BLUE: 5, Color.GREEN: 0, Color.WHITE: 1}
        self.h10.setup(
            self.game_map, self.h10_initial_rails, self.h10_initial_cards)

        pgs = PlayerGameState(set(), cards, self.h10_initial_rails,
                              self.h10_destinations, self.h10_other_acquisitions)

        move = self.h10.play(pgs)
        self.assertTrue(move.accepts(
            IsAcquireConnectionMove(self.connection4)))

    def test_can_acquire_connection_true(self):
        cards = {Color.RED: 5, Color.BLUE: 5, Color.GREEN: 0, Color.WHITE: 1}
        pgs = PlayerGameState(set(), cards, self.h10_initial_rails,
                              self.h10_destinations, self.h10_other_acquisitions)
        self.assertTrue(can_acquire_connection(pgs, self.connection1))

    def test_can_acquire_connection_false_not_enough_cards(self):
        cards = {Color.RED: 1, Color.BLUE: 2, Color.GREEN: 0, Color.WHITE: 1}
        pgs = PlayerGameState(set(), cards, self.h10_initial_rails,
                              self.h10_destinations, self.h10_other_acquisitions)
        self.assertFalse(can_acquire_connection(pgs, self.connection1))

    def test_can_acquire_connection_false_not_enough_rails(self):
        num_rails = 2
        cards = {Color.RED: 10, Color.BLUE: 20, Color.GREEN: 10, Color.WHITE: 10}
        pgs = PlayerGameState(set(), cards, num_rails,
                              self.h10_destinations, self.h10_other_acquisitions)
        self.assertFalse(can_acquire_connection(pgs, self.connection1))

    # can_acquire_connection is only called in the context that the given connection
    # is unacquired, so the tests below return True
    def test_can_acquire_connection_already_acquired_by_different_player(self):
        cards = {Color.RED: 10, Color.BLUE: 20, Color.GREEN: 10, Color.WHITE: 10}
        pgs = PlayerGameState(set(), cards, self.h10_initial_rails,
                              self.h10_destinations, [{self.connection1}])
        self.assertTrue(can_acquire_connection(pgs, self.connection1))

    def test_can_acquire_connection_already_acquired_by_this_player(self):
        cards = {Color.RED: 10, Color.BLUE: 20, Color.GREEN: 10, Color.WHITE: 10}
        pgs = PlayerGameState({self.connection1}, cards, self.h10_initial_rails,
                              self.h10_destinations, [])
        self.assertTrue(can_acquire_connection(pgs, self.connection1))


class TestPlayerBuyNow(unittest.TestCase):
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

        self.age = 20
        self.name = "test_player_buy_now"
        self.bn = Buy_Now_Player(self.name)
        self.bn_initial_cards = {Color.RED: 2,
                                 Color.BLUE: 4, Color.GREEN: 3, Color.WHITE: 2}
        self.bn_initial_rails = 45
        self.bn_destinations = {self.dest1, self.dest2, self.dest3}
        self.bn_other_acquisitions = [set(), set()]

    def test_buy_now_constructor(self):
        test_player = Buy_Now_Player(self.name)

        self.assertEqual(test_player.name, self.name)
        self.assertEqual(type(test_player.strategy), Buy_Now)

    def test_select_destinations_select_two_buy_now(self):
        number_of_destination = 2
        destinations = self.bn.strategy.select_destinations(
            self.bn_destinations, number_of_destination)
        self.assertEqual(destinations, {self.dest1, self.dest2})

    def test_select_destinations_select_three_buy_now(self):
        number_of_destination = 3
        destinations = self.bn.strategy.select_destinations(
            self.bn_destinations, number_of_destination)
        self.assertEqual(destinations, {self.dest1, self.dest2, self.dest3})

    def test_select_destinations_invalid_select_number_buy_now(self):
        number_of_destination = 4
        with self.assertRaises(ValueError):
            destinations = self.bn.strategy.select_destinations(
                self.bn_destinations, number_of_destination)

    def test_get_move_buy_now_draw_not_enough_cards(self):
        cards = {Color.RED: 2, Color.BLUE: 2, Color.GREEN: 2, Color.WHITE: 2}
        self.bn.setup(
            self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        pgs = PlayerGameState(set(), cards, self.bn_initial_rails,
                              self.bn_destinations, self.bn_other_acquisitions)
        move = self.bn.play(pgs)
        self.assertTrue(move.accepts(IsDrawCardMove()))

    def test_get_move_buy_now_draw_at_exactly_10(self):
        cards = {Color.RED: 3, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        self.bn.setup(
            self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        pgs = PlayerGameState(set(), cards, self.bn_initial_rails,
                              self.bn_destinations, self.bn_other_acquisitions)
        move = self.bn.play(pgs)
        self.assertTrue(move.accepts(IsDrawCardMove()))

    def test_get_move_buy_now_enough_cards_to_aquire(self):
        cards = {Color.RED: 11, Color.BLUE: 2, Color.GREEN: 0, Color.WHITE: 0}
        self.bn.setup(
            self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        pgs = PlayerGameState(set(), cards, self.bn_initial_rails,
                              self.bn_destinations, self.bn_other_acquisitions)
        move = self.bn.play(pgs)
        self.assertTrue(move.accepts(
            IsAcquireConnectionMove(self.connection7)))

    def test_get_move_buy_now_break_tie_with_length(self):
        cards = {Color.RED: 5, Color.BLUE: 1, Color.GREEN: 0, Color.WHITE: 5}
        self.bn.setup(
            self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        pgs = PlayerGameState(set(), cards, self.bn_initial_rails,
                              self.bn_destinations, self.bn_other_acquisitions)
        move = self.bn.play(pgs)
        self.assertTrue(move.accepts(
            IsAcquireConnectionMove(self.connection5)))

    def test_get_move_buy_now_break_tie_with_color(self):
        cards = {Color.RED: 5, Color.BLUE: 5, Color.GREEN: 0, Color.WHITE: 1}
        self.bn.setup(
            self.game_map, self.bn_initial_rails, self.bn_initial_cards)
        pgs = PlayerGameState(set(), cards, self.bn_initial_rails,
                              self.bn_destinations, self.bn_other_acquisitions)
        move = self.bn.play(pgs)
        self.assertTrue(move.accepts(
            IsAcquireConnectionMove(self.connection4)))


class TestPlayerDynamicallyLoadedStrategy(unittest.TestCase):
    def setUp(self):
        self.name = "test_player_draw_cards"
        self.rel_filepath = "../Strategies/draw_cards_strat.py"
        self.abs_filepath = os.path.abspath(self.rel_filepath)

    def test_constructor_absolute_file_path(self):
        initial_rails = 45
        initial_cards = {Color.RED: 2, Color.GREEN: 1, Color.WHITE: 0, Color.BLUE: 1}
        draw_cards_player: PlayerInterface = StrategicPlayer.create_player_from_strategy_file_path(
            self.abs_filepath, self.name)
        self.assertEqual(draw_cards_player.get_name(), self.name)
        draw_cards_player.setup(DEFAULT_MAP, initial_rails, initial_cards)
        self.assertEqual(draw_cards_player.game_map, DEFAULT_MAP)
        pgs = PlayerGameState(set(), {
                              Color.RED: 0, Color.GREEN: 0, Color.BLUE: 0, Color.WHITE: 0}, 0, set(), [])
        self.assertEqual(draw_cards_player.play(pgs), DrawCardMove())


if __name__ == '__main__':
    unittest.main()

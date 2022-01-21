import sys
import unittest
from collections import deque
from copy import deepcopy
from typing import Deque, Dict, List

sys.path.append('../../../')

from Trains.Admin.referee import (ApplyPlayerMove, Cheating,
                                  NotEnoughDestinations, Referee, IsPlayerMoveLegal)
from Trains.Admin.referee_game_state import RefereeGameState
from Trains.Common.map import City, Color, Connection, Destination, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Other.Mocks.mock_bad_pick_player import MockBadPickPlayer
from Trains.Other.Mocks.mock_bad_setup_player import MockBadSetUpPlayer
from Trains.Other.Mocks.mock_configurable_player import (
    MockBuyNowPlayer, MockConfigurablePlayer)
from Trains.Other.Util.constants import MIN_RAILS_TO_NOT_TRIGGER_LAST_TURN, int2color
from Trains.Player.moves import AcquireConnectionMove, DrawCardMove
from Trains.Player.player import Buy_Now_Player, Hold_10_Player
from Trains.Player.player_interface import PlayerInterface


class TestReferee(unittest.TestCase):
    def setUp(self):
        # Setup a Map
        self.boston = City("Boston", 70, 80)
        self.new_york = City("New York", 60, 70)
        self.philadelphia = City("Philadelphia", 90, 10)
        self.los_angeles = City("Los Angeles", 0, 10)
        self.austin = City("Austin", 50, 10)
        self.wdc = City("Washington D.C.", 55, 60)
        self.boise = City("Boise", 30, 50)

        self.connection1 = Connection(
            frozenset({self.boston, self.new_york}), Color.BLUE, 3)
        self.connection2 = Connection(
            frozenset({self.boston, self.new_york}), Color.RED, 3)
        self.connection3 = Connection(
            frozenset({self.boston, self.new_york}), Color.GREEN, 3)
        self.connection4 = Connection(
            frozenset({self.boston, self.new_york}), Color.WHITE, 3)
        self.connection5 = Connection(
            frozenset({self.philadelphia, self.new_york}), Color.RED, 4)
        self.connection6 = Connection(
            frozenset({self.philadelphia, self.new_york}), Color.GREEN, 4)
        self.connection7 = Connection(
            frozenset({self.philadelphia, self.new_york}), Color.WHITE, 4)
        self.connection8 = Connection(
            frozenset({self.boston, self.philadelphia}), Color.GREEN, 4)
        self.connection9 = Connection(
            frozenset({self.boston, self.philadelphia}), Color.BLUE, 4)
        self.connection10 = Connection(
            frozenset({self.austin, self.los_angeles}), Color.BLUE, 5)
        self.connection11 = Connection(
            frozenset({self.philadelphia, self.wdc}), Color.WHITE, 5)
        self.connection12 = Connection(
            frozenset({self.austin, self.boise}), Color.RED, 5)
        self.connection13 = Connection(
            frozenset({self.boise, self.los_angeles}), Color.GREEN, 5)
        self.connection14 = Connection(
            frozenset({self.boise, self.philadelphia}), Color.RED, 5)
        self.connection15 = Connection(
            frozenset({self.boise, self.wdc}), Color.GREEN, 5)
        self.bad_connection = Connection(frozenset({City("this does not exist", -10, -10), City(
            "this does not exist either", -11, -11)}), Color.GREEN, 3)

        self.destination1 = Destination({self.boston, self.wdc})
        self.destination2 = Destination({self.austin, self.boise})
        self.destination3 = Destination({self.philadelphia, self.new_york})
        self.destination4 = Destination({self.boston, self.new_york})
        self.destination5 = Destination({self.boise, self.philadelphia})

        self.cities = {self.boston, self.new_york, self.philadelphia,
                       self.los_angeles, self.austin, self.wdc, self.boise}
        self.connections = {self.connection1, self.connection2, self.connection3, self.connection4, self.connection5, self.connection6, self.connection7,
                            self.connection8, self.connection9, self.connection10, self.connection11, self.connection12, self.connection13, self.connection14, self.connection15}
        self.width = 800
        self.height = 800
        self.game_map = Map(self.cities, self.connections,
                            self.height, self.width)

        # Setup ref constants/fields for testing
        self.INITIAL_DECK_SIZE = 250
        self.INITIAL_RAIL_COUNT = 45
        self.INITIAL_NUM_DESTINATIONS = 2
        self.NUM_DESTINATION_OPTIONS = 5
        self.INITIAL_HAND_SIZE = 4
        self.DRAW_NUM = 2
        self.RAIL_SEGMENT_POINT_VALUE = 1
        self.LONGEST_CONTINUOUS_PATH_VALUE = 20
        self.DESTINATION_COMPLETE_VALUE = 10
        self.BANNED_PLAYER_SCORE_REPRESENTATION = -21
        self.feasible_destinations = self.game_map.get_feasible_destinations(
            self.connections)

        # players list
        self.p1_name = "p1"
        self.p2_name = "p2"
        self.p3_name = "p3"
        self.player_names = [self.p1_name, self.p2_name, self.p3_name]
        self.p1 = Hold_10_Player(self.p1_name)
        self.p2 = Hold_10_Player(self.p2_name)
        self.p3 = Buy_Now_Player(self.p3_name)

        self.players: List[PlayerInterface] = [self.p1, self.p2, self.p3]
        self.ref = Referee(self.game_map, self.players)
        self.deck = self.ref.initialize_deck(self.INITIAL_DECK_SIZE)

    def test_constructor(self):
        ref = Referee(self.game_map, self.players)
        self.assertEqual(ref.game_map, self.game_map)
        self.assertEqual(ref.players, self.players)
        self.assertEqual(ref.ban_list, set())
        self.assertEqual(ref.took_last_turn, set())
        # Check that the ref_game_state was initialized properly
        self.assertEqual(ref.ref_game_state.game_map, self.ref.game_map)
        self.assertEqual(len(ref.ref_game_state.colored_card_deck),
                         self.INITIAL_DECK_SIZE - (len(self.players) * self.INITIAL_HAND_SIZE))
        for card in ref.ref_game_state.colored_card_deck:
            self.assertEqual(type(card), Color)

    def test_constructor_invalid_map(self):
        with self.assertRaises(TypeError):
            ref = Referee(self.connections, self.players)

    def test_constructor_invalid_num_players_out_of_bounds_too_few(self):
        with self.assertRaises(ValueError):
            players = [self.p1]
            ref = Referee(self.game_map, players)

    def test_constructor_invalid_num_players_out_of_bounds_too_many(self):
        with self.assertRaises(ValueError):
            players = [self.p1] * 10
            ref = Referee(self.game_map, players)

    def test_constructor_invalid_players_not_list(self):
        with self.assertRaises(TypeError):
            players = {self.p1, self.p2, self.p3}
            ref = Referee(self.game_map, players)

    def test_constructor_not_enough_destinations(self):
        cities = {self.boston, self.new_york}
        connections = {self.connection1}
        width = 800
        height = 800
        test_map = Map(cities, connections, height, width)
        with self.assertRaises(NotEnoughDestinations):
            ref = Referee(test_map, self.players)

    def test_constructor_invalid_deck_type(self):
        with self.assertRaises(TypeError):
            deck = [Color.RED]
            ref = Referee(self.game_map, self.players, deck)

    def test_constructor_invalid_deck_entry_type(self):
        with self.assertRaises(TypeError):
            deck = deque([Color.RED, "red"])
            ref = Referee(self.game_map, self.players, deck)

    def test_initialize_deck(self):
        deck = self.ref.initialize_deck(self.INITIAL_DECK_SIZE)

        for card in deck:
            self.assertEqual(type(card), Color)

        self.assertEqual(len(deck), self.INITIAL_DECK_SIZE)

    def test_create_initial_player_hand(self):
        hand = self.ref.create_initial_player_hand(
            self.deck, self.INITIAL_HAND_SIZE)
        self.assertEqual(type(hand), dict)
        self.assertEqual(sum(hand.values()), self.INITIAL_HAND_SIZE)
        str_colors = set()
        for i in range(1, Color.number_of_colors() + 1):
            str_colors.add(int2color[i])
        for card_color in hand.keys():
            self.assertIn(card_color, str_colors)

    def test_set_up_players_with_initial_game_states(self):
        formatted_player_states = self.ref.set_up_players_with_initial_game_states(
            self.players, self.deck, self.INITIAL_RAIL_COUNT, self.feasible_destinations)
        player_destinations = set()

        for player_state in formatted_player_states:
            self.assertEqual(player_state.connections, set())
            self.assertEqual(player_state.other_acquisitions,
                             [set(), set(), set()])
            self.assertEqual(len(player_state.destinations),
                             self.INITIAL_NUM_DESTINATIONS)
            # Checks that no two players have the same destination
            for destination in player_state.destinations:
                self.assertNotIn(destination, player_destinations)
                player_destinations.add(destination)
            self.assertEqual(
                player_state.get_total_cards(), self.INITIAL_HAND_SIZE)
            self.assertEqual(player_state.rails, self.INITIAL_RAIL_COUNT)

    def test_generate_initial_player_state(self):
        initial_hand = {Color.RED: 4, Color.BLUE: 0,
                        Color.GREEN: 0, Color.WHITE: 0}
        initial_rails = 45
        destinations = {self.destination1, self.destination2}
        game_state = self.ref.generate_initial_player_state(initial_hand, initial_rails,
                                                    destinations, len(self.players))
        self.assertEqual(game_state.get_total_cards(), 4)
        self.assertEqual(game_state.other_acquisitions, [set(), set(), set()])
        self.assertEqual(game_state.destinations, destinations)
        self.assertEqual(game_state.colored_cards, initial_hand)
        self.assertEqual(game_state.rails, initial_rails)

    def test_get_destination_selection(self):
        destination_options = self.ref.get_destination_selection(
            self.feasible_destinations, self.NUM_DESTINATION_OPTIONS)
        self.assertEqual(len(destination_options),
                         self.NUM_DESTINATION_OPTIONS)
        for destination in destination_options:
            self.assertIn(destination, self.feasible_destinations)

    def test_verify_player_destinations_valid(self):
        destinations_given = set({self.destination1, self.destination2,
                                 self.destination3, self.destination4, self.destination5})
        destinations_chosen = set({self.destination1, self.destination2})
        self.assertTrue(self.ref.verify_player_destinations(
            destinations_given, destinations_chosen))

    def test_verify_player_destinations_invalid_number_of_destinations_too_many(self):
        destinations_given = set({self.destination1, self.destination2,
                                 self.destination3, self.destination4, self.destination5})
        destinations_chosen = set(
            {self.destination1, self.destination2, self.destination3})
        self.assertFalse(self.ref.verify_player_destinations(
            destinations_given, destinations_chosen))

    def test_verify_player_destinations_invalid_number_of_destinations_too_few(self):
        destinations_given = set({self.destination1, self.destination2,
                                 self.destination3, self.destination4, self.destination5})
        destinations_chosen = set({self.destination1})
        self.assertFalse(self.ref.verify_player_destinations(
            destinations_given, destinations_chosen))

    def test_verify_player_destinations_invalid_destination_chosen(self):
        destinations_given = set({self.destination1, self.destination2,
                                 self.destination3, self.destination4, self.destination5})
        destination_not_given = Destination({self.boise, self.los_angeles})
        destinations_chosen = set({self.destination1, destination_not_given})
        self.assertFalse(self.ref.verify_player_destinations(
            destinations_given, destinations_chosen))

    def test_boot_player(self):
        pgs_before_boot = self.ref.ref_game_state.player_game_states[0]
        banned_player_connections = pgs_before_boot.connections
        self.ref.boot_player(0, "Cheating")
        exp_ban_list = {0}
        pgs = self.ref.ref_game_state.player_game_states[0]
        self.assertEqual(self.ref.ban_list, exp_ban_list)
        # Should have no connections after being banned
        self.assertEqual(pgs.connections, set())
        # Should have no colored cards after being banned
        self.assertEqual(pgs.colored_cards, dict())
        # Should have the minimum number of rails without triggering end game
        self.assertEqual(pgs.rails, MIN_RAILS_TO_NOT_TRIGGER_LAST_TURN)
        # Should have no information on other player acquisitions
        self.assertEqual(pgs.other_acquisitions, [])
        # Their connections were freed to the game again
        for connection in banned_player_connections:
            self.assertIn(
                connection, self.ref.ref_game_state.get_all_unacquired_connections())

    def test_ban_player(self):
        self.ref.boot_player(0, "Cheating")
        exp_ban_list = {0}
        self.assertEqual(self.ref.ban_list, exp_ban_list)
        self.ref.boot_player(1, "Cheating")
        exp_ban_list.add(1)
        self.assertEqual(self.ref.ban_list, exp_ban_list)

    def test_is_game_over_true_all_last_turns_taken(self):
        new_ref = Referee(self.game_map, self.players, self.deck)
        old_pgs = new_ref.ref_game_state.player_game_states[0]
        new_ref.ref_game_state.player_game_states[0] = PlayerGameState(
            old_pgs.connections, old_pgs.colored_cards, 1, old_pgs.destinations, old_pgs.other_acquisitions)
        new_ref.took_last_turn = set(self.players)
        self.assertTrue(new_ref.is_game_over())

    def test_is_game_over_false(self):
        self.assertFalse(self.ref.is_game_over())

    def test_is_game_over_false_one_player_remaining(self):
        self.ref.ban_list.add(0)
        self.ref.ban_list.add(1)
        self.assertFalse(self.ref.is_game_over())

    def test_is_game_over_true_no_players_remaining(self):
        for index in range(len(self.players)):
            self.ref.ban_list.add(index)
        self.assertTrue(self.ref.is_game_over())

    def test_is_game_over_false_player_kicked_more_than_one_player_remaining(self):
        self.ref.ban_list.add(self.players[0])
        self.assertFalse(self.ref.is_game_over())

    def test_is_game_over_same_states(self):
        self.ref.num_of_same_states = len(self.players)
        self.assertTrue(self.ref.is_game_over())

    def test_apply_draw_move(self):
        deck = deque([Color.GREEN, Color.RED, Color.RED])
        self.ref.ref_game_state.colored_card_deck = deck
        hand_before_draw = self.ref.ref_game_state.player_game_states[0].colored_cards
        exp_hand = deepcopy(hand_before_draw)
        if Color.RED in exp_hand.keys():
            exp_hand[Color.RED] += 2
        else:
            exp_hand[Color.RED] = 2

        DrawCardMove().accepts(ApplyPlayerMove(
            self.ref.ref_game_state, self.ref.get_active_player()))

        self.assertEqual(
            self.ref.ref_game_state.player_game_states[0].colored_cards, exp_hand)
        self.assertEqual(
            self.ref.ref_game_state.colored_card_deck, deque([Color.GREEN]))

    def test_apply_draw_move_not_the_full_amount_drawn(self):
        deck = deque([Color.RED])
        self.ref.ref_game_state.colored_card_deck = deck
        hand_before_draw = self.ref.ref_game_state.player_game_states[0].colored_cards
        exp_hand = deepcopy(hand_before_draw)
        if Color.RED in exp_hand.keys():
            exp_hand[Color.RED] += 1
        else:
            exp_hand[Color.RED] = 1

        DrawCardMove().accepts(ApplyPlayerMove(
            self.ref.ref_game_state, self.ref.get_active_player()))

        self.assertEqual(
            self.ref.ref_game_state.player_game_states[0].colored_cards, exp_hand)
        self.assertEqual(self.ref.ref_game_state.colored_card_deck, deque())

    def test_apply_draw_move_none_drawn_empty_deck(self):
        deck = deque()
        self.ref.ref_game_state.colored_card_deck = deck
        hand_before_draw = self.ref.ref_game_state.player_game_states[0].colored_cards
        exp_hand = hand_before_draw

        DrawCardMove().accepts(ApplyPlayerMove(
            self.ref.ref_game_state, self.ref.get_active_player()))

        self.assertEqual(
            self.ref.ref_game_state.player_game_states[0].colored_cards, exp_hand)
        self.assertEqual(self.ref.ref_game_state.colored_card_deck, deque())

    def test_apply_acquire_connection_move(self):
        SET_BLUE_CARDS = 20
        colored_cards = {Color.RED: 0, Color.BLUE: SET_BLUE_CARDS, Color.GREEN: 0, Color.WHITE: 0} 
        pgs = self.ref.ref_game_state.player_game_states[0]
        self.ref.ref_game_state.player_game_states[0] = PlayerGameState(pgs.connections, colored_cards, \
            pgs.rails, pgs.destinations, pgs.other_acquisitions)

        connection_to_acquire = self.connection1

        AcquireConnectionMove(connection_to_acquire).accepts(ApplyPlayerMove(
            self.ref.ref_game_state, self.ref.get_active_player()))

        self.assertEqual(
            self.ref.ref_game_state.player_game_states[0].colored_cards[Color.BLUE], SET_BLUE_CARDS - connection_to_acquire.length)
        self.assertEqual(
            self.ref.ref_game_state.player_game_states[0].rails, self.INITIAL_RAIL_COUNT - connection_to_acquire.length)
        self.assertIn(connection_to_acquire,
                      self.ref.ref_game_state.player_game_states[0].connections)

    def test_apply_acquire_connection_move_cheating(self):
        zero_colored_cards = {Color.RED: 0, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0} 
        pgs = self.ref.ref_game_state.player_game_states[0]
        self.ref.ref_game_state.player_game_states[0] = PlayerGameState(pgs.connections, zero_colored_cards, \
            pgs.rails, pgs.destinations, pgs.other_acquisitions)
        self.assertEqual(len(self.ref.ban_list), 0)

        self.assertRaises(Cheating, AcquireConnectionMove(self.connection1).accepts, ApplyPlayerMove(
            self.ref.ref_game_state, self.ref.get_active_player()))

    def test_execute_player_move_acquire_connection(self):
        SET_BLUE_CARDS = 20
        colored_cards = {Color.RED: 0, Color.BLUE: SET_BLUE_CARDS, Color.GREEN: 0, Color.WHITE: 0}
        pgs = self.ref.ref_game_state.player_game_states[0]
        self.ref.ref_game_state.player_game_states[0] = PlayerGameState(pgs.connections, colored_cards, \
            pgs.rails, pgs.destinations, pgs.other_acquisitions)
        # Should acquire connection 10 due to lexicographical ordering
        connection_to_acquire = self.connection10

        self.ref.execute_active_player_move()

        self.assertIn(connection_to_acquire,
                      self.ref.ref_game_state.player_game_states[0].connections)
        self.assertEqual(
            self.ref.ref_game_state.player_game_states[0].colored_cards[Color.BLUE], SET_BLUE_CARDS - connection_to_acquire.length)
        self.assertEqual(
            self.ref.ref_game_state.player_game_states[0].rails, self.INITIAL_RAIL_COUNT - connection_to_acquire.length)

    def test_execute_player_move_draw_cards(self):
        deck = deque([Color.RED, Color.WHITE, Color.GREEN, Color.BLUE] * 5)
        ref = Referee(self.game_map, self.players, deck)
        pgs_before = ref.ref_game_state.player_game_states[0]
        self.assertEqual(
            pgs_before.get_total_cards(), self.INITIAL_HAND_SIZE)
        # The player in index 0 is a Hold 10 player, so they will draw cards in this situation
        ref.execute_active_player_move()
        pgs = ref.ref_game_state.player_game_states[0]
        self.assertEqual(
            pgs.connections, set())
        self.assertEqual(
            pgs.get_total_cards(), self.INITIAL_HAND_SIZE + self.DRAW_NUM)
        exp_colored_cards = {Color.RED: 1, Color.WHITE: 1, Color.GREEN: 2, Color.BLUE: 2}
        self.assertEqual(pgs.colored_cards, exp_colored_cards)
        self.assertEqual(
            pgs.rails, self.INITIAL_RAIL_COUNT)

    def test_execute_player_cheating(self):
        bad_move = AcquireConnectionMove(self.bad_connection)
        bad_player = MockConfigurablePlayer("cheater", bad_move)
        players = [bad_player, self.p1]
        ref = Referee(self.game_map, players)
        self.assertEqual(len(ref.ban_list), 0)
        ref.execute_active_player_move()
        self.assertIn(0, ref.ban_list)

    def test_generate_updated_state_for_player(self):
        # Create a deck of all red cards to give to the referee
        red_deck = deque([Color.RED] * 20)

        ref = Referee(self.game_map, self.players, red_deck)
        pgs = ref.ref_game_state.player_game_states[0]

        # Create non initial player game states to update
        p0_connections = {self.connection1}
        p0_dests = {Destination({self.boston, self.new_york}), Destination({self.philadelphia, self.new_york})}
        ref.ref_game_state.player_game_states[0] = PlayerGameState(p0_connections, \
            pgs.colored_cards, pgs.rails, p0_dests, [])
        
        p1_connections = {self.connection2, self.connection3}
        p1_dests = {Destination({self.austin, self.boston}), Destination({self.boise, self.boston})}
        ref.ref_game_state.player_game_states[1] = PlayerGameState(p1_connections, \
            pgs.colored_cards, pgs.rails, p1_dests, [])

        p2_connections = set()
        p2_dests = {Destination({self.boston, self.los_angeles}), Destination({self.philadelphia, self.los_angeles})}
        ref.ref_game_state.player_game_states[2] = PlayerGameState(p2_connections, \
            pgs.colored_cards, pgs.rails, p2_dests, [])

        # The deck is all red cards
        exp_hand = {Color.RED: 4, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        exp_rails = self.INITIAL_RAIL_COUNT

        pgs0 = ref.generate_updated_state_for_player(0)
        exp_pgs0 = PlayerGameState(p0_connections, exp_hand, exp_rails, p0_dests, [p1_connections, p2_connections])
        self.assertEqual(pgs0, exp_pgs0)

        pgs1 = ref.generate_updated_state_for_player(1)
        exp_pgs1 = PlayerGameState(p1_connections, exp_hand, exp_rails, p1_dests, [p2_connections, p0_connections])
        self.assertEqual(pgs1, exp_pgs1)

        pgs2 = ref.generate_updated_state_for_player(2)
        exp_pgs2 = PlayerGameState(p2_connections, exp_hand, exp_rails, p2_dests, [p0_connections, p1_connections])
        self.assertEqual(pgs2, exp_pgs2)

    def test_update_specific_player_state(self):
        # Create a deck of all red cards to give to the referee
        red_deck = deque([Color.RED] * 20)

        ref = Referee(self.game_map, self.players, red_deck)
        pgs = ref.ref_game_state.player_game_states[0]

        p0_connections = {self.connection1}
        p0_dests = {Destination({self.boston, self.new_york}), Destination({self.philadelphia, self.new_york})}
        ref.ref_game_state.player_game_states[0] = PlayerGameState(p0_connections, \
            pgs.colored_cards, pgs.rails, p0_dests, [])

        # If another player gets a connection, the other_acquired field should update
        p1_connections = {self.connection2}
        p1_dests = {Destination({self.austin, self.boston}), Destination({self.boise, self.boston})}
        ref.ref_game_state.player_game_states[1] = PlayerGameState(p1_connections, \
            pgs.colored_cards, pgs.rails, p1_dests, [])

        ref.update_specific_player_state(0)
        pgs = ref.ref_game_state.player_game_states[0]
        exp_pgs = PlayerGameState(p0_connections, pgs.colored_cards, pgs.rails, p0_dests, [{self.connection2}, set()])
        self.assertEqual(pgs, exp_pgs)

    def test_update_player_states(self):
        # Create a deck of all red cards to give to the referee
        red_deck = deque([Color.RED] * 20)

        ref = Referee(self.game_map, self.players, red_deck)
        pgs = ref.ref_game_state.player_game_states[0]

        p0_connections = {self.connection1}
        p0_dests = {Destination({self.boston, self.new_york}), Destination({self.philadelphia, self.new_york})}
        ref.ref_game_state.player_game_states[0] = PlayerGameState(p0_connections, \
            pgs.colored_cards, pgs.rails, p0_dests, [])
        
        p1_connections = {self.connection2, self.connection3}
        p1_dests = {Destination({self.austin, self.boston}), Destination({self.boise, self.boston})}
        ref.ref_game_state.player_game_states[1] = PlayerGameState(p1_connections, \
            pgs.colored_cards, pgs.rails, p1_dests, [])

        p2_connections = set()
        p2_dests = {Destination({self.boston, self.los_angeles}), Destination({self.philadelphia, self.los_angeles})}
        ref.ref_game_state.player_game_states[2] = PlayerGameState(p2_connections, \
            pgs.colored_cards, pgs.rails, p2_dests, [])

        ref.update_player_states()

        # The deck is all red cards
        exp_hand = {Color.RED: 4, Color.BLUE: 0, Color.GREEN: 0, Color.WHITE: 0}
        exp_rails = self.INITIAL_RAIL_COUNT

        pgs0 = ref.ref_game_state.player_game_states[0]
        exp_pgs0 = PlayerGameState(p0_connections, exp_hand, exp_rails, p0_dests, [p1_connections, p2_connections])
        self.assertEqual(pgs0, exp_pgs0)

        pgs1 = ref.ref_game_state.player_game_states[1]
        exp_pgs1 = PlayerGameState(p1_connections, exp_hand, exp_rails, p1_dests, [p2_connections, p0_connections])
        self.assertEqual(pgs1, exp_pgs1)

        pgs2 = ref.ref_game_state.player_game_states[2]
        exp_pgs2 = PlayerGameState(p2_connections, exp_hand, exp_rails, p2_dests, [p0_connections, p1_connections])
        self.assertEqual(pgs2, exp_pgs2)

    def test_all_last_turns_taken_false(self):
        self.assertFalse(self.ref.all_last_turns_taken())

    def test_all_last_turns_taken_true(self):
        self.ref.took_last_turn = self.players
        self.assertTrue(self.ref.all_last_turns_taken())

    def test_get_connection_score(self):
        ref = Referee(self.game_map, self.players)
        pgs = ref.ref_game_state.player_game_states[0]
        # Give player connections to be scored
        ref.ref_game_state.player_game_states[0] = PlayerGameState({self.connection1, self.connection2}, pgs.colored_cards, pgs.rails, pgs.destinations, pgs.other_acquisitions)
        score = ref.get_connection_score(
            ref.ref_game_state.player_game_states[0], self.RAIL_SEGMENT_POINT_VALUE)
        exp_score = self.connection1.length + self.connection2.length
        self.assertEqual(score, exp_score)

    def test_get_connection_score_zero(self):
        score = self.ref.get_connection_score(
            self.ref.ref_game_state.player_game_states[0], self.RAIL_SEGMENT_POINT_VALUE)
        exp_score = 0
        self.assertEqual(score, exp_score)

    def test_get_destination_score_completed_two(self):
        dest1 = Destination({self.boston, self.new_york})
        dest2 = Destination({self.philadelphia, self.new_york})
        destinations = {dest1, dest2}
        pgs = self.ref.ref_game_state.player_game_states[0]
        self.ref.ref_game_state.player_game_states[0] = PlayerGameState({self.connection1, self.connection5}, \
            pgs.colored_cards, pgs.rails, destinations, pgs.other_acquisitions)
        score = self.ref.get_destination_score(
            self.ref.ref_game_state.player_game_states[0], self.DESTINATION_COMPLETE_VALUE)
        exp_score = self.DESTINATION_COMPLETE_VALUE + self.DESTINATION_COMPLETE_VALUE
        self.assertEqual(score, exp_score)

    def test_get_destination_score_completed_one(self):
        dest1 = Destination({self.boston, self.new_york})
        dest2 = Destination({self.philadelphia, self.new_york})
        destinations = {dest1, dest2}
        pgs = self.ref.ref_game_state.player_game_states[0]
        self.ref.ref_game_state.player_game_states[0] = PlayerGameState({self.connection1}, \
            pgs.colored_cards, pgs.rails, destinations, pgs.other_acquisitions)
        score = self.ref.get_destination_score(
            self.ref.ref_game_state.player_game_states[0], self.DESTINATION_COMPLETE_VALUE)
        exp_score = self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        self.assertEqual(score, exp_score)

    def test_get_destination_score_completed_zero(self):
        score = self.ref.get_destination_score(
            self.ref.ref_game_state.player_game_states[0], self.DESTINATION_COMPLETE_VALUE)
        exp_score = -self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        self.assertEqual(score, exp_score)

    def test_score_game(self):
        dest1 = Destination({self.boston, self.new_york})
        dest2 = Destination({self.austin, self.boston})
        destinations = {dest1, dest2}
        pgs = self.ref.ref_game_state.player_game_states[0]
        # Give this player a connection and a destination for that connection to given them the points for completing that destination
        self.ref.ref_game_state.player_game_states[0] = PlayerGameState({self.connection1}, pgs.colored_cards, pgs.rails, destinations, pgs.other_acquisitions)
        scores = self.ref.score_game()
        # Player in index 0 has longest path, because they are the only player with a connection
        exp_score1 = self.connection1.length + self.LONGEST_CONTINUOUS_PATH_VALUE + \
            self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        exp_score2 = -self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        exp_score3 = -self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        exp_scores = {self.p1: exp_score1,
                      self.p2: exp_score2, self.p3: exp_score3}
        self.assertEqual(scores, exp_scores)

    def test_score_game_banned_player(self):
        dest1 = Destination({self.boston, self.new_york})
        dest2 = Destination({self.austin, self.boston})
        destinations = {dest1, dest2}
        pgs = self.ref.ref_game_state.player_game_states[0]
        # Give this player a connection and a destination for that connection to given them the points for completing that destination
        self.ref.ref_game_state.player_game_states[0] = PlayerGameState({self.connection1}, pgs.colored_cards, pgs.rails, destinations, pgs.other_acquisitions)
        # Boot the cheater so they shouldn't show up in the outputted scores
        self.ref.boot_player(1, "cheating")
        scores = self.ref.score_game()
        exp_score_p1 = self.connection1.length + self.LONGEST_CONTINUOUS_PATH_VALUE + \
            self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        # p2 is banned, so they are not scored
        exp_score_p3 = -self.DESTINATION_COMPLETE_VALUE - self.DESTINATION_COMPLETE_VALUE
        exp_scores = {self.p1: exp_score_p1, self.p3: exp_score_p3}
        self.assertEqual(scores, exp_scores)

    def test_longest_path(self):
        pgs = self.ref.ref_game_state.player_game_states[0]
        self.ref.ref_game_state.player_game_states[0] = PlayerGameState({self.connection1, self.connection5}, \
            pgs.colored_cards, pgs.rails, pgs.destinations, pgs.other_acquisitions)
        self.assertEqual(
            self.ref.find_longest_continuous_path_for_player(0), 7)

    def test_longest_path_complex(self):
        player_connections = {self.connection1, self.connection2, self.connection3, \
            self.connection4, self.connection5, self.connection6, self.connection7, self.connection8, \
                self.connection9, self.connection10, self.connection11, self.connection12}
        pgs = self.ref.ref_game_state.player_game_states[0]
        self.ref.ref_game_state.player_game_states[0] = PlayerGameState(player_connections, pgs.colored_cards, \
            pgs.rails, pgs.destinations, pgs.other_acquisitions)
        self.assertEqual(
            self.ref.find_longest_continuous_path_for_player(0), 12)

    def test_longest_path_disjoint(self):
        pgs = self.ref.ref_game_state.player_game_states[0]
        # Give this player game state two connections that are not connected to each other
        # connection1 has a length of 3 and connection12 has a length of 5, so the output should be 5
        self.ref.ref_game_state.player_game_states[0] = PlayerGameState({self.connection1, self.connection12}, \
            pgs.colored_cards, pgs.rails, pgs.destinations, pgs.other_acquisitions)
        self.assertEqual(
            self.ref.find_longest_continuous_path_for_player(0), 5)

    def test_longest_path_no_connections(self):
        self.assertEqual(
            self.ref.find_longest_continuous_path_for_player(0), 0)

    def test_get_active_player_first_turn(self):
        self.assertEqual(self.players[0], self.ref.get_active_player())

    def test_get_active_player_next_turn(self):
        self.ref.ref_game_state.next_turn()
        self.assertEqual(self.players[1], self.ref.get_active_player())

    def test_get_active_player_wrap_around(self):
        self.assertEqual(self.players[0], self.ref.get_active_player())

    def test_notify_players(self):
        move = AcquireConnectionMove(self.connection1)
        winning_player = MockConfigurablePlayer("winner", move)
        losing_player = MockConfigurablePlayer("loser", move)
        players: List[PlayerInterface] = [winning_player, losing_player]
        ref = Referee(self.game_map, players)
        ref.notify_players([winning_player])
        self.assertTrue(winning_player._is_winner)
        self.assertFalse(losing_player._is_winner)

    def test_notify_players_tie(self):
        move = AcquireConnectionMove(self.connection1)
        tie_player1 = MockConfigurablePlayer("tie1", move)
        tie_player2 = MockConfigurablePlayer("tie2", move)
        losing_player = MockConfigurablePlayer("loser", move)
        players: List[PlayerInterface] = [
            tie_player1, tie_player2, losing_player]
        ref = Referee(self.game_map, players)
        ref.notify_players([tie_player1, tie_player2])
        self.assertTrue(tie_player1._is_winner)
        self.assertTrue(tie_player2._is_winner)
        self.assertFalse(losing_player._is_winner)

    def test_get_banned_players(self):
        self.ref.get_banned_players()
        self.assertEqual(len(self.ref.get_banned_players()), 0)

        self.ref.boot_player(1, "Testing player2 getting booted.")
        self.assertEqual(len(self.ref.get_banned_players()), 1)
        self.assertEqual(self.ref.get_banned_players()[0], self.p2)

        self.ref.boot_player(0, "Testing player1 getting booted.")
        self.assertEqual(len(self.ref.get_banned_players()), 2)
        self.assertEqual(self.ref.get_banned_players()[0], self.p1)
        self.assertEqual(self.ref.get_banned_players()[1], self.p2)

    def test_get_ranking_of_players(self):
        move = AcquireConnectionMove(self.connection1)
        tie_player1 = MockConfigurablePlayer("tie1", move)
        tie_player2 = MockConfigurablePlayer("tie2", move)
        losing_player = MockConfigurablePlayer("loser", move)
        players: List[PlayerInterface] = [
            tie_player1, tie_player2, losing_player]
        ref = Referee(self.game_map, players)
        scores: Dict[PlayerInterface, int] = {
            tie_player1: 10, tie_player2: 10, losing_player: 0}
        rankings = ref.get_ranking_of_players(scores)
        exp_rankings = [[tie_player1, tie_player2], [losing_player]]
        self.assertEqual(rankings, exp_rankings)

    def test_get_ranking_of_players_banned_player(self):
        move = AcquireConnectionMove(self.connection1)
        tie_player1 = MockConfigurablePlayer("tie1", move)
        tie_player2 = MockConfigurablePlayer("tie2", move)
        losing_player = MockConfigurablePlayer("loser", move)
        banned_player = MockConfigurablePlayer("cheater", move)
        players: List[PlayerInterface] = [tie_player1,
                                          tie_player2, losing_player, banned_player]
        ref = Referee(self.game_map, players)
        scores: Dict[PlayerInterface, int] = {
            tie_player1: 10, tie_player2: 10, losing_player: 0}
        rankings = ref.get_ranking_of_players(scores)
        exp_rankings = [[tie_player1, tie_player2], [losing_player]]
        self.assertEqual(rankings, exp_rankings)
        

class RefereeIntegrationTests(unittest.TestCase):

    def setUp(self):
        # Create map
        self.boston = City("Boston", 70, 80)
        self.new_york = City("New York", 60, 70)
        self.philadelphia = City("Philadelphia", 90, 10)
        self.wdc = City("Washington D.C.", 55, 60)
        self.boise = City("Boise", 30, 50)
        self.connection1 = Connection(
            frozenset({self.boston, self.new_york}), Color.BLUE, 3)
        self.connection2 = Connection(
            frozenset({self.philadelphia, self.new_york}), Color.RED, 4)
        self.connection3 = Connection(
            frozenset({self.boston, self.wdc}), Color.BLUE, 5)
        self.connection4 = Connection(
            frozenset({self.philadelphia, self.wdc}), Color.WHITE, 5)
        self.connection5 = Connection(
            frozenset({self.boise, self.wdc}), Color.GREEN, 5)
        self.bad_connection = Connection(frozenset({City("this does not exist", 10, 10), City(
            "this does not exist either", 11, 11)}), Color.GREEN, 3)

        self.cities = {self.boston, self.new_york,
                       self.philadelphia, self.wdc, self.boise}
        self.connections = {self.connection1, self.connection2,
                            self.connection3, self.connection4, self.connection5}
        self.height = 800
        self.width = 800
        self.game_map = Map(self.cities, self.connections,
                            self.height, self.width)

        # Create mock players that always draw cards - this means they will tie
        # The buy now player will always win if they are in the game because the
        # draw_playerX players are mock players that only draw (never acquire connections)
        draw = DrawCardMove()
        self.draw_player1 = MockConfigurablePlayer("player1", draw)
        self.draw_player2 = MockConfigurablePlayer("player2", draw)
        self.bn_player = MockBuyNowPlayer("buyer")
        self.bad_player = MockConfigurablePlayer(
            "cheater", AcquireConnectionMove(self.bad_connection))

        # The deck has 12 red cards
        self.red_deck = deque([Color.RED] * 12)

    def test_play_game_all_players_banned_on_setup(self):
        num_players = 2
        players: List[PlayerInterface] = []
        for pi in range(num_players):
            players.insert(0, MockBadSetUpPlayer(f"player{pi}"))
        ref = Referee(self.game_map, players, self.red_deck)
        rankings, banned_players = ref.play_game()
        self.assertEqual(rankings, [])
        exp_banned = players
        # Sort the lists by name to check that they are equal
        exp_banned.sort(key=lambda p: p.get_name())
        banned_players.sort(key=lambda p: p.get_name())
        self.assertEqual(banned_players, exp_banned)

    def test_play_game_all_players_banned_on_pick(self):
        num_players = 3
        players: List[PlayerInterface] = []
        for pi in range(num_players):
            players.append(MockBadPickPlayer(f"player{pi}"))
        ref = Referee(self.game_map, players, self.red_deck)
        rankings, banned_players = ref.play_game()
        self.assertEqual(rankings, [])
        exp_banned = players
        # Sort the lists by name to check that they are equal
        exp_banned.sort(key=lambda p: p.get_name())
        banned_players.sort(key=lambda p: p.get_name())
        self.assertEqual(banned_players, exp_banned)

    def test_play_game_tie(self):
        players: List[PlayerInterface] = [self.draw_player1, self.draw_player2]
        ref = Referee(self.game_map, players, self.red_deck)
        rankings, banned_list = ref.play_game()
        exp_rankings = [[self.draw_player1, self.draw_player2]]
        self.assertEqual(rankings, exp_rankings)
        self.assertEqual(banned_list, [])

    def test_play_game_no_tie(self):
        players = [self.bn_player, self.draw_player1]
        ref = Referee(self.game_map, players, self.red_deck)
        rankings, banned_list = ref.play_game()
        exp_rankings = [[self.bn_player], [self.draw_player1]]
        self.assertEqual(rankings, exp_rankings)
        self.assertEqual(banned_list, [])

    def test_play_game_with_cheater(self):
        players = [self.bn_player, self.bad_player]
        ref = Referee(self.game_map, players, self.red_deck)
        rankings, banned_list = ref.play_game()

        exp_rankings = [[self.bn_player]]
        exp_banned = [self.bad_player]
        self.assertEqual(rankings, exp_rankings)
        self.assertIn(self.bad_player, ref.get_banned_players())
        self.assertEqual(banned_list, exp_banned)

    def test_play_game_no_tie_with_cheater(self):
        players = [self.bn_player, self.draw_player1, self.bad_player]
        ref = Referee(self.game_map, players, self.red_deck)
        rankings, banned_list = ref.play_game()

        exp_rankings = [[self.bn_player], [self.draw_player1]]
        exp_banned = [self.bad_player]
        self.assertEqual(rankings, exp_rankings)
        self.assertIn(self.bad_player, ref.get_banned_players())
        self.assertEqual(banned_list, exp_banned)

    def test_play_game_all_players_booted_during_play(self):
        num_players = 3
        players: List[PlayerInterface] = []
        for pi in range(num_players):
            players.insert(0, MockConfigurablePlayer(f"cheater{pi}", \
                AcquireConnectionMove(self.bad_connection)))
        ref = Referee(self.game_map, players, self.red_deck)
        rankings, banned_players = ref.play_game()
        self.assertEqual(rankings, [])
        exp_banned = players
        # Sort the lists by name to check that they are equal
        exp_banned.sort(key=lambda p: p.get_name())
        banned_players.sort(key=lambda p: p.get_name())
        self.assertEqual(banned_players, exp_banned)
        
if __name__ == '__main__':
    unittest.main()

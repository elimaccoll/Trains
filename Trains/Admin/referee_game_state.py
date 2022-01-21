import sys
from collections import deque
from typing import Deque, List, Set

sys.path.append('../../')
from Trains.Common.map import Color, Connection, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Other.Util.constants import MIN_RAILS_TO_NOT_TRIGGER_LAST_TURN
from Trains.Other.Util.func_utils import flatten_set


class RefereeGameState:
    """
    Represents a referee game state that keeps track of player game states (PlayerGameState) and
    which player's turn it is. Also handles the verification of players acquiring connections, and
    determines what connections are available to the currently active player.
    """
    player_game_states: List[PlayerGameState]

    def __init__(self, game_map: Map, colored_card_deck: Deque[Color], player_game_states: List[PlayerGameState]) -> None:
        """
        Constructor for RefereeGameState that verifies given fields and initializes class fields to setup a game.
            Parameters:
                map (Map): The game map
                colored_card_deck (deque): A deque of colored cards representing the deck of colored cards
                player_game_states (list): A list of PlayerGameState provided by the referee (in sorted order)
            Throws:
                TypeError:
                    - The given map must be of type Map
                    - The deck of colored cards must be a deque
                    - The player game states must be a list and each one a PlayerGameState
        """
        if type(game_map) != Map:
            raise TypeError("The given map must be a Map")
        if type(colored_card_deck) != deque:
            raise TypeError("The colored card deck must be a deque")
        for card in colored_card_deck:
            if type(card) != Color:
                raise TypeError("Colored card deck must only contain Colors")
        if type(player_game_states) != list:
            raise TypeError("The given player game states must be a list.")
        for entry in player_game_states:
            if type(entry) != PlayerGameState:
                raise TypeError(
                    "Entry in list of player game states must be a PlayerGameState.")

        self.game_map = game_map
        self.player_game_states = player_game_states
        self.turn = 0

        self.free_connections = self.get_all_unacquired_connections()
        self.colored_card_deck = colored_card_deck.copy()

    def __eq__(self, other) -> bool:
        return type(other) == RefereeGameState and self.game_map == other.game_map and \
            list(self.colored_card_deck) == list(other.colored_card_deck) and \
            self.player_game_states == other.player_game_states

    def get_current_active_player_index(self) -> int:
        """
        Returns the currently active player
        INTENDED CALLER: Referee
        """
        return self.turn

    def next_turn(self) -> None:
        """
        Increments the turn counter and updates the set of unacquired connections.
        """
        self.turn = (self.turn + 1) % len(self.player_game_states)
        self.free_connections = self.get_all_unacquired_connections()

    def get_player_game_state(self) -> PlayerGameState:
        """
        Gets the player game state (PlayerGameState) of the currently active player.
            Returns:
                The PlayerGameState of the currently active player.
        """
        return self.player_game_states[self.get_current_active_player_index()]

    def get_all_player_connections(self) -> Set[Connection]:
        """
        Gets all acquired connections.
            Returns:
                A set of connections that have been acquired by any player.
        """
        return flatten_set(pgs.connections for pgs in self.player_game_states)

    def verify_legal_connection_for_player(self, connection: Connection, player_game_state: PlayerGameState) -> bool:
        """
        Verifies if a given connection can be legally acquired by a given player
        according the Trains game rules.
            Parameters:
                connection (Connection): Connection that is being acquired
                player_game_state (PlayerGameState): The player game state of the player
                                                     acquiring the connection
            Returns:
                True if the player can acquire the connection,
                False otherwise:
                - The connection is already acquired
                - The player does not have enough rails
                - The player does not have enough of the corresponding colored cards
        """
        player_rails = player_game_state.rails
        player_cards = player_game_state.colored_cards
        conn_color = connection.color
        conn_length = connection.length

        is_free_connection = connection in self.free_connections
        has_enough_rails = player_rails >= conn_length
        has_enough_colored_cards = player_cards[conn_color] >= conn_length

        return is_free_connection and has_enough_rails and has_enough_colored_cards

    def verify_legal_connection(self, connection: Connection) -> bool:
        """
        Verifies if a given connection can be legally acquired by the currently active player
        according the Trains game rules.
            Parameters:
                connection (Connection): Connection that is being acquired
            Returns:
                True if the currently active player can acquire the connection,
                False otherwise:
                - The connection is already acquired
                - The player does not have enough rails
                - The player does not have enough of the corresponding colored cards
        """
        player_resources = self.player_game_states[self.turn]
        return self.verify_legal_connection_for_player(connection, player_resources)

    def get_all_acquirable_connections(self, player_game_state: PlayerGameState) -> Set[Connection]:
        """
        Determines all connections that can be acquired by a given player.
            Parameters:
                player_game_state (PlayerGameState): The player to determines acquireable connections for
            Returns:
                Set of acquireable connections
        """
        acquirable_connections = set()
        for connection in self.free_connections:
            if self.verify_legal_connection_for_player(connection, player_game_state):
                acquirable_connections.add(connection)
        return acquirable_connections

    def get_all_unacquired_connections(self) -> Set[Connection]:
        """
        Determines all connections that have not been acquired by a player.
            Returns:
                Set of unacquired connections
        """
        all_connections = self.game_map.get_all_connections()
        unacquired_connections = all_connections - self.get_all_player_connections()
        return unacquired_connections

    def get_cards_from_deck(self, number_of_cards) -> List[Color]:
        """
        Gets the specified number of cards from the deck,
        or as many as possible ([] if none).
        """
        cards: List[Color] = []
        for _ in range(number_of_cards):
            if len(self.colored_card_deck) > 0:
                cards.append(self.colored_card_deck.pop())
        return cards

    def is_last_turn(self) -> bool:
        """
        Determines if any player has less than 3 rails and a game
        is entering its last round.
            Returns:
                True if end_game detected, else False
        """
        return any(pgs.rails < MIN_RAILS_TO_NOT_TRIGGER_LAST_TURN for pgs in self.player_game_states)

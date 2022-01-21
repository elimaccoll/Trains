import sys
from collections import defaultdict, deque
from random import randint
from typing import (Any, Callable, DefaultDict, Deque, Dict, List, Optional,
                    Set, Tuple, TypeVar, Union)

import networkx as nx

sys.path.append('../../')
from Trains.Admin.referee_game_state import RefereeGameState
from Trains.Common.map import Color, Connection, Destination, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Other.Util.constants import (MIN_RAILS_TO_NOT_TRIGGER_LAST_TURN,
                                         int2color)
from Trains.Other.Util.func_utils import try_call
from Trains.Other.Util.map_utils import verify_game_map
from Trains.Player.moves import (AcquireConnectionMove, DrawCardMove,
                                 IPlayerMoveVisitor)
from Trains.Player.player_interface import PlayerInterface

T = TypeVar("T")


class Cheating(Exception):
    """
    An error class that represents cheating by the player.
    This can be used to distinguish between runtime errors/exceptions
    caused by player implementation and detection of cheating.
    """
    pass


class NotEnoughDestinations(ValueError):
    """
    An error class that represents when there are not enough destinations
    in a given map for the number of players in the game.
    """
    pass


class IsPlayerMoveLegal(IPlayerMoveVisitor[bool]):
    """A IPlayerMove visitor for checking if a PlayerMove is legal to apply to the current RefereeGameState.
    Virtual functions return a boolean indicating whether it is legal."""

    _rgs: RefereeGameState

    def __init__(self, rgs: RefereeGameState) -> None:
        super().__init__()
        self._rgs = rgs

    def visitDrawCards(self, _: DrawCardMove) -> bool:
        """Determines whether the player is allowed to request cards. To ensure
        proper progression of the game, this should always be allowed."""
        return True

    def visitAcquireConnection(self, move: AcquireConnectionMove) -> bool:
        """Determines if the active player can claim the connection associated with
        this action based on the corresponding RefereeGameState."""
        is_legal_acquisition = self._rgs.verify_legal_connection(
            move.connection)

        return is_legal_acquisition


class ApplyPlayerMove(IPlayerMoveVisitor[bool]):
    """A IPlayerMove visitor for applying PlayerMoves to the RefereeGameState.
    Virtual functions return a boolean indicating whether the state has changed.

    Note: this visitor performs mutation on the RefereeGameState it is initialized with.
    This visitor may also throw an error if an operation fails. It should only be called from a safe context."""
    CARDS_ON_DRAW = 2

    _rgs: RefereeGameState
    _player: PlayerInterface

    def __init__(self, rgs: RefereeGameState, player: PlayerInterface) -> None:
        super().__init__()
        self._rgs = rgs
        self._player = player

    def visitDrawCards(self, move: DrawCardMove) -> bool:
        # print(f"{self._player.get_name()} requested cards\n")  # DEBUG

        if not move.accepts(IsPlayerMoveLegal(self._rgs)):
            raise Cheating("Active player is unable to draw cards.")

        new_cards = self._rgs.get_cards_from_deck(
            ApplyPlayerMove.CARDS_ON_DRAW)

        pgs = self._rgs.player_game_states[self._rgs.turn]
        player_hand = pgs.colored_cards

        for card in new_cards:
            if card in player_hand.keys():
                player_hand[card] += 1
            else:
                player_hand[card] = 1
        self._rgs.player_game_states[self._rgs.turn] = PlayerGameState(
            pgs.connections, player_hand, pgs.rails, pgs.destinations, pgs.other_acquisitions)

        self._player.more(new_cards)  # may throw an error
        return len(new_cards) > 0

    def visitAcquireConnection(self, move: AcquireConnectionMove) -> bool:
        # print(
        #     f"{self._player.get_name()} is trying to acquire a connection: {repr(move.connection)}\n")  # DEBUG

        if not move.accepts(IsPlayerMoveLegal(self._rgs)):
            raise Cheating(
                "Active player is unable to acquire the given connection.")

        connection = move.connection
        pgs = self._rgs.player_game_states[self._rgs.turn]

        updated_connections = pgs.connections.union([connection])
        updated_rails = pgs.rails - connection.length

        updated_colored_cards = pgs.colored_cards
        updated_colored_cards[connection.color] -= connection.length

        updated_pgs = PlayerGameState(updated_connections, updated_colored_cards, updated_rails,
                                      pgs.destinations, pgs.other_acquisitions)

        self._rgs.player_game_states[self._rgs.turn] = updated_pgs
        return True


class Referee():
    """
    Represents a referee that setups, facilitates, and ends a game of Trains.
    Should call play_game() right after __init__() to begin game and assume
    game has ended after play_game() returns. No other methods should be called
    The referee should catch Cheating in the form of:
        - Data tampering during initialization
        - Illegal moves from players
        - Errors raised from player code
        - Exceptions raised from player code
        - Type mismatch returned from player code
    and boots them from the game.
    The following will be handled after networking is implemented:
        - Unresponsive players (timeouts)
        - Incorrectly formatted/invalid input (likely json)
    """

    ban_list: Set[int]
    players: List[PlayerInterface]
    game_map: Map
    took_last_turn: Set[PlayerInterface]
    ref_game_state: RefereeGameState
    num_of_same_states: int

    def __init__(self, game_map: Map, players: List[PlayerInterface], deck: Optional[Deque[Color]] = None) -> None:
        """
        Constructor for the Referee that initializes fields for the setup of a game of Trains.
            Parameters:
                game_map (Map): The game map
                players (list(PlayerInterface)): The list of players in descending order of player age
            Throws:
                ValueError:
                    - The game map must be a Map
                    - The players list must be a list of 2 to 8 players
        """
        if type(game_map) != Map:
            raise TypeError("Referee must be given a valid map")
        if type(players) != list:
            raise TypeError("Referee must get a list of players")
        if len(players) < 2 or len(players) > 8:
            raise ValueError("Referee must get a list of [2, 8] players")
        if deck is not None:
            if type(deck) != deque:
                raise TypeError("The colored card deck must be a deque")
            for card in deck:
                if type(card) != Color:
                    raise TypeError(
                        "Colored card deck must only contain Colors")

        # Constants for the setup of a game of Trains
        self.INITIAL_RAIL_COUNT = 45
        self.CARDS_ON_DRAW = 2
        self.INITIAL_DECK_SIZE = 250
        self.INITIAL_HAND_SIZE = 4
        self.NUM_DESTINATIONS = 2
        self.NUM_DESTINATION_OPTIONS = 5
        # Used to keep track of players eliminated for cheating
        self.ban_list = set()
        # Used on the last turn of the game to keep track of which players took their last turn
        self.took_last_turn = set()

        self.num_of_same_states = 0

        self.players = players

        # Make sure given map has enough destinations for the players.
        if verify_game_map(game_map, len(self.players), self.NUM_DESTINATION_OPTIONS, self.NUM_DESTINATIONS):
            self.game_map = game_map
        else:
            raise NotEnoughDestinations(f"Not enough destinations to give each \
                player {self.NUM_DESTINATION_OPTIONS} to choose from")

        # If the deck is not given, then create one
        if deck is None:
            deck = self.initialize_deck(self.INITIAL_DECK_SIZE)
        else:
            deck = deck.copy()
            self.INITIAL_DECK_SIZE = len(deck)

        formatted_player_states = self.set_up_players_with_initial_game_states(players, deck, self.INITIAL_RAIL_COUNT,
                                                                               game_map.get_all_feasible_destinations())

        self.ref_game_state = RefereeGameState(
            game_map, deck, formatted_player_states)

    def set_up_players_with_initial_game_states(self, players: List[PlayerInterface], deck: Deque[Color], \
        rails: int, feasible_destinations: Set[Destination]) -> List[PlayerGameState]:
        """
        Creates player game states (PlayerGameState) for each player in a given list of players
        according to the game map and game rule constants (initial rail count, initial hand
        size, and initial number of destinations)
            Parameters:
                players (list(PlayerInterface)): list of players to create player game states for
                deck (deque): Initial deck of colored cards
                rails (int): Initial rails given to each player
                feasible_destinations (set(Destination)): Feasible destinations on the map to be selected by players
            Returns:
                (list(PlayerGameState)): List of player game states in the turn order
                player game states in the format required to initialize a referee game state
        """
        formatted_player_states: List[PlayerGameState] = list()

        feasible_destinations_copy = {*feasible_destinations}
        for player_index, player in enumerate(players):

            # Give each player their initial hand of colored cards
            initial_hand_for_player = self.create_initial_player_hand(
                deck, self.INITIAL_HAND_SIZE)

            _, err = try_call(player.setup, self.game_map,
                              rails, {**initial_hand_for_player})
            if err is not None:
                self.ban_player(
                    player_index, "Encountered player error during setup.")
                destinations_chosen = set()
            else:
                # If setup was successful, have player pick destinations.
                destinations_chosen = self.get_player_destination_choices(
                    player_index, feasible_destinations_copy)

                # Remove the destinations that this player chose from the set of feasible destinations offered to players
                feasible_destinations_copy -= destinations_chosen

            # Create player state and append to list
            player_state = self.generate_initial_player_state(
                initial_hand_for_player, rails, destinations_chosen, len(players))
            formatted_player_states.append(player_state)

        return formatted_player_states

    def get_player_destination_choices(self, player_index: int, feasible_destinations: Set[Destination]) -> Set[Destination]:
        """
        Given the index of a player and the set of a map's feasible destinations that have not been chosen,
        call the player's pick method, and returns the destinations they've chosen.
        """
        player = self.players[player_index]

        # Give each player their initial destinations
        inital_player_feasible_destinations = self.get_destination_selection(
            feasible_destinations, self.NUM_DESTINATION_OPTIONS)

        destinations_not_chosen, _ = try_call(
            player.pick, inital_player_feasible_destinations)

        if destinations_not_chosen is None:
            destinations_not_chosen = inital_player_feasible_destinations

        destinations_chosen = inital_player_feasible_destinations.difference(
            destinations_not_chosen)

        # Verify destinations chosen by the player
        if not self.verify_player_destinations(inital_player_feasible_destinations, destinations_chosen):
            # If the destinations picked are invalid in some way, the player is banned and their destinations are freed
            destinations_chosen = set()
            self.ban_player(
                player_index, "Referee did not get a valid set of destinations.")

        return destinations_chosen

    def generate_initial_player_state(self, initial_hand_for_player: Dict[Color, int], rails: int, destinations_chosen: Set[Destination], player_count: int) -> PlayerGameState:
        """
        Given a player's initial hand, number of rails, chosen destinations, and the size of the deck after handing all players
        their cards, generate and return a PlayerGameState with the player's initial information.
            Parameters:
                initial_hand_for_player (dict): Player's initial hand
                rails (int): Initial rails the player starts with
                destinations_chosen (set): Destinations the player chose while the game was being set up
                player_count (int): The total number of players
            Returns:
                A PlayerGameState with the Player's initial information about the game
        """
        other_acquisitions: List[Set[Connection]] = [set()] * player_count
        return PlayerGameState(set(), initial_hand_for_player, rails, destinations_chosen, other_acquisitions)

    def initialize_deck(self, number_of_cards: int) -> Deque[Color]:
        """
        Initializes the deck of colored cards for a game of Trains.
        Randomly generates 'number_of_cards' colored cards.
            Parameters:
                number_of_cards (int): The initial number of cards in the deck
            Returns:
                (deque) The deck of cards
        """
        deck: Deque[Color] = deque()
        for _ in range(number_of_cards):
            next_card = int2color[(randint(1, Color.number_of_colors()))]
            deck.append(next_card)

        return deck

    def create_initial_player_hand(self, deck: Deque[Color], initial_player_cards: int) -> Dict[Color, int]:
        """
        Creates the initial hand of colored cards for a player using cards from a given deck.
            Parameters:
                deck (deque): The deck of cards
                initial_player_cards (int): The initial number of cards in a player hand
            Returns:
                (dict) The player hand of colored cards as a dictionary keyed by strings
                of supported colors with integer values representing the amount of cards
        """
        hand: Dict[Color, int] = dict()
        for _ in range(initial_player_cards):
            next_card = deck.pop()
            if next_card in hand.keys():
                hand[next_card] += 1
            else:
                hand[next_card] = 1

        for i in range(1, Color.number_of_colors() + 1):
            if int2color[i] not in hand.keys():
                hand[int2color[i]] = 0

        return hand

    def get_destination_selection(self, feasible_destinations: Set[Destination], number_of_destinations: int) -> Set[Destination]:
        """
        Gets the subset of feasible destinations that a player will choose their destinations from on setup.  Randomly selects the Destinations.
            Parameters:
                feasible_destinations (set(Destination)): Set of all feasible destinations on a game map
                number_of_destinations (int): The number of destinations that a player can select from
            Returns:
                (set(Destination)) The set of destinations that a player will select from
        """
        destination_options: Set[Destination] = set()
        destination_list = list(feasible_destinations)
        for _ in range(number_of_destinations):
            random_destination = destination_list[randint(
                0, len(destination_list) - 1)]
            destination_options.add(random_destination)
            destination_list.remove(random_destination)

        return destination_options

    def verify_player_destinations(self, destinations_given: Set[Destination], destinations_chosen: Set[Destination]) -> bool:
        """
        Verifies that a player's chosen destinations agree with the game rules (number of destinations chosen) and
        the destinations options provided.
        ONLY CALLED AFTER A PLAYER IS INITIALIZED (Once per player)
            Parameters:
                destinations_given (set(Destination)): The destinations given to a player to select from
                destinations_chosen (set(Destination)): The destinations chosen by the player
            Returns:
                True is the destinations are valid, False otherwise
        """
        if len(destinations_chosen) != self.NUM_DESTINATIONS:
            return False
        for destination in destinations_chosen:
            if destination not in destinations_given:
                return False
        return True

    def ban_player(self, player_index: int, reason: str = "") -> None:
        """
        Bans the corresponding player for cheating. Banned players are no longer permitted to take turns.  This method is used explicity
        during the setup phase of the game before players take turns.  Mutates the ban list.
            Parameters:
                player_index (int): The index of the player being booted
                reason (str): The reason why they are being booted
        """
        # sys.stderr.write(
        #     f"{self.players[player_index].get_name()} was banned.\n") # DEBUG

        self.ban_list.add(player_index)

    def boot_player(self, player_index: int, reason: str = "") -> None:
        """
        Boots players that are caught cheating. Booted players are banned, meaning they no longer take turns. But their connections
        also become available again, and their resources (rails and colored cards) are discarded.
        This method mutates the ban_list set and RefereeGameState player_game_states list.
            Parameters:
                player_index (int): The index of the player being booted
                reason (str): The reason why they are being booted
        """
        # We need to set the booted_player_game_state to MIN_RAILS_TO_TRIGGER_LAST_TURN to avoid triggering the `is_last_turn` method
        # in RefereeGameState (since banned players are not removed from the data)
        booted_player_game_state = PlayerGameState(
            set(), dict(), MIN_RAILS_TO_NOT_TRIGGER_LAST_TURN, set(), [])
        self.ref_game_state.player_game_states[player_index] = booted_player_game_state
        self.ban_player(player_index, reason)

    def try_call_player(self, player_index: int, player_method: Callable[..., T], *args) -> Union[Tuple[T, None], Tuple[None, Exception]]:
        """
        Given a player method and arguments, return the result of calling that method.
        Single point of control for calling a player's methods.
            Parameters:
                player_index (int): The index of the player executing the method
                player_method (Callable): The player method to execute
                *args: The arguments for the given method
            Returns:
                The result of the given player method
        """
        result = try_call(player_method, *args)

        err = result[1]
        if err is not None:
            self.boot_player(
                player_index, "Game held up due to a logic error. Player booted.")

        return result

    def is_game_over(self) -> bool:
        """
        Determines if the game is over
        This implementation checks that game_state changes and all players
        have taken their last turn (after the rails of any player drop below 3)
        """
        players_remaining = len(self.players) - len(self.ban_list)
        return self.num_of_same_states == players_remaining or self.all_last_turns_taken() or players_remaining == 0

    def execute_active_player_move(self) -> None:
        """
        Executes the player active player's move.
            Throws:
                Cheating when an unsupported move (unknown MoveType) is given
        """
        # Get move
        active_player_index = self.ref_game_state.turn
        move, _ = self.try_call_player(active_player_index, self.get_active_player(
        ).play, self.ref_game_state.player_game_states[active_player_index])

        state_changed = False
        if move is not None:
            maybe_state_changed, err = self.try_call_player(
                active_player_index, move.accepts, ApplyPlayerMove(self.ref_game_state, self.get_active_player()))
            state_changed = bool(maybe_state_changed) or err is not None

        self.num_of_same_states = self.num_of_same_states + 1 if not state_changed else 0

    def get_active_player(self) -> PlayerInterface:
        """
        Returns the Player who is currently taking their turn.
            Return: Player object for the active player.
        """
        return self.players[self.ref_game_state.turn]

    def update_player_states(self) -> None:
        """
        Updates all playes with the state they should have at a given point
        MUTATES player_game_state of each player
        """
        for player_index in range(len(self.players)):
            if player_index not in self.ban_list:
                self.update_specific_player_state(player_index)

    def update_specific_player_state(self, specific_player_index: int) -> None:
        """
        Updates the state of each player to reflect what should be visible
        to them
            Parameters:
                specific_player_index(int): Index of the player to compute state for
        """
        # Referee needs to get the new state for the Player and update their internal
        # state for that player.
        updated_state = self.generate_updated_state_for_player(
            specific_player_index)
        self.ref_game_state.player_game_states[specific_player_index] = updated_state

    def generate_updated_state_for_player(self, player_index: int) -> PlayerGameState:
        """
        Create a PlayerGameState object that accurately reflects a player's
        knowledge at the time of this method call.
            Parameters:
                player_index(int): Index of player to generate state for
            Return:
                PlayerGameState: A resource representing given players state
        """
        pgs = self.ref_game_state.player_game_states[player_index]
        hand = pgs.colored_cards
        rails = pgs.rails
        connections = pgs.connections
        destinations = pgs.destinations

        # Other player's acquisitions
        other_acquisitions: List[Set[Connection]] = []

        for ind in range(len(self.players)):
            # Skip own acquisitions
            if ind == player_index:
                continue

            opp_acquisitions: Set[Connection] = self.ref_game_state.player_game_states[ind].connections
            other_acquisitions.append(opp_acquisitions)

        # rearrange the order of opponent acquisitions so that it is in order of players relative to the current player
        other_acquisitions = other_acquisitions[player_index:] + \
            other_acquisitions[:player_index]

        return PlayerGameState({*connections}, {**hand}, rails, {*destinations}, other_acquisitions)

    def all_last_turns_taken(self) -> bool:
        """
        Determines if all players have taken their last turn
            Return:
                bool: True if all players took their last turn, else False
        """
        return len(self.took_last_turn) == (len(self.players) - len(self.ban_list))

    def find_longest_continuous_path_for_player(self, player_index: int) -> int:
        """
        Finds the longest continuous path that each player can create with
        the connections that they possess.
        SOURCE: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.all_simple_paths.html#networkx.algorithms.simple_paths.all_simple_paths
            Parameters:
                player (int): The index of the player to find a connection for
            Return:
                connection_length (int): Length of player's longest connection
        """
        trains_graph = nx.MultiGraph()
        # Create graph using the given player's connections
        player_cities = self.game_map.get_cities_from_connections(
            self.ref_game_state.player_game_states[player_index].connections)
        for city in player_cities:
            trains_graph.add_node(city)

        # TODO: Maybe make this a helper
        for connection in self.ref_game_state.player_game_states[player_index].connections:
            city1 = list(connection.cities)[0]
            city2 = list(connection.cities)[1]
            weight = connection.length
            trains_graph.add_edge(city1, city2, weight=weight)

        # Get all simple paths in the graph between all cities connected via some path
        simple_paths = []
        for source_city in player_cities:
            for dest_city in player_cities:
                simple_paths += nx.all_simple_paths(
                    trains_graph, source_city, dest_city)

        # Get the weight (length) of the longest path out of all the simple paths
        max_weight = 0
        for path in map(nx.utils.pairwise, simple_paths):
            path_weight = self.max_weight_of_simple_path(
                trains_graph, list(path))
            if path_weight > max_weight:
                max_weight = path_weight

        return max_weight

    def max_weight_of_simple_path(self, graph, path) -> int:
        """
        Gets the max weight path from a set of graphs
        THIS METHOD SHOULD ONLY BE CALLED BY get_longest_path
        SOURCE: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.all_simple_paths.html#networkx.algorithms.simple_paths.all_simple_paths
            Parameters:
                graph (nx.MultiGraph): the graph that paths belong to
                path (list(edge)): paths to compare | edge is a tuple of two nodes
            Return:
                weight (int): max weight of the given path
        """
        weight = 0
        for edge in path:
            edge_weight_options = []
            # get_edge_data creates a dictionary of edge attributes (weights) for all edges in the given path
            for edge_weight_index in graph.get_edge_data(*edge).keys():
                edge_weight_options.append(graph.get_edge_data(
                    *edge)[edge_weight_index]['weight'])
            weight += max(edge_weight_options)

        return weight

    def score_game(self) -> Dict[PlayerInterface, int]:
        """
        Calculates the score of the game for each player
            Return:
                player_scores (dict(PlayerInterface, int)): dictionary of players to their corresponding scores
        """
        player_scores = dict()

        RAIL_SEGMENT_POINT_VALUE = 1
        LONGEST_CONTINUOUS_PATH_VALUE = 20
        DESTINATION_COMPLETE_VALUE = 10

        for player_index, player in enumerate(self.players):
            if player_index not in self.ban_list:
                player_game_state = self.ref_game_state.player_game_states[player_index]
                player_scores[player] = 0
                player_scores[player] += self.get_connection_score(
                    player_game_state, RAIL_SEGMENT_POINT_VALUE)
                player_scores[player] += self.get_destination_score(
                    player_game_state, DESTINATION_COMPLETE_VALUE)

        max_length_players = self.get_players_with_longest_route()
        for player in max_length_players:
            player_scores[player] += LONGEST_CONTINUOUS_PATH_VALUE

        return player_scores

    def get_players_with_longest_route(self) -> List[PlayerInterface]:
        """Get the player(s) with the longest, acyclic route."""
        max_players, max_length = [], -1
        for player_index, player in enumerate(self.players):
            if player_index not in self.ban_list:
                length = self.find_longest_continuous_path_for_player(
                    player_index)
                if length > max_length:
                    max_players, max_length = [player], length
                elif length == max_length:
                    max_players.append(player)

        return max_players

    def get_connection_score(self, player_game_state: PlayerGameState, score_value: int) -> int:
        """
        Gets the score that this player resources is worth for connections
            Parameters:
                player_resources (PlayerGameState): given PlayerGameState to score
                score_value (int): value of a segment
            Return:
                score (int): score for connections owned by this player
        """
        score = 0
        for connection in player_game_state.connections:
            score += connection.length * score_value

        return score

    def get_destination_score(self, player_game_state: PlayerGameState, score_value: int) -> int:
        """
        Gets the score that this player resources is worth for destinations
            Parameters:
                player_resources (PlayerGameState): given PlayerGameState to score
                score_value (int): value of a segment
            Return:
                score (int): score for destinations owned by this player
        """
        score = 0
        assigned_destinations = player_game_state.destinations
        reached_destinations = self.ref_game_state.game_map.get_feasible_destinations(
            player_game_state.connections)
        for destination in assigned_destinations:
            if destination in reached_destinations:
                score += score_value
            else:
                score -= score_value
        return score

    def get_ranking_of_players(self, scores: Dict[PlayerInterface, int]) -> List[List[PlayerInterface]]:
        """
        Given the final scores of the game's players in the turn order during the game,
        return a list of the players in the order of highest to lowest score.
            Parameters:
                scores (dict): Dictionary of non-banned players' scores.
            Returns:
                The ranking of the players by order of highest to lowest score.  Players who have
                the same score are sorted within their rank by name.
        """
        score2players: DefaultDict[int,
                                   List[PlayerInterface]] = defaultdict(list)
        for player, score in scores.items():
            score2players[score].append(player)

        def order_by_score(score_players: Tuple[int, List[PlayerInterface]]):
            """Ordering key function for scores and sets of Players."""
            score, players = score_players
            return (score, players)

        ordered_scores = sorted(score2players.items(),
                                key=order_by_score, reverse=True)
        ranking = [sorted(players, key=lambda player: player.get_name())
                   for _, players in ordered_scores]

        return ranking

    def get_banned_players(self) -> List[PlayerInterface]:
        """
        Gets the list of banned players
            Returns:
                List of banned players
        """
        banned_players = [self.players[i] for i in self.ban_list]
        return banned_players

    def notify_players(self, winners: List[PlayerInterface]) -> None:
        """
        Notifies player whether or not they won based on scores.
        Banned players will not be notified.
            Parameters:
                rankings (list): ranking of players
        """
        for player in self.players:
            win = False
            if self.players.index(player) not in self.ban_list:
                if player in winners:
                    win = True

                # The game is over so no ban, so we just catch and release
                try_call(player.win, win)

    def main_game_loop(self) -> None:
        """
        The main gameplay loop for a game of trains.
        This handles getting player moves, taking turns,
        and booting players that cheat.
        THIS METHOD SHOULD ONLY BE CALLED ONCE BY play_game
        """
        while not self.is_game_over():
            active_player_index = self.ref_game_state.get_current_active_player_index()
            active_player = self.players[active_player_index]

            # Skip booted players
            if active_player_index in self.ban_list:
                self.ref_game_state.next_turn()
                continue

            self.execute_active_player_move()

            # Update other players
            self.update_player_states()

            # Check if game has ended
            if self.ref_game_state.is_last_turn():
                self.took_last_turn.add(active_player)

            # Get next turn
            self.ref_game_state.next_turn()

    def play_game(self) -> Tuple[List[List[PlayerInterface]], List[PlayerInterface]]:
        """
        The main game functionality of a referee.
        Player states must be updated because this method is called
        right after __init__(). Then the main loop is run.
        Finally, the scores are calculated when the game ends.
        Players are notified if they won or lost, and rankings are
        calculated based on scores.
            Returns:
                Rankings as a list of lists (first place to last place) where the
                outer list represents placement and the inner lists represent players
                who finished at a given rank (sorted by player name),
                List of banned players sorted by player name.
        """
        # Update all player game states after initialization
        self.update_player_states()

        # Main game loop
        self.main_game_loop()

        # Score the game and notify players of win status
        scores = self.score_game()

        # sys.stderr.write(f"{repr(scores)}\n") # DEBUG

        rankings = self.get_ranking_of_players(scores)

        self.notify_players(rankings[0] if len(rankings) > 0 else [])
        # Return rankings and list of banned players
        return rankings, self.get_banned_players()

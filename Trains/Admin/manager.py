import sys
from typing import Callable, List, Tuple, TypeVar, Union

sys.path.append('../../')

from Trains.Admin.referee import Referee
from Trains.Common.map import Map
from Trains.Other.Util.constants import DEFAULT_MAP
from Trains.Other.Util.func_utils import try_call
from Trains.Other.Util.map_utils import verify_game_map
from Trains.Player.player_interface import PlayerInterface

T = TypeVar("T")


class Manager:
    """
    Represents a tournament manager that sets up and runs a tournament for games of Trains.
    The active players list will represent the tournament winners at the end of the
    tournament, since it is a knock-out elimination system.
    """

    _all_players: List[PlayerInterface]
    """All the players in the tournament"""

    eliminated_players: List[PlayerInterface]
    """Players who were eliminated for losing a tournament round."""

    banned_players: List[PlayerInterface]
    """Players who were eliminated for misbehaving."""

    def __init__(self, players: List[PlayerInterface]) -> None:
        """
        Constructor for the tournament manager that sets up a tournament with the given players.
        Players are notified of the start of the tournament upon Manager initialization.
        An initialized Manager can simply call 'run_tournament' to run a tournament.
            Parameters:
                players (list): List of players to setup for a tournament
            Raises:
                ValueError:
                - The given players is not a list
                - The given players list has less than the minimum number of players to play a game of Trains (2)
        """
        if type(players) != list:
            raise TypeError("Manager must get a list of players")

        self.MIN_PLAYERS_IN_A_GAME = 2
        if len(players) < self.MIN_PLAYERS_IN_A_GAME:
            raise ValueError(
                f"Manager must get a list of at least {self.MIN_PLAYERS_IN_A_GAME} players")

        self.MAXPLAYERS_IN_A_GAME = 8

        self._all_players = [*players]
        # Represents players who have not eliminated for losing or for misbehaving.
        self.active_players = [*players]
        # Players who were eliminated for losing a tournament round.
        self.eliminated_players = []
        # Players who were eliminated for misbehaving.
        self.banned_players = []

        self.tournament_map = self.get_valid_map(
            min(len(players), self.MAXPLAYERS_IN_A_GAME), self.setup_tournament())

        self.num_active_players = len(self.active_players)
        self.prev_num_active_players = self.num_active_players
        self.round_without_change = 0

    def setup_tournament(self) -> List[Map]:
        """
        Notifies players that they have been entered into a tournament.  The players
        respond with their game map suggestions (one Map suggestion per player).
        ONLY CALLED ONCE IN THE CONSTRUCTOR WHEN SETTING UP A TOURNAMENT.
            Returns:
                suggested_maps (list(Map)): A list of maps that were suggested by players
        """
        suggested_maps = []
        for player in self.active_players:
            suggested_map, _ = self.try_call_player(player, player.start)
            if suggested_map is not None:
                suggested_maps.append(suggested_map)
        self.remove_banned_players_from_active()
        return suggested_maps

    def verify_suggested_map(self, game_map: Map, number_of_players: int) -> bool:
        """
        Verifies whether or not a given map can be used by a given number of players.
            Parameters:
                game_map (Map): the game map that is being verified
                number_of_players (int): The number of players that would be using the given map
            Returns:
                True if the map can be used with the given number of players. False Otherwise.
        """
        NUM_DESTINATION_OPTIONS = 5
        NUM_DESTINATIONS_PER_PLAYER = 2
        return verify_game_map(game_map, number_of_players, NUM_DESTINATION_OPTIONS, NUM_DESTINATIONS_PER_PLAYER)

    def assign_players_to_games(self) -> List[List[PlayerInterface]]:
        """
        Break up players list into smaller lists of 2-8 players to be given to a Referee
        to start a game of Trains.
            Returns:
                game_assignments (list(list(PlayerInterface))): list of a lists of players where
                                  each inner list represents the 2-8 players in a game of trains
        """
        game_assignments: List[List[PlayerInterface]] = []
        if len(self.active_players) <= 1:
            return game_assignments

        curr_assignment = []
        for player in self.active_players:
            curr_assignment.append(player)
            if len(curr_assignment) == self.MAXPLAYERS_IN_A_GAME:
                curr_assignment.sort(key=lambda p: self._all_players.index(p))
                game_assignments.append(curr_assignment)
                curr_assignment = []

        # Need to backtrack to assign additional player to game with too few players
        if len(curr_assignment) == (self.MIN_PLAYERS_IN_A_GAME - 1):
            last_player_assigned = game_assignments[-1].pop()
            curr_assignment.insert(0, last_player_assigned)

        # Sort and append the last assignment if the number of players isn't divisible
        # by the max number of players in a game
        if len(curr_assignment) >= self.MIN_PLAYERS_IN_A_GAME:
            curr_assignment.sort(key=lambda p: self._all_players.index(p))
            game_assignments.append(curr_assignment)

        return game_assignments

    def get_valid_map(self, number_of_players: int, suggested_maps: List[Map]) -> Map:
        """
        Gets a valid map from the given list of suggested maps and the number of players that
        will be playing in a game.
            Parameters:
                number_of_players (int): The number of players that will be playing in a game
                suggested_maps (list): A list of maps suggested by players
            Returns:
                game_map (Map): The first valid map found in the list of suggested maps or None if no
                                valid maps are found
        """
        for game_map in suggested_maps:
            if self.verify_suggested_map(game_map, number_of_players):
                return game_map
        return self.get_default_map()

    def get_default_map(self) -> Map:
        return DEFAULT_MAP

    def eliminate_losing_players(self, losing_player_rankings: List[List[PlayerInterface]]) -> None:
        """
        Handles the elimination of players who lost in the game of trains.
        This method mutates the eliminated_players and active_players sets.
            Parameters:
                losing_player_rankings (list(list(PlayerInterface)): The rankings of the losing players from a game of trains
        """
        for ranking in losing_player_rankings:
            for player in ranking:
                self.eliminated_players.append(player)
                self.active_players.remove(player)

    def run_tournament_round(self, game_assignments: List[List[PlayerInterface]]) -> None:
        """
        Starts games of Trains using the given game assignments of players and suggested maps.
        Gets the results of each game (rankings and banned players) and eliminates losing players
        and banned players from the tournament.
            Parameters:
                game_assigments (list(list(Player))): list of a lists of players where each inner
                                              list represents the 2-8 players in a game of trains
        """
        for assignment in game_assignments:
            ref = Referee(self.tournament_map, assignment)
            game_rankings, cheaters = ref.play_game()
            # Eliminate losing players
            if len(game_rankings) >= 2:
                self.eliminate_losing_players(game_rankings[1:])
            # Eliminate banned players
            self.banned_players.extend(cheaters)
            self.remove_banned_players_from_active()

    def no_change_in_winners(self) -> bool:
        """
        Detects if two rounds of the tournament have played with the same results each time.
            Returns:
                True if two rounds have passed without change, Otherwise False
        """
        self.num_active_players = len(self.active_players)
        if self.num_active_players == self.prev_num_active_players:
            self.round_without_change += 1
            return self.round_without_change == 2
        self.prev_num_active_players = self.num_active_players
        self.round_without_change = 0
        return False

    def main_tournament_loop(self) -> None:
        """
        The main loop for running a knock-out elimination tournament.
            Returns:
                tournament_winners (list): list of winners of the last game in the tournament (sorted by name)
        """
        while True:
            game_assignments = self.assign_players_to_games()
            self.run_tournament_round(game_assignments)
            if len(game_assignments) <= 1 or self.no_change_in_winners():
                break

    def notify_players_with_results(self) -> None:
        """
        Notifies players that the tournament has ended and informs them if they won or lost.
        """
        # Notify winners
        for player in self.active_players:
            self.try_call_player(player, player.end, True)
        # Notify eliminated players
        for eliminated_player in self.eliminated_players:
            self.try_call_player(
                eliminated_player, eliminated_player.end, False)

    def run_tournament(self) -> Tuple[List[PlayerInterface], List[PlayerInterface]]:
        """
        The main tournament functionality a of manager.  Runs the main tournament loop to get the
        winners and notify all non-misbehaving participants of the tournament results.
            Returns:
                tournament_winners (list): List of winners of the last game in the tournament (sorted by name),
                banned_players (list): List of players that were caught misbehaving in games/tournament
        """
        self.main_tournament_loop()
        self.notify_players_with_results()
        return self.active_players, self.banned_players

    def try_call_player(self, player: PlayerInterface, player_method: Callable[..., T], *args) -> Union[Tuple[T, None], Tuple[None, Exception]]:
        """
        Given a player method and arugments, return the result of calling that method.
        Single point of control for calling a player's methods.
            Parameters:
                player (PlayerInterface): The player executing the method
                player_method (Callable): The player method to execute
                *args: The arguments for the given method
            Returns:
                The result of the given player method
        """
        result = try_call(player_method, *args)

        err = result[1]
        if err is not None:
            self.boot_player(
                player, "Tournament held up due to a logic error. Player booted.")

        return result

    def remove_banned_players_from_active(self) -> None:
        """
        Removes all players stored in the banned_players internal list from active_players internal list
        if they are in active_players.
        """
        for banned_player in self.banned_players:
            if banned_player in self.active_players:
                self.active_players.remove(banned_player)

    def boot_player(self, player: PlayerInterface, reason: str = "") -> None:
        """
        Boots players that are holding up the tournament.  Booted players are not entered into tournaments.
            Parameters:
                player (PlayerInterface): The player being booted
                reason (str): The reason why they are being booted
        """
        self.banned_players.append(player)

import sys
from typing import Deque, Optional, List

sys.path.append("../../../")
from Trains.Player.player_interface import PlayerInterface
from Trains.Common.map import Color, Map
from Trains.Other.Mocks.configurable_manager import ConfigurableManager
from Trains.Other.Mocks.configurable_destination_referee import ConfigurableDestinationReferee
from Trains.Admin.referee import NotEnoughDestinations

class ConfigurableDestinationManager(ConfigurableManager):
    """
    A Manager that uses a ConfigurableDestinationReferee to ensure that games in tournaments are deterministic.
    This can be used to make entire tournaments deterministic if a known deck is given.
    """
    def __init__(self, players: list, deck: Optional[Deque[Color]] = None) -> None:
        """
        Constructor that initializes a ConfigurableDestinationManager. Takes in a list of players to be used normally (as a Manager would),
        and optionally a custom deck for use by the Referee.
            Parameters:
                players (list): List of players for a tournament.
                deck (deque): Custom deck for use during tournament games.
        """
        super().__init__(players, deck)

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
            game_map = self.tournament_map
            ref = ConfigurableDestinationReferee(game_map, assignment, self._deck)
            game_rankings, cheaters = ref.play_game()
            # Eliminate losing players
            if len(game_rankings) >= 2:
                self.eliminate_losing_players(game_rankings[1:])
            # Eliminate banned players
            self.banned_players.extend(cheaters)
            self.remove_banned_players_from_active()

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
            Raises:
                NotEnoughDestinations if there is no map with enough destinations for the given number of players
        """
        for game_map in suggested_maps:
            if self.verify_suggested_map(game_map, number_of_players):
                return game_map
        raise NotEnoughDestinations(f"Not enough destinations to give each player to choose from")
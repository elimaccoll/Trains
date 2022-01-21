import sys
from typing import Deque, Optional, List

sys.path.append("../../../")
from Trains.Player.player_interface import PlayerInterface
from Trains.Admin.manager import Manager
from Trains.Admin.referee import Referee
from Trains.Common.map import Color


class ConfigurableManager(Manager):
    """ A Manager that can take in a deck to be used during games. """

    _deck: Optional[Deque[Color]]

    def __init__(self, players: List[PlayerInterface], deck: Optional[Deque[Color]] = None):
        """
        Constructor that initializes a ConfigurableManager. Takes in a list of players to be used normally (as a Manager would),
        and optionally a custom deck for use by the Referee.
            Parameters:
                players (list): List of players for a tournament.
                deck (deque): Custom deck for use during tournament games.
        """
        super().__init__(players)

        if deck is not None:
            deck = deck.copy()
        self._deck = deck

    def run_tournament_round(self, game_assignments: List[List[PlayerInterface]]):
        """
        Starts games of Trains using the given game assignments of players and suggested maps.
        Gets the results of each game (rankings and banned players) and eliminates losing players
        and banned players from the tournament.
            Parameters:
                game_assigments (list(list(PlayerInterface))): list of a lists of players where each inner
                                              list represents the 2-8 players in a game of trains
        """
        for assignment in game_assignments:
            game_map = self.tournament_map
            ref = Referee(game_map, assignment, self._deck)
            game_rankings, cheaters = ref.play_game()
            # Eliminate losing players
            if len(game_rankings) >= 2:
                self.eliminate_losing_players(game_rankings[1:])
            # Eliminate banned players
            self.banned_players.extend(cheaters)
            self.remove_banned_players_from_active()

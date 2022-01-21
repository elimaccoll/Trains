import sys
from typing import Set

sys.path.append("../../../")
from Trains.Common.map import Destination, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.moves import DrawCardMove, IPlayerMove
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.strategy import PlayerStrategyInterface


class DrawCardsStrategy(PlayerStrategyInterface):
    """ Strategy used for testing that always draws cards """
    def select_destinations(self, destinations: Set[Destination], num_destinations: int) -> Set[Destination]:
        """
        Strategy for selecting their 2 destinations during the setup of the game.
            Parameters:
                destinations (set(Destination)): Destinations to choose 2 from according to the strategy above.
                num_destinations (int): number of destinations to pick, num_destinations <= len(destination)
            Returns:
                set(Destination): The set of destinations selected
            Throws:
                ValueError: num_destinations must be less than set size
        """
        if num_destinations > len(destinations):
            raise ValueError("num_destinations must be <= len(destinations)")

        dests_as_list = list(destinations)
        return set(dests_as_list[:num_destinations])

    def get_player_move(self, pgs: PlayerGameState, game_map: Map) -> IPlayerMove:
        """
        Always Draw cards.
            Parameters:
                resources (PlayerResources): Player resources to inform decision making
            Return:
                A PlayerMove indicating a player's intended move
        """
        return DrawCardMove()

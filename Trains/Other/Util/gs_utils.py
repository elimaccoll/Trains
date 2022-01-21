import sys

sys.path.append('../../')
from Trains.Common.map import Connection
from Trains.Common.player_game_state import PlayerGameState


def can_acquire_connection(pgs: PlayerGameState, unacquired_connection: Connection) -> bool:
    """
    Determines whether or not a player has enough resources (rails and corresponding colored cards) to acquire a given connection.
        Parameters:
            pgs (PlayerGameState): the resources the player implementing this strategy has
            unacquired_connection (Connection): The connection being checked to see if the player has the resources to acquire it.
        Returns:
            True if the player has the necessary resources to acquire the connection, False otherwise
    """
    return pgs.rails >= unacquired_connection.length and pgs.colored_cards[unacquired_connection.color] >= unacquired_connection.length

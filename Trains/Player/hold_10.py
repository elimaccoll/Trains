import sys

sys.path.append('../../')

from Trains.Common.map import Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.buy_now import Buy_Now
from Trains.Player.moves import DrawCardMove, IPlayerMove
from Trains.Player.strategy import AbstractPlayerStrategy


class Hold_10(AbstractPlayerStrategy):
    """
    Represents the following strategy:
    - Draw cards if the player with this strategy has 10 or less cards.
    - If the player has more than 10 cards, attempt to acquire a connection.
    - - The logic for attempting to acquire a connection is the same as the BuyNow strategy
    """
    def get_player_move(self, pgs: PlayerGameState, game_map: Map) -> IPlayerMove:
        """
        Polls the Hold_10 player strategy for a move.  The logic here follows the strategy described
        above in the Hold_10 Class purpose statement.
            Parameters:
                game_state (PlayerGameState): the game state of the player implementing this strategy
            Return:
                A PlayerMove indicating a player's intended move
        """
        # Draw cards if player has 10 or fewer colored cards
        if pgs.get_total_cards() <= 10:
            return DrawCardMove()

        # Otherwise attempt to acquire a connection
        return Buy_Now().get_player_move(pgs, game_map)

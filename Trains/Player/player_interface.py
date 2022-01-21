import sys
from abc import ABCMeta, abstractmethod
from typing import Dict, List, Set

sys.path.append('../../')
from Trains.Common.map import Color, Destination, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Player.moves import IPlayerMove


class PlayerInterface(metaclass=ABCMeta):

    @abstractmethod
    def setup(self, map: Map, rails: int, cards: Dict[Color, int]) -> None:
        """
        Sets the player up with a map, a number of rails, and a hand of cards.
            Parameters:
                - map (Map): The map of the game.
                - rails (int): The number of rails the player will start with.
                - cards (dict): The hand of cards the player starts with.
        """
        pass

    @abstractmethod
    def play(self, active_game_state: PlayerGameState) -> IPlayerMove:
        """
        Polls the player strategy for a move.
            Parameters:
                active_game_state (PlayerGameState): The game state of this player when they've become active.
            Return:
                A PlayerMove indicating a player's intended move
        """
        pass

    @abstractmethod
    def pick(self, destinations: Set[Destination]) -> Set[Destination]:
        """
        Given a set of destinations, the player picks two destinations and the three
        that were not chosen are returned.
            Parameters:
                destinations (set(Destination)): Set of five destinations to choose from.
            Return:
                A set(Destination) containing the three destinations the player did not pick.
        """
        pass

    @abstractmethod
    def more(self, cards: List[Color]) -> None:
        """
        Hands this player some cards
            Parameters:
                cards (list(Color)): cards being handed to player
        """
        pass

    @abstractmethod
    def win(self, winner: bool) -> None:
        """
        Informs player that the game is over.  Tells players whether or not they won the game.
        ONLY CALLED ONCE(PER PLAYER) AT THE END OF THE GAME
            Parameters:
                winner (bool): True if this player won the game, False otherwise
        """
        pass

    @abstractmethod
    def start(self) -> Map:
        """
        Informs player that they have been entered into a tournament.  Player responds by
        returning a game map to suggest for use in a game of trains.
        ONLY CALLED ONCE(PER PLAYER) BY MANAGER AT THE START OF A TOURNAMENT
            Returns:
                The player's game map (Map) suggestion
        """
        pass

    @abstractmethod
    def end(self, winner: bool) -> None:
        """
        Informs player that the tournament is over.  Tells the player whether or not they won
        the tournament.
        ONLY CALLED ONCE (PER PLAYER) BY MANAGER AT THE END OF A TOURNAMENT
            Parameters:
                winner (bool): True if the player won the tournament, False otherwise
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Gets the name of the player. Calling this method should never fail; the information is always cached locally.
            Returns:
                name (str): The name of the player
        """
        pass

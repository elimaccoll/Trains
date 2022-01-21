import json
import sys
from typing import Dict, Iterable, List, Optional, Set

sys.path.append('../../')

from asyncio import AbstractEventLoop, get_event_loop

from Trains.Common.map import Color, Destination, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Other.Util.json_utils import (JSONDestination,
                                          convert_dict_hand_to_json_hand,
                                          convert_json_connection_to_data,
                                          convert_json_destinations_to_data,
                                          convert_json_map_to_data_map)
from Trains.Player.moves import AcquireConnectionMove, DrawCardMove, IPlayerMove
from Trains.Player.player_interface import PlayerInterface
from Trains.Remote.tcp_connection import JSONValue, TCPConnection


def format_message(name: str, *args: str) -> str:
    msg = f'["{name}", [{", ".join(args)}]]'
    return msg


def join_json_strs(iterable: Iterable[str]) -> str:
    msg = f"[{', '.join(iterable)}]"
    return msg


class RemoteProxyPlayer(PlayerInterface):
    """ Facilitates interactions between Manager and clients with a TCPConnection to a client's corresponding RemotePlayerInvoker. """

    GAME_ACTION_TIMEOUT = 2

    _name: str
    _client: TCPConnection
    _loop: AbstractEventLoop
    _game_map: Optional[Map]

    @property
    def client(self):
        return self._client

    def __init__(self, name: str, client: TCPConnection) -> None:
        super().__init__()
        self._name = name
        self._client = client
        self._loop = get_event_loop()

    def setup(self, game_map: Map, rails: int, cards: Dict[Color, int]) -> None:
        """
        Sets the player up with a map, a number of rails, and a hand of cards.
            Parameters:
                - game_map (Map): The map of the game.
                - rails (int): The number of rails the player will start with.
                - cards (dict): The hand of cards the player starts with.
        """
        self._game_map = game_map # cache

        msg = format_message(
            "setup", game_map.get_as_json(), json.dumps(rails), convert_dict_hand_to_json_hand(cards))
        self._loop.run_until_complete(self._client.write(msg, timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))

        json_response = self._loop.run_until_complete(
            self._client.read(timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))

        if json_response != "void": raise RuntimeError("Method call did not return void")

    def play(self, active_game_state: PlayerGameState) -> IPlayerMove:
        """
        Polls the player strategy for a move.
            Parameters:
                active_game_state (PlayerGameState): The game state of this player when they've become active.
            Return:
                A PlayerMove indicating a player's intended move
        """
        if self._game_map is None:
            raise RuntimeError("Player is not setup yet.")

        msg = format_message(
            "play", active_game_state.get_as_json())
        self._loop.run_until_complete(self._client.write(msg, timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))

        json_response = self._loop.run_until_complete(
            self._client.read(timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))
        return self._parse_player_move(json_response, self._game_map)

    def _parse_player_move(self, json_value: JSONValue, game_map: Map) -> IPlayerMove:
        if json_value == "more cards":
            return DrawCardMove()
        elif type(json_value) is list:
            return AcquireConnectionMove(convert_json_connection_to_data(json_value, game_map))
        else:
            raise ValueError("Bad PlayerMove json")

    def pick(self, destinations: Set[Destination]) -> Set[Destination]:
        """
        Given a set of destinations, the player picks two destinations and the three
        that were not chosen are returned.
            Parameters:
                destinations (set(Destination)): Set of five destinations to choose from.
            Return:
                A set(Destination) containing the three destinations the player did not pick.
        """
        msg = format_message(
            "pick", join_json_strs(destination.get_as_json() for destination in destinations))
        self._loop.run_until_complete(self._client.write(msg, timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))

        json_response = self._loop.run_until_complete(
            self._client.read(timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))
        if type(json_response) is not list:
            raise RuntimeError  # TODO: find better error to use

        destinations_not_chosen = {convert_json_destinations_to_data(
            destination, destinations) for destination in json_response}
        return destinations_not_chosen

    def more(self, cards: List[Color]) -> None:
        """
        Hands this player some cards
            Parameters:
                cards (list(Color)): cards being handed to player
        """
        json_cards = json.dumps([card.value for card in cards])
        msg = format_message(
            "more", json_cards)
        self._loop.run_until_complete(self._client.write(msg, timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))

        json_response = self._loop.run_until_complete(
            self._client.read(timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))

        if json_response != "void": raise RuntimeError("Method call did not return void")

    def win(self, winner: bool) -> None:
        """
        Informs player that the game is over.  Tells players whether or not they won the game.
        ONLY CALLED ONCE(PER PLAYER) AT THE END OF THE GAME
            Parameters:
                winner (bool): True if this player won the game, False otherwise
        """
        msg = format_message(
            "win", json.dumps(winner))
        self._loop.run_until_complete(self._client.write(msg, timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))

        json_response = self._loop.run_until_complete(
            self._client.read(timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))

        if json_response != "void": raise RuntimeError("Method call did not return void")

    def start(self) -> Map:
        """
        Informs player that they have been entered into a tournament.  Player responds by
        returning a game map to suggest for use in a game of trains.
        ONLY CALLED ONCE(PER PLAYER) BY MANAGER AT THE START OF A TOURNAMENT
            Returns:
                The player's game map (Map) suggestion
        """
        msg = format_message(
            "start", json.dumps(True))
        self._loop.run_until_complete(self._client.write(msg, timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))

        json_response = self._loop.run_until_complete(
            self._client.read(timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))
        if type(json_response) is not dict:
            raise RuntimeError  # TODO: find better error to use

        game_map = convert_json_map_to_data_map(json_response)
        return game_map


    def end(self, winner: bool) -> None:
        """
        Informs player that the tournament is over.  Tells the player whether or not they won
        the tournament.
        ONLY CALLED ONCE (PER PLAYER) BY MANAGER AT THE END OF A TOURNAMENT
            Parameters:
                winner (bool): True if the player won the tournament, False otherwise
        """
        msg = format_message(
            "end", json.dumps(winner))
        self._loop.run_until_complete(self._client.write(msg, timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))

        json_response = self._loop.run_until_complete(
            self._client.read(timeout=RemoteProxyPlayer.GAME_ACTION_TIMEOUT))

        if json_response != "void": raise RuntimeError("Method call did not return void")

    def get_name(self) -> str:
        """
        Gets the name of the player. Calling this method should never fail; the information is always cached locally.
            Returns:
                name (str): The name of the player
        """
        return self._name

    def __repr__(self) -> str:
        # For debugging only
        return f'RemoteProxyPlayer(name="{self._name}")'

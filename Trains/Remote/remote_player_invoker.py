import json
import sys
from typing import Any, List, Optional, Tuple

sys.path.append('../../')
from Trains.Common.map import Color, Map
from Trains.Other.Util.func_utils import try_call_async
from Trains.Other.Util.json_utils import (
    convert_json_colored_cards_list_to_colored_cards_dict,
    convert_json_destinations_to_data, convert_json_map_to_data_map,
    convert_json_this_player_to_data)
from Trains.Player.moves import (AcquireConnectionMove, DrawCardMove,
                                 IPlayerMoveVisitor)
from Trains.Player.player_interface import PlayerInterface
from Trains.Remote.tcp_connection import JSONValue, TCPConnection


class PlayerMoveToJSONSerializer(IPlayerMoveVisitor[JSONValue]):
    """An PlayerMove to JSON serializer."""

    def visitDrawCards(self, _: DrawCardMove) -> JSONValue:
        return "more cards"

    def visitAcquireConnection(self, move: AcquireConnectionMove) -> JSONValue:
        connection = move.connection
        city1, city2 = sorted(city.name for city in connection.cities)
        json_connection = [city1, city2,
                           connection.color.value, connection.length]
        return json_connection


class RemotePlayerInvoker:
    """ Facilitates interactions between clients and Manager with a TCPConnection to a client's corresponding RemoteProxyPlayer. """

    _client: TCPConnection
    _player: PlayerInterface
    _game_map: Optional[Map]

    def __init__(self, client: TCPConnection, player: PlayerInterface) -> None:
        self._client = client
        self._player = player
        self._game_map = None

    async def start_and_wait_until_closed(self) -> None:
        while not self._client.is_closed():
            await try_call_async(self._try_read_write, timeout=2)

    async def _try_read_write(self):
        json_request = await self._client.read()
        method, args = self.parse_json_player_call(json_request)
        json_response_str = self._get_matched_json_response(
            method, *args)
        await self._client.write(json_response_str)

    def _get_matched_json_response(self, method: str, *args: JSONValue) -> str:
        if method == "start":
            game_map = self._player.start()
            return game_map.get_as_json()

        if method == "setup":
            json_map, rails, json_player_hand = args
            if type(json_map) is not dict:
                raise ValueError("Given JSON map type is invalid")
            if type(rails) is not int:
                raise ValueError("Given JSON map type is invalid")
            if type(json_player_hand) is not list:
                raise ValueError("Given JSON map type is invalid")

            cards = convert_json_colored_cards_list_to_colored_cards_dict(
                json_player_hand)
            game_map = convert_json_map_to_data_map(json_map)
            self._game_map = game_map
            self._player.setup(game_map, rails, cards)
            return json.dumps("void")

        if method == "pick":
            json_destinations, = args
            if type(json_destinations) is not list:
                raise ValueError(
                    "Given JSON destinations list type is invalid")
            if self._game_map is None:
                raise RuntimeError("Map is currently unknown")

            all_destinations = self._game_map.get_all_feasible_destinations()
            destinations = {convert_json_destinations_to_data(
                destination, all_destinations) for destination in json_destinations}

            destinations_not_chosen = self._player.pick(destinations)
            return f'[{", ".join(destination.get_as_json() for destination in destinations_not_chosen)}]'

        if method == "play":
            json_pgs, = args
            if type(json_pgs) is not dict:
                raise ValueError(
                    "Given JSON player game state type is invalid")
            if self._game_map is None:
                raise RuntimeError("Map is currently unknown")

            pgs = convert_json_this_player_to_data(json_pgs, self._game_map)
            player_move = self._player.play(pgs)
            return json.dumps(player_move.accepts(PlayerMoveToJSONSerializer()))

        if method == "more":
            json_card_list, = args
            if type(json_card_list) is not list:
                raise ValueError("Given JSON card list type is invalid")

            cards_list: List[Color] = [Color(color)
                                       for color in json_card_list]
            self._player.more(cards_list)
            return json.dumps("void")

        if method == "win":
            result, = args
            if type(result) is not bool:
                raise ValueError("Given JSON win result type is invalid")

            self._player.win(result)
            return json.dumps("void")

        if method == "end":
            result, = args
            if type(result) is not bool:
                raise ValueError("Given JSON end result type is invalid")

            self._player.end(result)
            return json.dumps("void")

        raise ValueError(f"Unexpected method: {method}")

    def parse_json_player_call(self, json_request: JSONValue) -> Tuple[str, List[Any]]:
        if type(json_request) is not list:
            raise ValueError("JSON request must be a list.")
        if len(json_request) != 2:
            raise ValueError("JSON request must contain two arguments")
        if type(json_request[0]) is not str and type(json_request[1]) is not list:
            raise ValueError("JSON request contains invalid argument types")

        return json_request[0], json_request[1]

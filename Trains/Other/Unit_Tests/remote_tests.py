import asyncio
import json
import sys
from asyncio import AbstractEventLoop
from asyncio.streams import StreamReader, StreamWriter
from typing import Optional, Tuple
from unittest import TestCase, main
from unittest.mock import Mock

sys.path.append('../../../')
from Trains.Common.map import City, Color, Connection, Destination, Map
from Trains.Common.player_game_state import PlayerGameState
from Trains.Other.Mocks.mock_tournament_player import MockTournamentPlayer
from Trains.Other.Util.constants import DEFAULT_MAP
from Trains.Other.Util.test_utils import IsDrawCardMove
from Trains.Player.moves import DrawCardMove
from Trains.Player.player import Buy_Now_Player
from Trains.Player.player_interface import PlayerInterface
from Trains.Remote.remote_player_invoker import RemotePlayerInvoker
from Trains.Remote.remote_proxy_player import RemoteProxyPlayer
from Trains.Remote.tcp_connection import TCPConnection


def create_stream_reader_writer(loop: AbstractEventLoop) -> Tuple[StreamReader, StreamWriter]:
    reader = StreamReader(loop=loop)
    reader.at_eof = Mock(return_value=False)

    def mock_write(data: bytes) -> None:
        reader.feed_data(data)

    mock_transport = Mock()
    mock_transport.is_closing = Mock(return_value=False)

    async def mock_close() -> None:
        reader.at_eof = Mock(return_value=True)
        mock_transport.is_closing = Mock(return_value=True)

    async def mock_drain() -> None:
        await asyncio.sleep(0)

    writer = StreamWriter(mock_transport, None, reader, None)
    writer.write = Mock(side_effect=mock_write)
    writer.close = Mock(side_effect=mock_close)
    writer.drain = Mock(side_effect=mock_drain)

    return reader, writer


def create_tcp_connections(loop: Optional[AbstractEventLoop] = None) -> Tuple[TCPConnection, TCPConnection]:
    if loop is None:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    reader1, writer1 = create_stream_reader_writer(loop)
    reader2, writer2 = create_stream_reader_writer(loop)

    return TCPConnection(reader1, writer2), TCPConnection(reader2, writer1)


def create_proxy_player(name: str, tcp: TCPConnection) -> RemoteProxyPlayer:
    return RemoteProxyPlayer(name, tcp)


def create_proxy_player_invoker(tcp: TCPConnection, player: PlayerInterface) -> RemotePlayerInvoker:
    return RemotePlayerInvoker(tcp, player)


class TestTCPConnection(TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.tcp1, self.tcp2 = create_tcp_connections(self.loop)

    def test_tcp_connections(self) -> None:
        async def go():
            msg = "This is a JSON string"
            json_msg = json.dumps(msg)

            await self.tcp1.write(json_msg)
            read_msg = await self.tcp2.read()

            self.assertEqual(msg, read_msg)

        self.loop.run_until_complete(go())


class TestRemoteProxyPlayer(TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.tcp1, self.tcp2 = create_tcp_connections(self.loop)
        self.rpp = create_proxy_player("Dennis", self.tcp1)
        self.rpi = create_proxy_player_invoker(
            self.tcp2, MockTournamentPlayer("Dennis", DrawCardMove()))

    def test_remote_start(self) -> None:
        asyncio.ensure_future(self.rpi._try_read_write())

        map = self.rpp.start()
        self.assertEqual(map, DEFAULT_MAP)

    def test_remote_play(self) -> None:
        cards = {Color.RED: 5, Color.BLUE: 6,
                 Color.GREEN: 7, Color.WHITE: 8}
        dests = list(DEFAULT_MAP.get_all_feasible_destinations())

        asyncio.ensure_future(self.rpi._try_read_write())
        self.rpp.setup(DEFAULT_MAP, 10, cards)

        asyncio.ensure_future(self.rpi._try_read_write())

        pr1 = PlayerGameState(set(), cards, 10, {dests[0], dests[1]}, [set()])
        move = self.rpp.play(pr1)
        self.assertTrue(move.accepts(IsDrawCardMove()))


if __name__ == '__main__':
    main()

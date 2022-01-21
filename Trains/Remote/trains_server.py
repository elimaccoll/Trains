import sys
from asyncio import gather, get_event_loop, start_server
from asyncio.events import AbstractEventLoop, AbstractServer
from asyncio.streams import StreamReader, StreamWriter
from typing import Dict, List, Optional

sys.path.append('../')
from Trains.Other.Util.func_utils import try_call_async
from Trains.Remote.remote_proxy_player import RemoteProxyPlayer
from Trains.Remote.tcp_connection import TCPConnection

DEFAULT_MAX_NUM_CLIENTS = 50
"""The maximum number of clients permitted to sign up"""


def _is_ascii(string: str) -> bool:
    return all(0 <= ord(char) < 128 for char in string)


class TrainsServer:
    """A server for asynchronously establishing TCP connections with remote Trains players, but
    whose external interface is synchronous."""

    _port: int
    _max_clients: int
    _rpps: Dict[str, RemoteProxyPlayer]
    _server: Optional[AbstractServer]
    _loop: AbstractEventLoop
    _accept_new_connections: bool

    def __init__(self, port: int, max_clients: int = DEFAULT_MAX_NUM_CLIENTS) -> None:
        self._port = port
        self._max_clients = max_clients
        self._rpps = {}
        self._server = None
        self._loop = get_event_loop()
        self._accept_new_connections = False

    def _get_unique_name(self, base_name: str) -> str:
        # There is no guarantee that distinct clients sign up with distinct names.
        # If the administrative framework employs an observer, the server should make
        # the names unique by adding suffixes.
        counter = 0
        result = base_name
        while result in self._rpps:
            counter += 1
            result = f'{base_name}{counter}'
        return result

    def start(self):
        """ Starts server for a Trains tournament. """
        if self._server is not None:
            raise RuntimeError("Server was already started")

        self._accept_new_connections = True

        async def handle_connection(reader: StreamReader, writer: StreamWriter) -> None:
            """Handler for a new client connection to the server."""
            # Waiting period to receive a name after a connection is established
            NAME_TIMEOUT = 3
            tcp = TCPConnection(reader, writer)

            if not self._accept_new_connections:
                return await tcp.close()

            name, _ = await try_call_async(tcp.read, timeout=NAME_TIMEOUT)

            if type(name) is not str or len(name) < 1 or len(name) > 50 or not _is_ascii(name):
                return await tcp.close()

            unique_name = self._get_unique_name(name)
            player = RemoteProxyPlayer(unique_name, tcp)
            self._rpps[unique_name] = player

            if len(self._rpps) >= self._max_clients:
                self._accept_new_connections = False

        self._server = self._loop.run_until_complete(start_server(
            handle_connection, host='localhost', port=self._port))

    def set_listening(self, is_listening: bool) -> None:
        """Controls whether the server is listening for and accepting new connections.
        Can always be set to `False`.

        Raises:
            - RuntimeError:
                - when called before `TrainsServer.start()`
                - when called after the maximum number of clients have connected"""
        # always accept False
        if not is_listening:
            self._accept_new_connections = is_listening
            return

        if self._server is None:
            raise RuntimeError(
                "Cannot resume listening on unstarted server.")

        if len(self._rpps) >= self._max_clients:
            raise RuntimeError(
                "Cannot resume listening, the max number of clients has been reached.")

        self._accept_new_connections = is_listening

    def get_players(self) -> List[RemoteProxyPlayer]:
        return [*self._rpps.values()]

    def get_max_clients(self) -> int:
        return self._max_clients

    def shutdown(self) -> None:
        if self._server is None:
            return

        self._loop.run_until_complete(
            gather(*[rpp.client.close() for rpp in self.get_players() if not rpp.client.is_closed()]))
        self._server.close()
        self._loop.run_until_complete(self._server.wait_closed())

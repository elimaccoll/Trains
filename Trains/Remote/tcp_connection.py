import json
import sys
from asyncio import wait_for
from asyncio.streams import StreamReader, StreamWriter
from typing import Optional, Union

sys.path.append('../../')
from Trains.Other.Util.func_utils import try_call_async

JSONValue = Union[int, float, str, list, bool, None, dict]


class TCPConnection:
    BYTES_TO_READ = 8192

    _reader: StreamReader
    _writer: StreamWriter

    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self._reader = reader
        self._writer = writer

    async def read(self, timeout: Optional[int] = None) -> JSONValue:
        async def read_helper() -> JSONValue:
            read_so_far = ""
            is_json = False
            result = None
            while not is_json:
                if self.is_closed():
                    raise ConnectionError("Connection error")

                data_bytes = await self._reader.read(TCPConnection.BYTES_TO_READ)
                read_so_far += data_bytes.decode()
                try:
                    result = json.loads(read_so_far)
                    is_json = True
                except:
                    continue
            return result

        return await wait_for(read_helper(), timeout=timeout)

    async def write(self, string: str, timeout: Optional[int] = None) -> None:
        if self.is_closed():
            raise ConnectionError("Connection error")

        self._writer.write(string.encode())
        return await wait_for(self._writer.drain(), timeout=timeout)

    def is_closed(self) -> bool:
        return self._reader.at_eof() or self._writer.transport.is_closing()

    async def close(self) -> None:
        DRAIN_TIMEOUT = 2  # TODO: merge with other constants

        if self.is_closed():
            return

        if self._writer.can_write_eof():
            self._writer.write_eof()

        await try_call_async(wait_for, self._writer.drain(), DRAIN_TIMEOUT)
        self._writer.close()

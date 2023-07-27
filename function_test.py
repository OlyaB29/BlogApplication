import asyncio
import aiohttp
from unittest import TestCase, mock


# tested function
async def logs(cont, name):
    conn = aiohttp.UnixConnector(path="/var/run/docker.sock")
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(f"http://xx/containers/{cont}/logs?follow=1&stdout=1") as resp:
            async for line in resp.content:
                print(name, line)


# redefined the methods of the base class to avoid the NotImplementationError error
class MyLoop(asyncio.AbstractEventLoop):
    async def create_unix_connection(self, *args, **kwargs):
        print("Method redefined")

    async def run_until_complete(self, *args, **kwargs):
        print("Method redefined")


class TestLogs(TestCase):

    async def test_logs(self):
        cont = 'd0d7c00fdec42f3cc08b700c7'
        name = 'my_container'
        test_content = [b'data1\n', b'data2\n', b'data3\n', b'data4\n', b'data5\n']

        connector_mock = mock.Mock()
        session_mock = mock.Mock()
        response_mock = mock.Mock()

        connector_mock.path = "/var/run/docker.sock"
        session_mock.__aenter__ = response_mock
        response_mock.content = test_content

        loop = MyLoop()
        await loop.run_until_complete(logs(cont, name))

        connector_mock.assert_called_once_with(path="/var/run/docker.sock")
        session_mock.assert_called_once_with(connector=connector_mock)
        session_mock.get.assert_called_once_with(f"http://xx/containers/{cont}/logs?follow=1&stdout=1")
        response_mock.__aenter__.assert_called_once()
        response_mock.__aexit__.assert_called_once()

        self.assertEqual(response_mock.content.__aiter__.call_count, 1)
        self.assertEqual(response_mock.content.__aiter__.return_value.__anext__.call_count, 5)

        self.assertEqual(response_mock.content.__aiter__.return_value.__anext__.call_args_list, [
            mock.call(), mock.call(), mock.call(), mock.call(), mock.call()
        ])



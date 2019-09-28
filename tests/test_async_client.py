import asyncio
from aiohttp import web
from unittest.mock import patch

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from pyacryl2.async_client import AcrylAsyncClientResponse, AcrylAsyncClient
from pyacryl2.client import AcrylClientResponse
from pyacryl2.utils import AcrylAddressGenerator


class AcrylAsyncClientTest(AioHTTPTestCase):

    def setUp(self):
        super().setUp()
        self.api_client = AcrylAsyncClient(node_address="http://{}:{}".format(self.server.host, self.server.port))

    async def get_application(self):

        async def node_version(request):
            return web.json_response({"version": "v99999"})

        app = web.Application()
        app.router.add_get('/node/version', node_version)
        return app

    @unittest_run_loop
    async def test_request_response(self):
        node_version_response = await self.api_client.node_version()
        self.assertIsInstance(node_version_response, AcrylClientResponse)
        self.assertTrue(node_version_response)
        self.assertEqual(node_version_response.response_data, {"version": "v99999"})

    @patch('pyacryl2.async_client.AcrylAsyncClient')
    def test_mocked_request_response(self, mocked_client):
        client = mocked_client()
        data = {"version": "v99999"}
        request_future = self.loop.create_future()
        request_future.set_result(AcrylAsyncClientResponse(successful=True, response_data=data))
        client.node_version.return_value = request_future
        node_version_response = self.loop.run_until_complete(client.node_version())
        self.assertIsInstance(node_version_response, AcrylClientResponse)
        self.assertTrue(node_version_response)
        self.assertEqual(node_version_response.response_data, data)

    @unittest_run_loop
    async def test_offline_client(self):
        client = AcrylAsyncClient(online=False)
        request = await client.node_version()
        self.assertIsInstance(request, dict)
        self.assertIn('url', request)
        self.assertIn('headers', request)

    @unittest_run_loop
    async def test_client_session_context(self):
        client = self.api_client
        current_session = client.session
        await client.node_version()
        self.assertIs(client.session, current_session)
        await client.close_session()
        self.assertIsNone(self.api_client.session)

    @unittest_run_loop
    async def test_client_session_context(self):
        async with self.api_client as context_client:
            current_session = context_client.session
            await context_client.node_version()
            self.assertIs(context_client.session, current_session)

        self.assertIsNone(self.api_client.session)
        await self.api_client.node_version()
        self.assertIsNone(self.api_client.session)

    @unittest_run_loop
    async def test_offline_async_client(self):
        client = AcrylAsyncClient(online=False)
        request = await client.node_version()
        self.assertIsInstance(request, dict)
        self.assertIn('url', request)
        self.assertIn('headers', request)

    @unittest_run_loop
    async def test_offline_address(self):
        address_generator = AcrylAddressGenerator(async_address=True)
        address = address_generator.generate(online=False)
        balance_result = await address.get_balance()
        self.assertIsInstance(balance_result, dict)
        transfer_result = await address.transfer_acryl('3EMZGnpVGcCWjdQWAU2Hc8SFUVUDnxKnprX', 1000, attachment="test")
        self.assertIsInstance(transfer_result, dict)

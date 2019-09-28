import unittest
from unittest.mock import patch
from pyacryl2.client import AcrylClientResponse, AcrylClient


class AcrylClientTest(unittest.TestCase):

    @patch('pyacryl2.client.AcrylClient')
    def test_request_response(self, mocked_client):
        client = mocked_client()
        data = {"version": "v99999"}
        client.node_version.return_value = AcrylClientResponse(
            successful=True, response_data=data
        )
        node_version = client.node_version()
        self.assertIsInstance(node_version, AcrylClientResponse)
        self.assertTrue(node_version)
        self.assertEqual(node_version.response_data, data)

    def test_offline_client(self):
        client = AcrylClient(online=False)
        request = client.node_version()
        self.assertIsInstance(request, dict)
        self.assertIn('url', request)
        self.assertIn('headers', request)

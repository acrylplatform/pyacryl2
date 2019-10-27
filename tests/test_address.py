import unittest
from unittest.mock import patch

import base58

from pyacryl2 import AcrylClient
from pyacryl2.utils import AcrylAddress
from pyacryl2.utils import AcrylAddressGenerator
from pyacryl2.utils import AcrylAsyncAddress


class AddressGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.address_generator = AcrylAddressGenerator()

    def test_generating_class(self):
        address = self.address_generator.generate()
        self.assertIsInstance(address, AcrylAddress)
        address = self.address_generator.generate()
        self.assertNotIsInstance(address, AcrylAsyncAddress)

    def test_address_client(self):
        address = self.address_generator.generate()
        self.assertIsInstance(getattr(address, '_api_client'), AcrylClient)


class AddressMethodsTest(unittest.TestCase):

    @patch('pyacryl2.utils.address.AcrylAddress')
    def test_address_from_alias(self, mocked_address):
        address = mocked_address()
        address.from_alias.return_value = None
        result = address.from_alias('acrylalias')
        self.assertIs(None, result)

    def test_offline_address(self):
        address_generator = AcrylAddressGenerator()
        address = address_generator.generate(online=False)
        balance_result = address.get_balance()
        self.assertIsInstance(balance_result, dict)
        transfer_result = address.transfer_acryl('3EMZGnpVGcCWjdQWAU2Hc8SFUVUDnxKnprX', 1000, attachment="test")
        self.assertIsInstance(transfer_result, dict)

    def test_base58_seed_encode(self):
        address_generator = AcrylAddressGenerator()
        address = address_generator.generate()
        self.assertEqual(address.base58_seed, base58.b58encode(address.seed.encode('latin-1')).decode())


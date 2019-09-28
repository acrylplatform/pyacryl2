import unittest

from pyacryl2 import AcrylAsyncClient
from pyacryl2.utils import AcrylAddress
from pyacryl2.utils import AcrylAddressGenerator
from pyacryl2.utils import AcrylAsyncAddress


class AsyncAddressGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.address_generator = AcrylAddressGenerator(async_address=True)

    def test_generating_class(self):
        address = self.address_generator.generate()
        self.assertIsInstance(address, AcrylAsyncAddress)
        address = self.address_generator.generate()
        self.assertNotIsInstance(address, AcrylAddress)

    def test_address_client(self):
        address = self.address_generator.generate()
        self.assertIsInstance(getattr(address, '_api_client'), AcrylAsyncClient)


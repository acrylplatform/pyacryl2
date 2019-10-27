"""
pyacryl2.utils.address_generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Address generator for Acryl blockchain
"""

import hashlib
import struct

import base58
import sha3
import axolotl_curve25519
from mnemonic import Mnemonic

from pyacryl2.client import DEFAULT_NODE_ADDRESS, DEFAULT_CHAIN_ID
from pyacryl2.utils.address import AcrylAddress, DEFAULT_ADDRESS_VERSION
from pyacryl2.utils.async_address import AcrylAsyncAddress


class AcrylAddressGenerator:
    """
    Acryl address generator

    :param node_address: node API URL
    :type node_address: str
    :param async_address: return address with async client instead of default sync
    :type async_address: bool
    """

    def __init__(self, node_address=DEFAULT_NODE_ADDRESS, async_address=False):
        self.node_address = node_address
        self.async_address = async_address

    def generate(self, value=None, private_key=None, public_key=None, seed=None, chain_id=DEFAULT_CHAIN_ID, nonce=0,
                 version=DEFAULT_ADDRESS_VERSION, online=True, client_request_params=None):
        """
        Generate address
            - if there is no seed and private key is specified then generate address value and public key
            - if there is no seed and public key is specified then generate address value
            - if there is no seed and value is specified with any key then validate them and return address object
            - if there is no seed and no any key but value is specified validation or generation is not performed,
                address object would be returned with the same value and chain_id

        :param value: address string value in base58
        :param private_key: private key string value in base58
        :param public_key: private key string value in base58
        :param seed: seed
        :param chain_id: chain id value
        :param nonce: nonce
        :param version: address version
        :param online: if True send requests else return request params dict
        :param: client_request_params:
        :return: AcrylAddress or AsyncAcrylAddress object with different attributes
        :rtype: AcrylAddress or AcrylAsyncAddress
        """
        address_class = AcrylAddress if not self.async_address else AcrylAsyncAddress
        if not seed and value and any((private_key, public_key)):
            address_data = self.validate_address(value, private_key, public_key, chain_id)
            return address_class(
                address_data["value"], address_data["private_key"] if "private_key" in address_data else None,
                address_data["public_key"] if "public_key" in address_data else None,
                chain_id, nonce, node_address=self.node_address, online=online,
                client_request_params=client_request_params
            )

        if not seed and not private_key and not public_key and value:
            return address_class(
                value, chain_id=chain_id, node_address=self.node_address, online=online,
                client_request_params=client_request_params
            )

        if not seed and private_key:
            address_data = self.generate_from_private_key(private_key, chain_id, version)
            return address_class(
                address_data["value"], private_key, address_data["public_key"], chain_id=address_data["chain_id"],
                node_address=self.node_address, online=online, client_request_params=client_request_params
            )

        if not seed and public_key:
            address_data = self.generate_from_public_key(public_key, chain_id, version)
            return address_class(
                address_data["value"], public_key=address_data["public_key"], chain_id=address_data["chain_id"],
                node_address=self.node_address, online=online, client_request_params=client_request_params
            )

        if seed:
            address_data = self.generate_from_seed(seed, chain_id, nonce, version)
            return address_class(
                address_data["value"], address_data["private_key"], address_data["public_key"], address_data["seed"],
                address_data["chain_id"], nonce, node_address=self.node_address, online=online,
                client_request_params=client_request_params
            )

        new_seed = self.generate_seed()
        address_data = self.generate_from_seed(new_seed, chain_id, nonce, version)
        return address_class(
            address_data["value"], address_data["private_key"], address_data["public_key"], address_data["seed"],
            address_data["chain_id"], nonce, node_address=self.node_address, online=online,
            client_request_params=client_request_params
        )

    def validate_address(self, value, private_key=None, public_key=None, chain_id=DEFAULT_CHAIN_ID, version=None):
        """
        Validate address. If address data is valid returns it else raises error

        :param value: address value
        :param chain_id: Acryl chain id
        :param private_key: address private key
        :param public_key: address public key
        :param version: address version
        :return: data for address object creation
        :rtype: dict
        :raises: ValueError
        """
        if private_key:
            address_data = self.generate_from_private_key(private_key, chain_id, version)
            if address_data["value"] != value:
                raise ValueError("Incorrect address for private key")

            if public_key:
                if address_data["public_key"] != public_key:
                    raise ValueError("Incorrect public key for private key")

            return address_data

        if public_key:
            address_data = self.generate_from_public_key(public_key, chain_id, version)
            if address_data["value"] != value:
                raise ValueError("Incorrect address for public key")

            return address_data

        raise ValueError('No private key or public key provided')

    def generate_from_private_key(self, private_key, chain_id, version):
        """
        Generate address from private key (address value, public key)

        :param private_key:
        :param chain_id:
        :return: data for address object creation
        :rtype: dict
        """
        decoded_private_key = base58.b58decode(private_key)
        public_key = axolotl_curve25519.generatePublicKey(decoded_private_key)
        raw_address = chr(version) + chain_id + self._hash_bytes(public_key)[0:20]
        address_digest = self._hash_bytes(raw_address.encode('latin-1'))[0:4]
        address_data = dict()
        address_data["value"] = base58.b58encode((raw_address + address_digest).encode('latin-1')).decode()
        address_data["public_key"] = base58.b58encode(public_key).decode()
        address_data["private_key"] = private_key
        address_data["chain_id"] = chain_id
        return address_data

    def generate_from_public_key(self, public_key, chain_id, version):
        """
        Generate address from public key (address value only)

        :param public_key: public key in base58
        :param chain_id: chain id
        :return: data for address object creation
        :rtype: dict
        """
        decoded_public_key = base58.b58decode(public_key)
        raw_address = chr(version) + chain_id + self._hash_bytes(decoded_public_key)[0:20]
        address_digest = self._hash_bytes(raw_address.encode('latin-1'))[0:4]
        address_data = dict()
        address_data["value"] = base58.b58encode((raw_address + address_digest).encode('latin-1')).decode()
        address_data["public_key"] = public_key
        address_data["chain_id"] = chain_id
        return address_data

    @classmethod
    def generate_from_seed(cls, seed, chain_id, nonce, version):
        """
        Generate address from seed (address value, private and public keys)

        :return: data for address object creation
        :rtype: dict
        """
        private_key = cls.generate_private_key(seed, nonce)
        public_key = axolotl_curve25519.generatePublicKey(private_key)
        raw_address = chr(version) + chain_id + cls._hash_bytes(public_key)[0:20]
        address_digest = cls._hash_bytes(raw_address.encode('latin-1'))[0:4]
        address_data = dict()
        address_data["value"] = base58.b58encode((raw_address + address_digest).encode('latin-1')).decode()
        address_data["public_key"] = base58.b58encode(public_key).decode()
        address_data["private_key"] = base58.b58encode(private_key).decode()
        address_data["seed"] = seed
        address_data["chain_id"] = chain_id
        return address_data

    @staticmethod
    def generate_seed(language=None, strength=None):
        """
        Generate seed

        :return: seed string
        :rtype: str
        """
        mnemonic_object = Mnemonic(language or "english")
        seed = mnemonic_object.generate(strength=strength or 160)
        return seed

    @classmethod
    def generate_private_key(cls, seed, nonce=0):
        """
        Generate private key from seed

        :param seed: seed value
        :param nonce: nonce value
        :return:
        """
        decoded_seed = seed.encode('latin-1')
        nonce_bytes = struct.pack(">L", nonce)
        seed_keccak_digest = cls._hash_bytes(nonce_bytes + decoded_seed)
        seed_sha256_hash = hashlib.sha256(seed_keccak_digest.encode('latin-1')).digest()
        private_key = axolotl_curve25519.generatePrivateKey(seed_sha256_hash)
        return private_key

    @staticmethod
    def _hash_bytes(bytes_object):
        """
        Hash bytes with BLAKE and KECCAK algorithms

        :param bytes_object: bytes to hash
        :type bytes_object: bytes
        :return: keccak hash digest
        :rtype
        """
        blake_digest = hashlib.blake2b(bytes_object, digest_size=32).digest()
        keccak_digest = sha3.keccak_256(blake_digest).digest().decode('latin-1')
        return keccak_digest

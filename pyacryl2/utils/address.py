"""
pyacryl2.utils.address
~~~~~~~~~~~~~~~~~~~~~~

Acryl address
"""

import base64
import json
import math
import struct
import time
from functools import wraps

import base58

from pyacryl2.client import DEFAULT_NODE_ADDRESS, AcrylClient, CHAIN_ID_NAMES
from pyacryl2.utils.crypto import sign_with_private_key


DEFAULT_ADDRESS_VERSION = 1

DEFAULT_TRANSFER_TRANSACTION_FEE = 100000
DEFAULT_LEASE_TRANSACTION_FEE = 100000
DEFAULT_ALIAS_TRANSACTION_FEE = 100000
DEFAULT_ISSUE_TRANSACTION_FEE = 100000000
DEFAULT_REISSUE_TRANSACTION_FEE = 100000000
DEFAULT_BURN_TRANSACTION_FEE = 100000
DEFAULT_MASS_TRANSFER_TRANSACTION_FEE = 100000
DEFAULT_CANCEL_LEASE_TRANSACTION_FEE = 100000
DEFAULT_SPONSORSHIP_TRANSACTION_FEE = 100000000
DEFAULT_SET_SCRIPT_TRANSACTION_FEE = 1000000
DEFAULT_SET_ASSET_SCRIPT_TRANSACTION_FEE = 100000000

TRANSACTION_TYPE_GENESIS = 1
TRANSACTION_TYPE_PAYMENT = 2
TRANSACTION_TYPE_ISSUE = 3
TRANSACTION_TYPE_TRANSFER = 4
TRANSACTION_TYPE_REISSUE = 5
TRANSACTION_TYPE_BURN = 6
TRANSACTION_TYPE_EXCHANGE = 7
TRANSACTION_TYPE_LEASE = 8
TRANSACTION_TYPE_CANCEL_LEASE = 9
TRANSACTION_TYPE_ALIAS = 10
TRANSACTION_TYPE_MASS_TRANSFER = 11
TRANSACTION_TYPE_DATA = 12
TRANSACTION_TYPE_SET_SCRIPT = 13
TRANSACTION_TYPE_SPONSORSHIP = 14
TRANSACTION_TYPE_SET_ASSET_SCRIPT = 15
TRANSACTION_TYPE_INVOKE_SCRIPT = 16

DATA_TRANSACTION_INT_TYPE = 0
DATA_TRANSACTION_BOOLEAN_TYPE = 1
DATA_TRANSACTION_STRING_TYPE = 2
DATA_TRANSACTION_BINARY_TYPE = 3

DEFAULT_TRANSACTION_VERSION = 1


def sign_required(method):
    """
    Decorator. Check if address can sign request data, if not then raises ValueError

    :param method: address class method
    :return: wrapped method
    :rtype: Callable
    :raises: ValueError
    """
    @wraps(method)
    def wrapper(*args, **kwargs):
        if not args[0].can_sign:
            raise ValueError("Can't sign request: address has not private key")

        return method(*args, **kwargs)
    return wrapper


class BaseAcrylAddress:
    """
    Base address class. Has methods for transaction data generation, common for child address classes 
    
    :param value: address text value in base58
    :param private_key: address private key string in base58
    :param public_key: address public key string in base58
    :param address_seed: address seed
    :param chain_id: address chain id
    :param nonce: nonce
    :param node_address: node API address for data retrieve and transaction broadcast
    :param version: address version (currently, only for information)
    :param online: make requests or return only request data
    :param client_request_params: client API request param (check API client doc)
    """
    
    def __init__(self, value=None, private_key=None, public_key=None, address_seed=None, chain_id=None, nonce=0,
                 node_address=DEFAULT_NODE_ADDRESS, version=DEFAULT_ADDRESS_VERSION, online=True,
                 client_request_params=None):
        self.value = value
        self.private_key = private_key
        self.public_key = public_key
        self.seed = address_seed
        self.chain_id = chain_id
        if not self.chain_id and self.value:
            self.chain_id = chr(base58.b58decode(self.value)[1])

        self.nonce = nonce
        self.node_address = node_address
        self.version = version
        self.online = online
        self.client_request_params = client_request_params
        self._api_client = None
        
    def save_as_json(self, file_path, encode_seed=False):
        """
        Save address data as json
        :param file_path: file path
        :param encode_seed: encode seed to base58
        :return: nothing
        :rtype: None
        """
        file_data = {
            "address": self.value, "private_key": self.private_key, "public_key": self.public_key,
            "seed": base58.b58encode(self.seed).decode() if encode_seed else self.seed, "chain_id": self.chain_id
        }
        with open(file_path, 'w') as json_file:
            json.dump(file_data, json_file)

    def load_from_json(self, file_path, decode_seed=False):
        """
        Get address data from json file
        :param file_path: file path
        :param decode_seed: decode seed from base58
        :return: nothing
        :rtype: None
        """
        with open(file_path, 'r') as json_file:
            file_data = json.load(json_file)

        self.value = file_data.get('address')
        self.private_key = file_data.get('private_key')
        self.public_key = file_data.get('public_key')
        self.seed = file_data.get('seed')
        if self.seed and decode_seed:
            self.seed = base58.b58decode(self.seed)

        self.chain_id = file_data.get('chain_id')
        
    def _generate_asset_sponsorship_transaction(self, asset_id, min_sponsored_asset_fee, transaction_fee, timestamp):
        """
        Prepare data for sponsorship transaction

        :param asset_id:
        :param min_sponsored_asset_fee:
        :param transaction_fee:
        :param timestamp:
        :return:
        """
        if timestamp == 0:
            timestamp_param = int(time.time() * 1000)
        else:
            timestamp_param = timestamp

        version = 1
        sign_data = [
            TRANSACTION_TYPE_SPONSORSHIP.to_bytes(1, 'big'),
            version.to_bytes(1, 'big'),
            base58.b58decode(self.public_key),
            base58.b58decode(asset_id),
            struct.pack(">Q", min_sponsored_asset_fee),
            struct.pack(">Q", transaction_fee),
            struct.pack(">Q", timestamp_param),
        ]
        signature = sign_with_private_key(self.private_key, b''.join(sign_data))

        transaction_data = {
            "type": TRANSACTION_TYPE_SPONSORSHIP,
            "version": version,
            "senderPublicKey": self.public_key,
            "assetId": asset_id,
            "fee": transaction_fee,
            "timestamp": timestamp_param,
            "minSponsoredAssetFee": min_sponsored_asset_fee,
            "proofs": [signature]
        }

        return transaction_data

    def _generate_alias_transaction(self, alias, transaction_fee, timestamp):
        """
        Prepare data for alias transaction

        :return:
        """
        if timestamp == 0:
            timestamp_param = int(time.time() * 1000)
        else:
            timestamp_param = timestamp

        alias_data = b''.join((
            b'\x02', self.chain_id.encode('latin-1'), struct.pack(">H", len(alias)), alias.encode('latin-1')
        ))
        sign_data = [
            TRANSACTION_TYPE_ALIAS.to_bytes(1, 'big'),
            base58.b58decode(self.public_key),
            struct.pack(">H", len(alias_data)),
            alias_data,
            struct.pack(">Q", transaction_fee),
            struct.pack(">Q", timestamp_param),
        ]

        signature = sign_with_private_key(self.private_key, b''.join(sign_data))

        transaction_data = {
            "senderPublicKey": self.public_key,
            "alias": alias,
            "fee": transaction_fee,
            "timestamp": timestamp_param,
            "signature": signature,
        }

        return transaction_data

    def _generate_transfer_transaction(self, recipient, asset_id, fee_asset_id, amount, attachment, transaction_fee,
                                       timestamp):
        """
        Prepare data for transfer transaction

        :param recipient:
        :param amount:
        :param attachment:
        :param transaction_fee:
        :param timestamp:
        :return:
        """
        if isinstance(recipient, AcrylAddress):
            recipient_address = recipient.value
        else:
            recipient_address = recipient

        if timestamp == 0:
            timestamp_param = int(time.time() * 1000)
        else:
            timestamp_param = timestamp

        if not attachment:
            encoded_attachment = b''
        else:
            encoded_attachment = attachment.encode('latin-1')

        if asset_id:
            asset_sign_data = b'\1%s' % base58.b58decode(asset_id)
        else:
            asset_sign_data = b'\0'

        if fee_asset_id:
            fee_asset_sign_data = b'\1%s' % base58.b58decode(fee_asset_id)
        else:
            fee_asset_sign_data = b'\0'

        sign_data = [
            TRANSACTION_TYPE_TRANSFER.to_bytes(1, 'big'),
            base58.b58decode(self.public_key),
            asset_sign_data,
            fee_asset_sign_data,
            struct.pack(">Q", timestamp_param),
            struct.pack(">Q", amount),
            struct.pack(">Q", transaction_fee),
            base58.b58decode(recipient_address),
            struct.pack(">H", len(b'' or encoded_attachment)),
            encoded_attachment
        ]

        signature = sign_with_private_key(self.private_key, b''.join(sign_data))
        transaction_data = {
            "senderPublicKey": self.public_key,
            "recipient": recipient_address,
            "amount": amount,
            "fee": transaction_fee,
            "timestamp": timestamp_param,
            "attachment": base58.b58encode(encoded_attachment).decode(),
            "signature": signature,
        }
        if asset_id:
            transaction_data["assetId"] = asset_id

        if fee_asset_id:
            transaction_data["feeAssetId"] = fee_asset_id

        return transaction_data

    def _generate_asset_issue_transaction(self, name, description, quantity, decimals, reissuable, transaction_fee,
                                          script, version, timestamp):
        """
        Prepare asset issue transaction data

        :param name:
        :param description:
        :param quantity:
        :param decimals:
        :param reissuable:
        :param version
        :param timestamp:
        :return:
        """
        if not timestamp:
            timestamp_param = int(time.time() * 1000)
        else:
            timestamp_param = timestamp

        sign_data = [
            TRANSACTION_TYPE_ISSUE.to_bytes(1, 'big'),
            base58.b58decode(self.public_key),
            struct.pack(">H", len(name)),
            name.encode('latin-1'),
            struct.pack(">H", len(description)),
            description.encode('latin-1'),
            struct.pack(">Q", quantity),
            struct.pack(">B", decimals),
            reissuable.to_bytes(1, 'big'),
            struct.pack(">Q", transaction_fee),
            struct.pack(">Q", timestamp_param)
        ]

        transaction_data = {
            "senderPublicKey": self.public_key,
            "name": name,
            "quantity": quantity,
            "timestamp": timestamp_param,
            "description": description,
            "decimals": decimals,
            "reissuable": reissuable,
            "fee": transaction_fee,
        }

        if version > 1:
            sign_data.insert(1, version.to_bytes(1, 'big'))
            sign_data.insert(2, self.chain_id.encode('latin-1'))
            transaction_data.update({
                "type": TRANSACTION_TYPE_ISSUE,
                "senderPublicKey": self.public_key,
                "version": version,
                "chainId": self.chain_id
            })

        if script:
            if version < 2:
                raise ValueError("Smart assets require at least 2 transaction version")

            compiled_script = base64.b64decode(script)
            sign_data.extend([
                b'\1',  # smart asset
                struct.pack(">H", len(compiled_script)),
                compiled_script
            ])
            transaction_data["script"] = 'base64:' + script
        else:
            if version >= 2:
                sign_data.append(b'\0')

        signature = sign_with_private_key(self.private_key, b''.join(sign_data))
        if version == 1:
            transaction_data["signature"] = signature
        else:
            transaction_data["proofs"] = [signature]

        return transaction_data

    def _generate_asset_reissue_transaction(self, asset_id, quantity, reissuable, transaction_fee, timestamp):
        """
        Prepare asset reissue transaction data

        :param asset_id:
        :param quantity:
        :param reissuable:
        :param timestamp:
        :return:
        """
        if timestamp == 0:
            timestamp_param = int(time.time() * 1000)
        else:
            timestamp_param = timestamp

        sign_data = [
            TRANSACTION_TYPE_REISSUE.to_bytes(1, 'big'),
            base58.b58decode(self.public_key),
            base58.b58decode(asset_id),
            struct.pack(">Q", quantity),
            reissuable.to_bytes(1, 'big'),
            struct.pack(">Q", transaction_fee),
            struct.pack(">Q", timestamp_param)
        ]

        signature = sign_with_private_key(self.private_key, b''.join(sign_data))
        transaction_data = {
            "senderPublicKey": self.public_key,
            "assetId": asset_id,
            "quantity": quantity,
            "timestamp": timestamp_param,
            "reissuable": reissuable,
            "fee": transaction_fee,
            "signature": signature
        }
        return transaction_data

    def _generate_asset_burn_transaction(self, asset_id, quantity, transaction_fee, timestamp):
        """
        Prepare asset reissue transaction data

        :param asset_id:
        :param quantity:
        :param reissuable:
        :param timestamp:
        :return:
        """
        if timestamp == 0:
            timestamp_param = int(time.time() * 1000)
        else:
            timestamp_param = timestamp

        sign_data = [
            TRANSACTION_TYPE_BURN.to_bytes(1, 'big'),
            base58.b58decode(self.public_key),
            base58.b58decode(asset_id),
            struct.pack(">Q", quantity),
            struct.pack(">Q", transaction_fee),
            struct.pack(">Q", timestamp_param)
        ]

        signature = sign_with_private_key(self.private_key, b''.join(sign_data))
        transaction_data = {
            "senderPublicKey": self.public_key,
            "assetId": asset_id,
            "quantity": quantity,
            "timestamp": timestamp_param,
            "fee": transaction_fee,
            "signature": signature
        }
        return transaction_data

    def _generate_data_transaction(self, data, version=1, timestamp=0):
        """
        Prepare data for data transaction

        :return:
        """
        if not timestamp:
            timestamp_param = int(time.time() * 1000)
        else:
            timestamp_param = timestamp

        data_buffer = []
        for item in data:
            key_encoded = item['key'].encode('latin-1')
            data_buffer.extend([struct.pack(">H", len(key_encoded)), key_encoded])
            if item['type'] == 'integer':
                item_value = [
                    DATA_TRANSACTION_INT_TYPE.to_bytes(1, 'big'),
                    struct.pack(">Q", item['value'])
                ]
            elif item['type'] == 'boolean':
                item_value = [
                    DATA_TRANSACTION_BOOLEAN_TYPE.to_bytes(1, 'big'),
                    item['value'].to_bytes(1, 'big')
                ]
            elif item['type'] == 'binary':
                item_value = [
                    DATA_TRANSACTION_STRING_TYPE.to_bytes(1, 'big'),
                    struct.pack(">H", len(item['value'])),
                    item['value']
                ]
                item['value'] = "base64:" + base64.b64encode(item['value']).decode('latin-1')

            elif item['type'] == 'string':
                item_value = [
                    DATA_TRANSACTION_BINARY_TYPE.to_bytes(1, 'big'),
                    struct.pack(">H", len(item['value'])),
                    item['value']
                ]
            else:
                raise ValueError("Unknown data type: '{}'".format(item['type']))

            data_buffer.extend(item_value)

        transaction_fee = int(math.floor(1 + (len(json.dumps(data)) + 8 - 1) / 1024) * 100000)
        sign_data = [
            TRANSACTION_TYPE_DATA.to_bytes(1, 'big'),
            version.to_bytes(1, 'big'),
            base58.b58decode(self.public_key),
            struct.pack(">H", len(data)),
            b''.join(data_buffer),
            struct.pack(">Q", timestamp_param),
            struct.pack(">Q", transaction_fee),
        ]
        transaction_data = {
            "type": TRANSACTION_TYPE_DATA,
            "version": version,
            "senderPublicKey": self.public_key,
            "data": data,
            "fee": transaction_fee,
            "timestamp": timestamp_param,
            "proofs": [sign_with_private_key(self.private_key, b''.join(sign_data))]
        }
        return transaction_data

    def _generate_lease_transaction(self, recipient, amount, transaction_fee, timestamp):
        """
        Prepare data for lease transaction

        :param recipient:
        :param amount:
        :param transaction_fee:
        :param timestamp:
        :return:
        """
        if isinstance(recipient, AcrylAddress):
            recipient_address = recipient.value
        else:
            recipient_address = recipient

        if timestamp == 0:
            timestamp_param = int(time.time() * 1000)
        else:
            timestamp_param = timestamp

        sign_data = [
            TRANSACTION_TYPE_LEASE.to_bytes(1, 'big'),
            base58.b58decode(self.public_key),
            base58.b58decode(recipient_address),
            struct.pack(">Q", amount),
            struct.pack(">Q", transaction_fee),
            struct.pack(">Q", timestamp_param),
        ]

        signature = sign_with_private_key(self.private_key, b''.join(sign_data))
        transaction_data = {
            "senderPublicKey": self.public_key,
            "recipient": recipient_address,
            "amount": amount,
            "fee": transaction_fee,
            "timestamp": timestamp_param,
            "signature": signature
        }

        return transaction_data

    def _generate_cancel_lease_transaction(self, transaction_id, transaction_fee, timestamp):
        """
        Prepare data for cancel lease transaction

        :param transaction_id:
        :param transaction_fee:
        :param timestamp:
        :return:
        """

        if timestamp == 0:
            timestamp_param = int(time.time() * 1000)
        else:
            timestamp_param = timestamp

        sign_data = [
            TRANSACTION_TYPE_CANCEL_LEASE.to_bytes(1, 'big'),
            base58.b58decode(self.public_key),
            struct.pack(">Q", transaction_fee),
            struct.pack(">Q", timestamp_param),
            base58.b58decode(transaction_id),
        ]

        signature = sign_with_private_key(self.private_key, b''.join(sign_data))
        transaction_data = {
            "senderPublicKey": self.public_key,
            "txId": transaction_id,
            "fee": transaction_fee,
            "timestamp": timestamp_param,
            "signature": signature
        }

        return transaction_data
    
    def _generate_mass_transfer_transaction(self, transfer_data, asset_id, attachment, version, timestamp):
        """
        Setup mass transfer transaction data

        :param transfer_data:
        :param attachment:
        :param timestamp:
        :return:
        """
        if not timestamp:
            timestamp_param = int(time.time() * 1000)
        else:
            timestamp_param = timestamp

        if not attachment:
            encoded_attachment = b''
        else:
            encoded_attachment = attachment.encode('latin-1')

        mass_fee = 100000 + math.ceil(0.5 * len(transfer_data)) * 100000

        recipients_sign_data = []
        for recipient_data in transfer_data:
            recipients_sign_data.append(base58.b58decode(recipient_data['recipient']))
            recipients_sign_data.append(struct.pack(">Q", recipient_data['amount']))

        sign_data = [
            TRANSACTION_TYPE_MASS_TRANSFER.to_bytes(1, 'big'),
            version.to_bytes(1, 'big'),
            base58.b58decode(self.public_key),
            b'\0',  # for default asset (Acryl)
            struct.pack(">H", len(transfer_data)),
            b''.join(recipients_sign_data),
            struct.pack(">Q", timestamp_param),
            struct.pack(">Q", mass_fee),
            struct.pack(">H", len(encoded_attachment)),
            encoded_attachment
        ]

        if asset_id:
            sign_data[3] = b'\1'
            sign_data.insert(4, base58.b58decode(asset_id))

        signature = sign_with_private_key(self.private_key, b''.join(sign_data))

        transaction_data = {
            "type": TRANSACTION_TYPE_MASS_TRANSFER,
            "version": 1,
            "assetId": asset_id or "",
            "senderPublicKey": self.public_key,
            "fee": mass_fee,
            "timestamp": timestamp_param,
            "transfers": transfer_data,
            "attachment": base58.b58encode(encoded_attachment).decode(),
            "signature": signature,
            "proofs": [
                signature
            ]
        }

        return transaction_data

    def _generate_set_script_transaction(self, script, transaction_fee, timestamp, version):
        """
        Generate set script transaction data

        :param script:
        :param transaction_fee:
        :return:
        """
        if not timestamp:
            timestamp_param = int(time.time() * 1000)
        else:
            timestamp_param = timestamp

        script_bytes = base64.b64decode(script)
        sign_data = [
            TRANSACTION_TYPE_SET_SCRIPT.to_bytes(1, 'big'),
            version.to_bytes(1, 'big'),
            self.chain_id.encode('latin-1'),
            base58.b58decode(self.public_key),
            b'\1',
            struct.pack(">H", len(script_bytes)),
            script_bytes,
            struct.pack(">Q", transaction_fee),
            struct.pack(">Q", timestamp_param),
        ]

        signature = sign_with_private_key(self.private_key, b''.join(sign_data))
        transaction_data = {
            "type": TRANSACTION_TYPE_SET_SCRIPT,
            "version": version,
            "senderPublicKey": self.public_key,
            "fee": transaction_fee,
            "timestamp": timestamp_param,
            "script": 'base64:' + script,
            "proofs": [signature]
        }

        return transaction_data

    def _generate_set_asset_script_transaction(self, script, asset_id, transaction_fee, timestamp, version):
        """
        Generate set script transaction data

        :param asset_id:
        :param script:
        :param transaction_fee:
        :return:
        """
        if not timestamp:
            timestamp_param = int(time.time() * 1000)
        else:
            timestamp_param = timestamp

        script_bytes = base64.b64decode(script)
        sign_data = [
            TRANSACTION_TYPE_SET_ASSET_SCRIPT.to_bytes(1, 'big'),
            version.to_bytes(1, 'big'),
            self.chain_id.encode('latin-1'),
            base58.b58decode(self.public_key),
            base58.b58decode(asset_id),
            struct.pack(">Q", transaction_fee),
            struct.pack(">Q", timestamp_param),
            b'\1',
            struct.pack(">H", len(script_bytes)),
            script_bytes,
        ]

        signature = sign_with_private_key(self.private_key, b''.join(sign_data))
        transaction_data = {
            "type": TRANSACTION_TYPE_SET_ASSET_SCRIPT,
            "version": version,
            "assetId": asset_id,
            "senderPublicKey": self.public_key,
            "fee": transaction_fee,
            "timestamp": timestamp_param,
            "script": 'base64:' + script,
            "proofs": [signature]
        }

        return transaction_data

    @property
    def can_sign(self):
        """
        Ability to sign requests

        :return: yes or no
        :rtype: bool
        """
        return bool(self.private_key)

    @property
    def chain(self):
        """
        Address chain name

        :return: chain name
        :rtype: str
        """
        chains_dict = dict(CHAIN_ID_NAMES)
        return chains_dict[self.chain_id]

    @property
    def client(self):
        """
        Current API client instance

        :return: API client instance
        """
        return self._api_client

    @property
    def base58_seed(self):
        """
        Seed encoded base58

        :return: seed in base58
        :rtype: bytes
        """
        return base58.b58encode(self.seed.encode('latin-1')).decode()
        

class AcrylAddress(BaseAcrylAddress):
    """
    Acryl address class. Simplifies transaction data generation and data requests

    :param value: address text value in base58
    :param private_key: address private key string in base58
    :param public_key: address public key string in base58
    :param address_seed: address seed
    :param chain_id: address chain id
    :param nonce: nonce
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_client = AcrylClient(
            node_address=self.node_address, chain_id=self.chain_id, online=self.online,
            request_params=self.client_request_params
        )

    def from_alias(self, alias):
        """
        Set address value from alias

        :param alias: alias of address
        :return: address object with address value
        """

        address_data = self._api_client.alias_by_alias(alias)
        address_bytes = base58.b58decode(address_data["address"])
        self.value = address_data["address"]
        self.private_key = None
        self.public_key = None
        self.seed = None
        self.chain_id = chr(address_bytes[1])
        self.nonce = None
        self.version = int(address_bytes[0])

    def get_balance(self):
        """
        Get address balance

        :return: balance value
        :rtype: int or dict
        """
        data = self._api_client.address_balance(self.value)
        if not self.online:
            return data

        return data["balance"]

    def get_effective_balance(self):
        """
        Get address effective balance

        :return: balance value
        :rtype: int or dict
        """
        data = self._api_client.address_effective_balance(self.value)
        if not self.online:
            return data

        return data["balance"]

    def get_confirmed_balance(self, confirmations):
        """
        Get address balance

        :return: balance value
        :rtype: int or dict
        """
        data = self._api_client.address_balance_confirmed(self.value, confirmations)
        if not self.online:
            return data

        return data["balance"]

    def get_assets(self):
        """
        Get address assets

        :return: asset balances in dict
        :rtype: int or dict
        """
        data = self._api_client.assets_balance(self.value)
        if not self.online:
            return data

        return data["balances"]

    def get_address_data(self):
        """
        Get address data from blockchain

        :return: data in dict
        :rtype: dict
        """
        data = self._api_client.address_data_address(self.value)
        if not self.online:
            return data

        return data

    def get_aliases(self, flat=True):
        """
        Get address aliases

        :param flat: get only alias names without chain ids
        :return: list of dicts with prefix, chain ids and alias names or only alias names
        :rtype: list or dict
        """
        aliases = []
        data = self._api_client.alias_by_address(self.value)
        if not self.online:
            return data

        for alias_data_string in data.response_data:
            prefix, chain_id, alias = alias_data_string.split(":")
            if flat:
                aliases.append(alias)
            else:
                aliases.append({"chain_id": chain_id, "alias": alias, "prefix": prefix})

        return aliases

    def validate(self):
        """
        Validate address
        :return:
        :rtype bool or dict
        """
        data = self._api_client.address_validate(self.value)
        if not self.online:
            return data

        return data["valid"]

    def get_address_info(self):
        """
        Collect address info (balances, assets, data)
        :return: address info dict
        :rtype: dict
        """
        address_info = dict()
        address_info["valid"] = self.validate()
        if not address_info["valid"]:
            return address_info

        address_info["balance"] = self.get_balance()
        address_info["effective_balance"] = self.get_effective_balance()
        address_info["assets"] = self.get_assets()
        address_info["address_data"] = self.get_address_data()
        return address_info

    @sign_required
    def data_transaction(self, data, version=DEFAULT_TRANSACTION_VERSION, timestamp=0):
        """
        Create data transaction

        :param data: data for data transaction (list of dicts with keys type, key, value)
            Suitable python types for transaction data types:
            - boolean - `bool`
            - binary - `bytes` (converts them to base64 string)
            - integer - `int`
            - string - `str`

        :type data: list
        :param version: data transaction version
        :type version: int
        :param timestamp: transaction timestamp
        :type timestamp: int
        :return: client request result
        :rtype: AcrylClientResponse or dict
        """
        transaction_data = self._generate_data_transaction(data, version, timestamp)
        result = self._api_client.transaction_broadcast(transaction_data)
        return result

    @sign_required
    def transfer_acryl(self, recipient, amount, attachment=None, transaction_fee=DEFAULT_TRANSFER_TRANSACTION_FEE,
                       timestamp=0):
        """
        Send acryl to address

        :param recipient: recipient address in base58
        :type recipient: str or AcrylAddress or AcrylAsyncAddress
        :param amount: amount of acryl
        :type amount: int
        :param attachment: attachment string
        :type attachment: str
        :param transaction_fee: fee for transfer transaction
        :type transaction_fee: int
        :param timestamp: timestamp of transaction
        :type timestamp: int
        :return: transfer result
        :rtype: AcrylClientResponse or dict
        """
        transaction_data = self._generate_transfer_transaction(
            recipient, None, None, amount, attachment, transaction_fee, timestamp
        )
        result = self._api_client.asset_broadcast_transfer(transaction_data)
        return result

    @sign_required
    def transfer_asset(self, recipient, asset_id, fee_asset_id, amount, attachment=None,
                       transaction_fee=DEFAULT_TRANSFER_TRANSACTION_FEE, timestamp=0):
        """
        Send asset to address. If asset_id or fee_asset_id is None then acryl will be used

        :param recipient: recipient address in base58
        :type recipient: str or AcrylAddress or AcrylAsyncAddress
        :param asset_id: asset id
        :type asset_id: str or None
        :param fee_asset_id: fee asset id
        :type fee_asset_id: str or None
        :param amount: amount of acryl
        :type amount: int
        :param attachment: attachment string
        :type attachment: str
        :param transaction_fee: fee for transfer transaction
        :type transaction_fee: int
        :param timestamp: timestamp of transaction
        :type timestamp: int
        :return: transfer result
        :rtype: AcrylClientResponse or dict
        """
        transaction_data = self._generate_transfer_transaction(
            recipient, asset_id, fee_asset_id, amount, attachment, transaction_fee, timestamp
        )
        result = self._api_client.asset_broadcast_transfer(transaction_data)
        return result

    @sign_required
    def mass_transfer_acryl(self, transfer_data, attachment=None, timestamp=None):
        """
        Mass transfer acryl

        :param transfer_data: list of dicts with recipient and amount i.e.
            `[{ 'recipient': '3N1xca2DY8AEwqRDAJpzUgY99eq8J9h4rB3', 'amount': 1000 }]`
        :param attachment: transaction attachment
        :param transaction_fee: mass transfer transaction fee
        :param timestamp: transaction timestamp
        :return:
        :rtype: AcrylClientResponse or dict
        """
        transaction_data = self._generate_mass_transfer_transaction(
            transfer_data, None, attachment, DEFAULT_TRANSACTION_VERSION, timestamp)

        result = self._api_client.transaction_broadcast(transaction_data)
        return result

    @sign_required
    def mass_transfer_assets(self, transfer_data, asset_id=None, attachment=None, version=DEFAULT_TRANSACTION_VERSION,
                             timestamp=None):
        """
        Mass transfer acryl

        :param transfer_data: list of dicts with recipient and amount i.e.
            `[{ 'recipient': '3N1xca2DY8AEwqRDAJpzUgY99eq8J9h4rB3', 'amount': 1000 }]`
        :param attachment: transaction attachment
        :param asset_id: ID of transferring asset
        :param timestamp: transaction timestamp
        :return:
        """
        transaction_data = self._generate_mass_transfer_transaction(
            transfer_data, asset_id, attachment, version, timestamp
        )
        result = self._api_client.transaction_broadcast(transaction_data)
        return result

    @sign_required
    def lease_acryl(self, recipient, amount, transaction_fee=DEFAULT_LEASE_TRANSACTION_FEE, timestamp=0):
        """
        Lease acryl to address

        :param recipient:
        :param amount:
        :param transaction_fee:
        :param timestamp:
        :return:
        """
        transaction_data = self._generate_lease_transaction(recipient, amount, transaction_fee, timestamp)
        result = self._api_client.leasing_broadcast_lease(transaction_data)
        return result

    @sign_required
    def lease_cancel(self, transaction_id, transaction_fee=DEFAULT_CANCEL_LEASE_TRANSACTION_FEE, timestamp=0):
        """
        Cancel acryl lease

        :param transaction_id:
        :param transaction_fee:
        :param timestamp:
        :return:
        """
        transaction_data = self._generate_cancel_lease_transaction(transaction_id, transaction_fee, timestamp)
        result = self._api_client.leasing_broadcast_cancel_lease(transaction_data)
        return result

    @sign_required
    def create_alias(self, alias, transaction_fee=DEFAULT_ALIAS_TRANSACTION_FEE, timestamp=0):
        """
        Create alias for address

        :param alias: alias (min 4, max 30 chars)
        :param transaction_fee:
        :param timestamp:
        :return:
        """
        transaction_data = self._generate_alias_transaction(alias, transaction_fee, timestamp)
        result = self._api_client.alias_broadcast_create(transaction_data)
        return result

    @sign_required
    def issue_asset(self, name, description, quantity, decimals, reissuable,
                    transaction_fee=DEFAULT_ISSUE_TRANSACTION_FEE, version=DEFAULT_TRANSACTION_VERSION, timestamp=0):
        """
        Issue asset in acryl blockchain

        :param name: asset name (min 4, max 16 chars)
        :param description: asset description
        :param quantity: asset quantity
        :param decimals: asset decimals
        :param reissuable: is asset reissuable
        :param transaction_fee: asset issue transaction fee
        :param version: transaction version
        :param timestamp: transaction timestamp
        :return:
        """
        transaction_data = self._generate_asset_issue_transaction(
            name, description, quantity, decimals, reissuable, transaction_fee, None, version, timestamp
        )
        if version == 1:
            result = self._api_client.asset_broadcast_issue(transaction_data)
        else:
            result = self._api_client.transaction_broadcast(transaction_data)

        return result

    @sign_required
    def issue_smart_asset(self, name, description, quantity, decimals, reissuable, script,
                          transaction_fee=DEFAULT_ISSUE_TRANSACTION_FEE, timestamp=0):
        """
        Issue smart asset in acryl blockchain (asset with script)

        :param name: asset name (min 4, max 16 chars)
        :param description: asset description
        :param quantity: asset quantity
        :param decimals: asset decimals
        :param reissuable: is asset reissuable
        :param transaction_fee: asset issue transaction fee
        :param timestamp: transaction timestamp
        :return:
        """
        transaction_data = self._generate_asset_issue_transaction(
            name, description, quantity, decimals, reissuable, transaction_fee, script, 2, timestamp
        )
        result = self._api_client.transaction_broadcast(transaction_data)
        return result

    @sign_required
    def reissue_asset(self, asset_id, quantity, reissuable, transaction_fee=DEFAULT_REISSUE_TRANSACTION_FEE,
                      timestamp=0):
        """
        Reissue asset in acryl blockchain

        :param asset_id: asset id
        :param quantity: asset quantity
        :param transaction_fee:
        :param timestamp: transaction timestamp
        :return:
        """
        transaction_data = self._generate_asset_reissue_transaction(
            asset_id, quantity, reissuable, transaction_fee, timestamp
        )
        result = self._api_client.asset_broadcast_reissue(transaction_data)
        return result

    @sign_required
    def burn_asset(self, asset_id, quantity, transaction_fee=DEFAULT_BURN_TRANSACTION_FEE, timestamp=0):
        """
        Burn asset

        :param asset_id: asset id
        :param quantity: asset quantity
        :param transaction_fee:
        :param timestamp: transaction timestamp
        :return:
        """
        transaction_data = self._generate_asset_burn_transaction(asset_id, quantity, transaction_fee, timestamp)
        result = self._api_client.asset_broadcast_burn(transaction_data)
        return result

    @sign_required
    def asset_sponsorship(self, asset_id, min_sponsored_asset_fee, transaction_fee=DEFAULT_SPONSORSHIP_TRANSACTION_FEE,
                          timestamp=0):
        """
        Sponsor asset

        :param asset_id:
        :param min_sponsored_asset_fee:
        :param transaction_fee:
        :param timestamp:
        :return:
        """
        transaction_data = self._generate_asset_sponsorship_transaction(
            asset_id, min_sponsored_asset_fee, transaction_fee, timestamp
        )
        result = self._api_client.transaction_broadcast(transaction_data)
        return result

    @sign_required
    def set_script(self, script, transaction_fee=DEFAULT_SET_SCRIPT_TRANSACTION_FEE, timestamp=None,
                   version=DEFAULT_TRANSACTION_VERSION):
        """
        Set script for account

        :param script:
        :param transaction_fee:
        :param timestamp:
        :param version:
        :return:
        """
        transaction_data = self._generate_set_script_transaction(script, transaction_fee, timestamp, version)
        result = self._api_client.transaction_broadcast(transaction_data)
        return result

    @sign_required
    def set_asset_script(self, script, asset_id, transaction_fee=DEFAULT_SET_ASSET_SCRIPT_TRANSACTION_FEE,
                         timestamp=None, version=DEFAULT_TRANSACTION_VERSION):
        """
        Set script for asset

        :param script:
        :param asset_id:
        :param transaction_fee:
        :param timestamp:
        :param version:
        :return:
        """
        transaction_data = self._generate_set_asset_script_transaction(
            script, asset_id, transaction_fee, timestamp, version
        )
        result = self._api_client.transaction_broadcast(transaction_data)
        return result

    def __repr__(self):
        return "AcrylAddress({})".format(self.value)

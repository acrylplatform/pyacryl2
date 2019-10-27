"""
pyacryl2.client
~~~~~~~~~~~~~~~~

This module provides API client class
"""
import logging
from urllib.parse import urljoin

import requests


DEFAULT_NODE_ADDRESS = 'https://nodes.acrylplatform.com'
DEFAULT_MATCHER_ADDRESS = 'https://matcher.acrylplatform.com'
DEFAULT_CHAIN_ID = "A"
CHAIN_ID_NAMES = (('A', 'mainnet'), ('K', 'testnet'))
DEFAULT_HEADERS = (('user-agent', 'pyacryl2-client'),)

client_logger = logging.getLogger('pyacryl2.AcrylClient')


class AcrylClientException(Exception):
    """Exception for Acryl client"""


class AcrylClientResponse:
    """
    API client response. Any API method of `AcrylClient` returns `AcrylClientResponse` with response data or error
    (if raise_exception is False)

    :param successful: is request was successful
    :param response_data: data, returned in response
    :param error_code: error code in response (key "code")
    :param error_message: error message in response (key "message" if response has json else response body as text)
    """

    def __init__(self, successful, endpoint, response_data=None, error_code=None, error_message=None):
        self.successful = successful
        self.endpoint = endpoint
        self.response_data = response_data
        self.error_code = error_code
        self.error_message = error_message

    def __getitem__(self, item):
        if item not in self.response_data:
            raise KeyError("key '{}' not found in response data".format(item))

        return self.response_data[item]

    def __setitem__(self, key, value):
        self.response_data["key"] = value

    def __iter__(self):
        return iter(self.response_data)

    def __repr__(self):
        repr_string = "<{}(successfull={}, response_data={}, error_code={}, error_message={})>".format(
            self.__class__.__name__, self.successful, self.response_data, self.error_code, self.error_message
        )
        return repr_string

    def __bool__(self):
        return self.successful


class BaseClient:
    """
    Base class for API clients

    :param node_address: node url
    :type node_address: str
    :param matcher_address: node url
    :type matcher_address: str
    :param chain_id: chain id
    :type chain_id: str
    :param api_key: API key for private methods
    :type api_key: str
    :param raise_exception: raise AcrylClientException on request error
    :type raise_exception: bool
    :param request_params: request params dict e.g. timeout, proxies. May vary by client, see client lib docs
    :type request_params: dict
    :param online: send requests to node if true, else return prepared request with data
    :type online: bool
    """

    def __init__(self, node_address=DEFAULT_NODE_ADDRESS, matcher_address=DEFAULT_MATCHER_ADDRESS, chain_id=None,
                 api_key=None, raise_exception=True, request_params=None, online=True):
        self.node_address = node_address
        self.matcher_address = matcher_address
        self.chain_id = chain_id
        self.api_key = api_key
        self.raise_exception = raise_exception
        self.request_params = request_params
        self.online = online
        self.session = None

    def _setup_request_params(self, endpoint, params=None, data=None, json_data=None, headers=None, matcher=False):
        """
        Create request params for requests session
        :param endpoint: API endpoint
        :param params: request params
        :param data: request data
        :param json_data: request json data
        :param headers: request headers
        :param matcher: matcher request
        :return: dict of request params suitable for requests method function
        :rtype: dict
        """
        if matcher:
            request_url = urljoin(self.matcher_address, endpoint)
        else:
            request_url = urljoin(self.node_address, endpoint)

        request_headers = dict(DEFAULT_HEADERS)

        if self.api_key:
            request_headers['X-API-KEY'] = self.api_key

        if headers:
            request_headers.update(headers)

        request_params = dict()
        if self.request_params:
            request_params.update(self.request_params)

        request_params.update({'url': request_url, 'headers': request_headers})
        if params:
            request_params["params"] = params

        if data:
            request_params["data"] = data

        if json_data:
            request_params["json"] = json_data

        return request_params


class AcrylClient(BaseClient):
    """
    Acryl API client class based on `requests` HTTP client
    Class method names usually consist of a API endpoint, like `/blocks/height` is `blocks_height` or
    `/utils/seed/{length}` is `utils_seed_length`, also HTTP methods may affect class method name like
    `POST /address` is `address_create` or `DELETE /address` is address_delete.
    Check out node API documentation at https://nodes.acrylplatform.com/api-docs/index.html
    """

    # Node API methods

    def address_data_key(self, address, key):
        """
        Get address data by key

        :param address: address in base58
        :param key: string key
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/addresses/data/{}/{}'.format(address, key))

    def address_script_info(self, address):
        """
        Get address script info

        :param address: address in base58
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/addresses/scriptInfo/{}'.format(address))

    def address_delete(self, address):
        """
        Delete address from node

        :param address: address in base58
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('delete', '/addresses/{}'.format(address))

    def address_sign_text(self, address, message):
        """
        Sign text

        :param address:
        :param message: message string
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/addresses/signText/{}'.format(address), data=message)

    def address_verify_text(self, address, message_data):
        """
        Verify text

        :param address:
        :param message_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/addresses/verifyText/{}'.format(address), json_data=message_data)

    def address_balance_details(self, address):
        """
        Get address details

        :param address:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/addresses/balance/details/{}'.format(address))

    def address_balance_confirmed(self, address, confirmations):
        """
        Get confirmed address balance

        :param address:
        :param confirmations:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/addresses/balance/{}/{}'.format(address, confirmations))

    def address_effective_balance_confirmed(self, address, confirmations):
        """
        Get confirmed address effective balance

        :param address:
        :param confirmations:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/addresses/effectiveBalance/{}/{}'.format(address, confirmations))

    def address_data(self, address_data):
        """
        Set address data

        :param address_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/addresses/data', json_data=address_data)

    def address_seed(self, address):
        """
        Get address seed

        :param address:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/addresses/seed/{}'.format(address))

    def address_validate(self, address):
        """
        Validate address
        :param address:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/addresses/validate/{}'.format(address))

    def address_balance(self, address):
        """
        Address acryl balance
        :param address:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/addresses/balance/{}'.format(address))

    def address_effective_balance(self, address):
        """
        Address effective balance
        :param address:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/addresses/effectiveBalance/{}'.format(address))

    def address_public_key(self, public_key):
        """
        Get address by public key
        :param public_key:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/addresses/publicKey/{}'.format(public_key))

    def address_data_address(self, address, matches=None):
        """
        Get full address data
        :param address:
        :return:
        :rtype: AcrylClientResponse
        """
        params = dict()
        if matches:
            params['matches'] = matches

        return self.request('get', '/addresses/data/{}'.format(address), params=params)

    def addresses(self):
        """
        Get node addresses
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/addresses')

    def address_create(self):
        """
        Create node address

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/addresses')

    def addresses_sequence(self, address_from, address_to):
        """
        Get address sequence

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/addresses/seq/{}/{}'.format(address_from, address_to))

    def blocks_checkpoint(self, checkpoint_data):
        """
        Get blocks checkpoint

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/blocks/checkpoint', json_data=checkpoint_data)

    def blocks_height(self):
        """
        Get node blockchain height

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/blocks/height')

    def blocks_height_signature(self, block_signature):
        """
        Get signature of block at height

        :param block_signature:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/blocks/height/{}'.format(block_signature))

    def blocks_headers_at(self, block_height):
        """
        Get headers of block at height

        :param block_height:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/blocks/headers/at/{}'.format(block_height))

    def blocks_headers_sequence(self, height_from, height_to):
        """
        Get headers of blocks at heights

        :param height_from:
        :param height_to:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/blocks/headers/seq/{}/{}'.format(height_from, height_to))

    def blocks_headers_last(self):
        """
        Last block headers

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/blocks/headers/last')

    def blocks_signature(self, signature):
        """
        Get block by signature

        :param signature:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/blocks/signature/{}'.format(signature))

    def blocks_first(self):
        """
        Get first block

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/blocks/first')

    def blocks_delay(self, signature, block_number):
        """
        Get blocks delay by signature and block number

        :param signature:
        :param block_number:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/blocks/delay/{}/{}'.format(signature, block_number))

    def blocks_last(self):
        """
        Get last block

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/blocks/last')

    def blocks_address(self, address, height_from, height_to):
        """
        Get blocks generated by address

        :param address:
        :param height_from:
        :param height_to:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/blocks/address/{}/{}/{}'.format(address, height_from, height_to))

    def blocks_child(self, block_signature):
        """
        Get successor of specified block

        :param block_signature:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/blocks/child/{}'.format(block_signature))

    def blocks_at(self, height):
        """
        Get block at height

        :param height:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/blocks/at/{}'.format(height))

    def consensus_generating_balance_address(self, address):
        """
        Get address generating balance

        :param address:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/consensus/generatingbalance/{}'.format(address))

    def consensus_generation_signature_block(self, signature, block_id):
        """
        Get generation signature of a block with specified id

        :param signature:
        :param block_id:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/consensus/generationsignature/{}/{}'.format(signature, block_id))

    def consensus_generation_signature(self):
        """
        Get generation signature of a last block

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/consensus/generationsignature')

    def consensus_base_target_block(self, block_id):
        """
        Get consensus base target block

        :param block_id:
        :return:
        """
        return self.request('get', '/consensus/basetarget/{}'.format(block_id))

    def consensus_base_target(self):
        """
        Get consensus base target

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/consensus/basetarget')

    def consensus_algo(self):
        """
        Get consensus algorithm
        :return:
        """
        return self.request('get', '/consensus/algo')

    def activation_status(self):
        """
        Get node activation status

        :return:
        """
        return self.request('get', '/activation/status')

    def utils_script_estimate(self, code):
        """
        Estimate compiled script

        :param code:
        :return:
        """
        return self.request('post', '/utils/script/estimate', data=code)

    def utils_seed(self):
        """
        Generate random seed on node
        :return:
        """
        return self.request('get', '/utils/seed')

    def utils_hash_secure(self, message):
        """
        Get SecureCryptographicHash for message

        :param message:
        :return:
        """
        return self.request('post', '/utils/hash/secure', data=message)

    def utils_hash_fast(self, message):
        """
        Get FastCryptographicHash for message

        :param message:
        :return:
        """
        return self.request('post', '/utils/hash/fast', data=message)

    def utils_transaction_serialize(self, transaction_data):
        """
        Serialize transaction

        :param transaction_data:
        :return:
        """
        return self.request('post', '/utils/transactionSerialize', json_data=transaction_data)

    def utils_seed_length(self, length):
        """
        Generate random seed of specified length on node

        :param length:
        :return:
        """
        return self.request('get', '/utils/seed/{}'.format(length))

    def utils_script_compile(self, code):
        """
        Compile string code (deprecated on node version 1.0 and higher)

        :param code:
        :return:
        """
        return self.request('post', '/utils/script/compile', data=code)

    def utils_time(self):
        """
        Get node time

        :return:
        """
        return self.request('get', '/utils/time')

    def alias_broadcast_create(self, transaction_data):
        """
        Create alias

        :param transaction_data:
        :return:
        """
        return self.request('post', '/alias/broadcast/create', json_data=transaction_data)

    def alias_by_address(self, address):
        """
        Get alias by address

        :param address: acryl address
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/alias/by-address/{}'.format(address))

    def alias_by_alias(self, alias):
        """
        Get address by alias

        :param alias: alias (without preifx and chain id)
        :type alias: str
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/alias/by-alias/{}'.format(alias))

    def asset_broadcast_transfer(self, transfer_data):
        """
        Broadcast asset transfer transaction (v1)

        :param transfer_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/assets/broadcast/transfer', json_data=transfer_data)

    def asset_broadcast_issue(self, transaction_data):
        """
        Issue asset (v1)

        :param transaction_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/assets/broadcast/issue', json_data=transaction_data)

    def asset_broadcast_reissue(self, transaction_data):
        """
        Reissue asset (transaction v1)

        :param transaction_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/assets/broadcast/reissue', json_data=transaction_data)

    def asset_broadcast_burn(self, transaction_data):
        """
        Burn asset (v1)

        :param transaction_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/assets/broadcast/burn', json_data=transaction_data)

    def assets_balance(self, address):
        """
        Get assets balance

        :param address:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/assets/balance/{}'.format(address))

    def assets_nft_balance(self, address, limit, after=None):
        """
        Get NFT balance (node version 1.0 and higher)

        :param address:
        :param limit:
        :param after:
        :return:
        :rtype: AcrylClientResponse
        """
        params = dict()
        if after:
            params["after"] = after

        return self.request('get', '/assets/nft/{}/limit/{}'.format(address, limit), params=params)

    def assets_balance_asset(self, address, asset_id):
        """
        Get asset balance

        :param address:
        :param asset_id:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/assets/balance/{}/{}'.format(address, asset_id))

    def asset_distribution_at_height(self, asset_id, height, limit):
        """
        Get asset distribution at height

        :param asset_id:
        :param height:
        :param limit:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/assets/{}/distribution/{}/limit/{}'.format(asset_id, height, limit))

    def assets_details(self, asset_id, full=None):
        """
        Get asset details

        :param asset_id:
        :param full:
        :return:
        :rtype: AcrylClientResponse
        """
        params = dict()
        if full is not None:
            params["full"] = full

        return self.request('get', '/assets/details/{}'.format(asset_id), params=params)

    def leasing_active(self, address):
        """
        Get active leasing

        :param address:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/leasing/active/{}'.format(address))

    def leasing_broadcast_lease(self, transaction_data):
        """
        Create lease transaction

        :param transaction_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/leasing/broadcast/lease', json_data=transaction_data)

    def leasing_broadcast_cancel_lease(self, transaction_data):
        """
        Create cancel lease transaction

        :param transaction_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/leasing/broadcast/cancel', json_data=transaction_data)

    def peers_connected(self):
        """
        Get connected peer list

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/peers/connected')

    def peers_clear_blacklist(self):
        """
        Clear peers blacklist

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/peers/clearblacklist')

    def peers_blacklisted(self):
        """
        Get blacklisted peers

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/peers/blacklisted')

    def peers_suspended(self):
        """
        Get suspended peers

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/peers/suspended')

    def peers_connect(self, peer_data):
        """
        Connect to peer

        :param peer_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/peers/connect', json_data=peer_data)

    def transaction_broadcast(self, transaction_data):
        """
        Broadcast new transaction

        :param transaction_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/transactions/broadcast', json_data=transaction_data)

    def transaction_unconfirmed(self):
        """
        Get unconfirmed transactions

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/transactions/unconfirmed')

    def transaction_unconfirmed_size(self):
        """
        Get size of unconfirmed transactions

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/transactions/unconfirmed/size')

    def transaction_unconfirmed_info(self, transaction_id):
        """
        Get unconfirmed transaction info

        :param transaction_id:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/transactions/unconfirmed/info/{}'.format(transaction_id))

    def transaction_calculate_fee(self, transaction_data):
        """
        Calculate transaction fee

        :param transaction_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/transactions/calculateFee', json_data=transaction_data)

    def transaction_sign_address(self, signer_address, transaction_data):
        """
        Sign address transaction

        :param signer_address:
        :param transaction_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/transactions/sign/{}'.format(signer_address), json_data=transaction_data)

    def transactions_address(self, address, limit, after=None):
        """
        Get address transactions

        :param address: Acryl address
        :param limit: transaction limit
        :param after: show transactions after transaction id
        :return:
        :rtype: AcrylClientResponse
        """
        params = dict()
        if after:
            params["after"] = after

        return self.request('get', '/transactions/address/{}/limit/{}'.format(address, limit), params=params)

    def transaction_info(self, transaction_id):
        """
        Get transaction info

        :param transaction_id:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/transactions/info/{}'.format(transaction_id))

    def transaction_sign(self, transaction_data):
        """
        Sign transaction

        :param transaction_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/transactions/sign', json_data=transaction_data)

    def node_status(self):
        """
        Get node status

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/node/status')

    def node_stop(self):
        """
        Stop node

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/node/stop')

    def node_version(self):
        """
        Get node version

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/node/version')

    # Matcher endpoints

    def matcher(self):
        """
        Get matcher public key

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/matcher', matcher=True)

    def matcher_orderbook(self):
        """
        Get trading markets

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/matcher/orderbook', matcher=True)

    def matcher_order_create(self, order_data):
        """
        Create order

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/matcher/orderbook', json_data=order_data, matcher=True)

    def matcher_settings(self):
        """
        Get matcher settings

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/matcher/settings', matcher=True)

    def matcher_orderbook_remove(self, amount_asset_id, price_asset_id):
        """
        Remove orderbook for asset pair

        :param amount_asset_id:
        :param price_asset_id:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request(
            'delete', '/matcher/orderbook/{}/{}'.format(amount_asset_id, price_asset_id), matcher=True
        )

    def matcher_v1_orderbook_get_asset_pair(self, amount_asset_id, price_asset_id, depth=None):
        """
        Get orderbook for asset pair (API v1)

        :param amount_asset_id:
        :param price_asset_id:
        :param depth:
        :return:
        :rtype: AcrylClientResponse
        """
        params = dict()
        if depth:
            params["after"] = depth

        return self.request(
            'get', '/api/v1/orderbook/{}/{}'.format(amount_asset_id, price_asset_id), params=params, matcher=True
        )

    def matcher_orderbook_get_asset_pair_status(self, amount_asset_id, price_asset_id):
        """
        Get orderbook status for asset pair

        :param amount_asset_id:
        :param price_asset_id:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request(
            'get', '/matcher/orderbook/{}/{}/status'.format(amount_asset_id, price_asset_id), matcher=True
        )

    def matcher_orderbook_history(self, public_key):
        """
        Get orderbook history for a public key

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/matcher/orderbook/{}'.format(public_key), matcher=True)

    def matcher_orders_cancel_order(self, order_id, transaction_data):
        """
        Cancel order by id

        :param order_id:
        :param transaction_data:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request(
            'post', '/matcher/orders/cancel/{}'.format(order_id), json_data=transaction_data, matcher=True
        )

    def matcher_orders_cancel_order_without_signature(self, order_id):
        """
        Cancel order with API key

        :param order_id:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('post', '/matcher/orders/cancel/{}'.format(order_id), matcher=True)

    def matcher_orders_address(self, address):
        """
        Get address order history for an address

        :param address:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/matcher/orders/{}'.format(address))

    def matcher_orderbook_tradable_balance(self, amount_asset, price_asset, address):
        """
        Get tradable balance for asset pair

        :param amount_asset:
        :param price_asset:
        :param address:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request(
            'get', '/matcher/orderbook/{}/{}/tradableBalance/{}'.format(amount_asset, price_asset, address)
        )

    def matcher_balance_reserved(self, public_key):
        """
        Get reserved balance of open orders

        :param public_key:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/matcher/balance/reserved/{}'.format(public_key))

    def matcher_order_status(self, amount_asset, price_asset, order_id):
        """
        Get order status for asset pair

        :param amount_asset:
        :param price_asset:
        :param order_id:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/matcher/orderbook/{}/{}/{}'.format(amount_asset, price_asset, order_id))

    def matcher_transactions_order(self, order_id):
        """
        Get exchange transactions created on DEX for the given order

        :param order_id:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/matcher/transactions/{}'.format(order_id))

    def matcher_settings_rates(self):
        """
        Get matcher rates in Acryl

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/matcher/settings/rates')

    def matcher_debug_last_offset(self):
        """
        TODO:

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/matcher/debug/lastOffset')

    def matcher_debug_current_offset(self):
        """
        TODO:

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/matcher/debug/currentOffset')

    def matcher_debug_all_snapshot_offsets(self):
        """
        TODO:

        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('get', '/matcher/debug/allSnapshotOffsets')

    def matcher_set_asset_rate(self, asset_id, rate):
        """
        TODO:

        :param asset_id:
        :param rate:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('put', '/matcher/settings/rates/{}'.format(asset_id), data=rate)

    def matcher_delete_asset_rate(self, asset_id):
        """
        TODO:

        :param asset_id:
        :return:
        :rtype: AcrylClientResponse
        """
        return self.request('delete', '/matcher/settings/rates/{}'.format(asset_id))

    # Node API request maker

    def request(self, method, endpoint, params=None, data=None, json_data=None, headers=None, matcher=False):
        """
        Make a request to API

        :param method: HTTP method
        :param endpoint: API endpoint
        :param params: query params
        :param data: body data
        :param json_data: body data in json
        :param headers: HTTP headers
        :param matcher: matcher request
        :return: handled result if online else request params dict
        :rtype: AcrylClientResponse or dict
        """
        request_params = self._setup_request_params(endpoint, params, data, json_data, headers, matcher)
        if not self.online:
            client_logger.debug("Offline request '{}'".format(endpoint))
            return request_params

        close_session = False
        if not self.session:
            self.session = requests.Session()
            close_session = True

        try:
            request_method = getattr(self.session, method)
            client_logger.debug("Requesting '{}'".format(endpoint))
            response = request_method(**request_params)
        finally:
            client_logger.debug("Finished request '{}'".format(endpoint))
            if self.session and close_session:
                self.session.close()
                self.session = None

        result = self._handle_response(response, endpoint)
        return result

    def _handle_response(self, response, endpoint):
        """
        Handle requests response object. If client attribute `raise_exception` is True, then client error will be raised

        :param response: requests response object
        :return: client response object
        :rtype: AcrylClientResponse
        :raises: AcrylClientException
        """
        if not response.ok:
            try:
                error_data = response.json()
            except ValueError:
                error_code = None
                error_message = response.text
            else:
                error_code = error_data.get('code')
                error_message = error_data.get('message')

            if self.raise_exception:
                raise AcrylClientException(
                    "HTTP error code {}, error text: {}".format(response.status_code, error_message)
                )

            return AcrylClientResponse(
                successful=False, endpoint=endpoint, error_code=error_code, error_message=error_message
            )

        try:
            result = response.json()
        except ValueError:
            result = response.text

        return AcrylClientResponse(successful=True, endpoint=endpoint, response_data=result)

    def start_session(self):
        """
        Create requests session

        :return: nothing
        :rtype: None
        """
        self.session = requests.Session()
        client_logger.debug("Started session")

    def close_session(self):
        """
        Close requests session

        :return: nothing
        :rtype: None
        """
        client_logger.debug("Closing session")
        self.session.close()
        self.session = None
        client_logger.debug("Session closed")

    def __enter__(self):
        self.start_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_session()


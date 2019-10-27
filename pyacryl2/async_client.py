"""
pyacryl2.async_client
~~~~~~~~~~~~~~~~~~~~~

This module provides async API client class
"""
import logging

import ujson

from aiohttp import ClientSession, ContentTypeError

from pyacryl2.client import AcrylClientException, AcrylClientResponse, BaseClient


acryl_client_logger = logging.getLogger('pyacryl2.AcrylClient')


class AcrylAsyncClientResponse(AcrylClientResponse):
    """Async API client response"""


class AcrylAsyncClientException(AcrylClientException):
    """Exception for async acryl client"""


class AcrylAsyncClient(BaseClient):
    """
    Acryl async API client class based on `aiohttp.client`
    """

    _default_session_args = {'json_serialize': ujson.dumps}

    async def address_data_key(self, address, key):
        """
        Get address data by key

        :param address: address in base58
        :param key: string key
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/addresses/data/{}/{}'.format(address, key))

    async def address_script_info(self, address):
        """
        Get address script info

        :param address: address in base58
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/addresses/scriptInfo/{}'.format(address))

    async def address_delete(self, address):
        """
        Delete address from node

        :param address: address in base58
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('delete', '/addresses/{}'.format(address))

    async def address_sign_text(self, address, message):
        """
        Sign text

        :param address:
        :param message: message string
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/addresses/signText/{}'.format(address), data=message)

    async def address_verify_text(self, address, message_data):
        """
        Verify text

        :param address:
        :param message_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/addresses/verifyText/{}'.format(address), json_data=message_data)

    async def address_balance_details(self, address):
        """
        Get address details

        :param address:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/addresses/balance/details/{}'.format(address))

    async def address_balance_confirmed(self, address, confirmations):
        """
        Get confirmed address balance

        :param address:
        :param confirmations:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/addresses/balance/{}/{}'.format(address, confirmations))

    async def address_effective_balance_confirmed(self, address, confirmations):
        """
        Get confirmed address effective balance

        :param address:
        :param confirmations:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/addresses/effectiveBalance/{}/{}'.format(address, confirmations))

    async def address_data(self, address_data):
        """
        Set address data

        :param address_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/addresses/data', json_data=address_data)

    async def address_seed(self, address):
        """
        Get address seed

        :param address:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/addresses/seed/{}'.format(address))

    async def address_validate(self, address):
        """
        Validate address
        :param address:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/addresses/validate/{}'.format(address))

    async def address_balance(self, address):
        """
        Address acryl balance
        :param address:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/addresses/balance/{}'.format(address))

    async def address_effective_balance(self, address):
        """
        Address effective balance
        :param address:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/addresses/effectiveBalance/{}'.format(address))

    async def address_public_key(self, public_key):
        """
        Get address by public key
        :param public_key:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/addresses/publicKey/{}'.format(public_key))

    async def address_data_address(self, address, matches=None):
        """
        Get full address data
        :param address:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        params = dict()
        if matches:
            params['matches'] = matches

        return await self.request('get', '/addresses/data/{}'.format(address), params=params)

    async def addresses(self):
        """
        Get node addresses
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/addresses')

    async def address_create(self):
        """
        Create node address

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/addresses')

    async def addresses_sequence(self, address_from, address_to):
        """
        Get address sequence

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/addresses/seq/{}/{}'.format(address_from, address_to))

    async def blocks_checkpoint(self, checkpoint_data):
        """
        Get blocks checkpoint

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/blocks/checkpoint', json_data=checkpoint_data)

    async def blocks_height(self):
        """
        Get node blockchain height

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/blocks/height')

    async def blocks_height_signature(self, block_signature):
        """
        Get signature of block at height

        :param block_signature:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/blocks/height/{}'.format(block_signature))

    async def blocks_headers_at(self, block_height):
        """
        Get headers of block at height

        :param block_height:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/blocks/headers/at/{}'.format(block_height))

    async def blocks_headers_sequence(self, height_from, height_to):
        """
        Get headers of blocks at heights

        :param height_from:
        :param height_to:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/blocks/headers/seq/{}/{}'.format(height_from, height_to))

    async def blocks_headers_last(self):
        """
        Last block headers

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/blocks/headers/last')

    async def blocks_signature(self, signature):
        """
        Get block by signature

        :param signature:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/blocks/signature/{}'.format(signature))

    async def blocks_first(self):
        """
        Get first block

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/blocks/first')

    async def blocks_delay(self, signature, block_number):
        """
        Get blocks delay by signature and block number

        :param signature:
        :param block_number:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/blocks/delay/{}/{}'.format(signature, block_number))

    async def blocks_last(self):
        """
        Get last block

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/blocks/last')

    async def blocks_address(self, address, height_from, height_to):
        """
        Get blocks generated by address

        :param address:
        :param height_from:
        :param height_to:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/blocks/address/{}/{}/{}'.format(address, height_from, height_to))

    async def blocks_child(self, block_signature):
        """
        Get successor of specified block

        :param block_signature:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/blocks/child/{}'.format(block_signature))

    async def blocks_at(self, height):
        """
        Get block at height

        :param height:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/blocks/at/{}'.format(height))

    async def consensus_generating_balance_address(self, address):
        """
        Get address generating balance

        :param address:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/consensus/generatingbalance/{}'.format(address))

    async def consensus_generation_signature_block(self, signature, block_id):
        """
        Get generation signature of a block with specified id

        :param signature:
        :param block_id:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/consensus/generationsignature/{}/{}'.format(signature, block_id))

    async def consensus_generation_signature(self):
        """
        Get generation signature of a last block

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/consensus/generationsignature')

    async def consensus_base_target_block(self, block_id):
        """
        Get consensus base target block

        :param block_id:
        :return:
        """
        return await self.request('get', '/consensus/basetarget/{}'.format(block_id))

    async def consensus_base_target(self):
        """
        Get consensus base target

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/consensus/basetarget')

    async def consensus_algo(self):
        """
        Get consensus algorithm
        :return:
        """
        return await self.request('get', '/consensus/algo')

    async def activation_status(self):
        """
        Get node activation status

        :return:
        """
        return await self.request('get', '/activation/status')

    async def utils_script_estimate(self, code):
        """
        Estimate compiled script

        :param code:
        :return:
        """
        return await self.request('post', '/utils/script/estimate', data=code)

    async def utils_seed(self):
        """
        Generate random seed on node
        :return:
        """
        return await self.request('get', '/utils/seed')

    async def utils_hash_secure(self, message):
        """
        Get SecureCryptographicHash for message

        :param message:
        :return:
        """
        return await self.request('post', '/utils/hash/secure', data=message)

    async def utils_hash_fast(self, message):
        """
        Get FastCryptographicHash for message

        :param message:
        :return:
        """
        return await self.request('post', '/utils/hash/fast', data=message)

    async def utils_transaction_serialize(self, transaction_data):
        """
        Serialize transaction

        :param transaction_data:
        :return:
        """
        return await self.request('post', '/utils/transactionSerialize', json_data=transaction_data)

    async def utils_seed_length(self, length):
        """
        Generate random seed of specified length on node

        :param length:
        :return:
        """
        return await self.request('get', '/utils/seed/{}'.format(length))

    async def utils_script_compile(self, code):
        """
        Compile string code (deprecated on node version 1.0 and higher)

        :param code:
        :return:
        """
        return await self.request('post', '/utils/script/compile', data=code)

    async def utils_time(self):
        """
        Get node time

        :return:
        """
        return await self.request('get', '/utils/time')

    async def alias_broadcast_create(self, transaction_data):
        """
        Create alias

        :param transaction_data:
        :return:
        """
        return await self.request('post', '/alias/broadcast/create', json_data=transaction_data)

    async def alias_by_address(self, address):
        """
        Get alias by address

        :param address: acryl address
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/alias/by-address/{}'.format(address))

    async def alias_by_alias(self, alias):
        """
        Get address by alias

        :param alias: alias (without preifx and chain id)
        :type alias: str
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/alias/by-alias/{}'.format(alias))

    async def asset_broadcast_transfer(self, transfer_data):
        """
        Broadcast asset transfer transaction (v1)

        :param transfer_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/assets/broadcast/transfer', json_data=transfer_data)

    async def asset_broadcast_issue(self, transaction_data):
        """
        Issue asset (v1)

        :param transaction_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/assets/broadcast/issue', json_data=transaction_data)

    async def asset_broadcast_reissue(self, transaction_data):
        """
        Reissue asset (transaction v1)

        :param transaction_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/assets/broadcast/reissue', json_data=transaction_data)

    async def asset_broadcast_burn(self, transaction_data):
        """
        Burn asset (v1)

        :param transaction_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/assets/broadcast/burn', json_data=transaction_data)

    async def assets_balance(self, address):
        """
        Get assets balance

        :param address:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/assets/balance/{}'.format(address))

    async def assets_nft_balance(self, address, limit, after=None):
        """
        Get NFT balance (node version 1.0 and higher)

        :param address:
        :param limit:
        :param after:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        params = dict()
        if after:
            params["after"] = after

        return await self.request('get', '/assets/nft/{}/limit/{}'.format(address, limit), params=params)

    async def assets_balance_asset(self, address, asset_id):
        """
        Get asset balance

        :param address:
        :param asset_id:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/assets/balance/{}/{}'.format(address, asset_id))

    async def asset_distribution_at_height(self, asset_id, height, limit):
        """
        Get asset distribution at height

        :param asset_id:
        :param height:
        :param limit:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/assets/{}/distribution/{}/limit/{}'.format(asset_id, height, limit))

    async def assets_details(self, asset_id, full=None):
        """
        Get asset details

        :param asset_id:
        :param full:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        params = dict()
        if full is not None:
            params["full"] = full

        return await self.request('get', '/assets/details/{}'.format(asset_id), params=params)

    async def leasing_active(self, address):
        """
        Get active leasing

        :param address:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/leasing/active/{}'.format(address))

    async def leasing_broadcast_lease(self, transaction_data):
        """
        Create lease transaction

        :param transaction_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/leasing/broadcast/lease', json_data=transaction_data)

    async def leasing_broadcast_cancel_lease(self, transaction_data):
        """
        Create cancel lease transaction

        :param transaction_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/leasing/broadcast/cancel', json_data=transaction_data)

    async def peers_connected(self):
        """
        Get connected peer list

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/peers/connected')

    async def peers_clear_blacklist(self):
        """
        Clear peers blacklist

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/peers/clearblacklist')

    async def peers_blacklisted(self):
        """
        Get blacklisted peers

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/peers/blacklisted')

    async def peers_suspended(self):
        """
        Get suspended peers

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/peers/suspended')

    async def peers_connect(self, peer_data):
        """
        Connect to peer

        :param peer_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/peers/connect', json_data=peer_data)

    async def transaction_broadcast(self, transaction_data):
        """
        Broadcast new transaction

        :param transaction_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/transactions/broadcast', json_data=transaction_data)

    async def transaction_unconfirmed(self):
        """
        Get unconfirmed transactions

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/transactions/unconfirmed')

    async def transaction_unconfirmed_size(self):
        """
        Get size of unconfirmed transactions

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/transactions/unconfirmed/size')

    async def transaction_unconfirmed_info(self, transaction_id):
        """
        Get unconfirmed transaction info

        :param transaction_id:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/transactions/unconfirmed/info/{}'.format(transaction_id))

    async def transaction_calculate_fee(self, transaction_data):
        """
        Calculate transaction fee

        :param transaction_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/transactions/calculateFee', json_data=transaction_data)

    async def transaction_sign_address(self, signer_address, transaction_data):
        """
        Sign address transaction

        :param signer_address:
        :param transaction_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/transactions/sign/{}'.format(signer_address), json_data=transaction_data)

    async def transactions_address(self, address, limit, after=None):
        """
        Get address transactions

        :param address: Acryl address
        :param limit: transaction limit
        :param after: show transactions after transaction id
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        params = dict()
        if after:
            params["after"] = after

        return await self.request('get', '/transactions/address/{}/limit/{}'.format(address, limit), params=params)

    async def transaction_info(self, transaction_id):
        """
        Get transaction info

        :param transaction_id:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/transactions/info/{}'.format(transaction_id))

    async def transaction_sign(self, transaction_data):
        """
        Sign transaction

        :param transaction_data:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/transactions/sign', json_data=transaction_data)

    async def node_status(self):
        """
        Get node status

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/node/status')

    async def node_stop(self):
        """
        Stop node

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('post', '/node/stop')

    async def node_version(self):
        """
        Get node version

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/node/version')

    # Matcher endpoints

    async def matcher(self):
        """
        Get matcher public key

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return await self.request('get', '/matcher', matcher=True)

    async def matcher_orderbook(self):
        """
        Get trading markets

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request('get', '/matcher/orderbook', matcher=True)

    async def matcher_order_create(self, order_data):
        """
        Create order

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request('post', '/matcher/orderbook', json_data=order_data, matcher=True)

    async def matcher_settings(self):
        """
        Get matcher settings

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request('get', '/matcher/settings', matcher=True)

    async def matcher_orderbook_remove(self, amount_asset_id, price_asset_id):
        """
        Remove orderbook for asset pair

        :param amount_asset_id:
        :param price_asset_id:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request(
            'delete', '/matcher/orderbook/{}/{}'.format(amount_asset_id, price_asset_id), matcher=True
        )

    async def matcher_orderbook_get_asset_pair(self, amount_asset_id, price_asset_id):
        """
        Get orderbook for asset pair

        :param amount_asset_id:
        :param price_asset_id:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request('get', '/matcher/orderbook/{}/{}'.format(amount_asset_id, price_asset_id), matcher=True)

    async def matcher_orderbook_get_asset_pair_status(self, amount_asset_id, price_asset_id):
        """
        Get orderbook status for asset pair

        :param amount_asset_id:
        :param price_asset_id:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request(
            'get', '/matcher/orderbook/{}/{}/status'.format(amount_asset_id, price_asset_id), matcher=True
        )

    async def matcher_orderbook_history(self, public_key):
        """
        Get orderbook history for a public key

        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request('get', '/matcher/orderbook/{}'.format(public_key), matcher=True)

    async def matcher_orders_cancel_order(self, order_id, transaction_data):
        """
        Cancel order by id

        :param order_id:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request(
            'post', '/matcher/orders/cancel/{}'.format(order_id), json_data=transaction_data, matcher=True
        )

    async def matcher_orders_address(self, address):
        """
        Get address order history for an address

        :param address:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request('get', '/matcher/orders/{}'.format(address))

    async def matcher_orderbook_tradable_balance(self, amount_asset, price_asset, address):
        """
        Get tradable balance for asset pair

        :param amount_asset:
        :param price_asset:
        :param address:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request(
            'get', '/matcher/orderbook/{}/{}/tradableBalance/{}'.format(amount_asset, price_asset, address)
        )

    async def matcher_balance_reserved(self, public_key):
        """
        Get reserved balance of open orders

        :param public_key:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request('get', '/matcher/balance/reserved/{}'.format(public_key))

    async def matcher_order_status(self, amount_asset, price_asset, order_id):
        """
        Get order status for asset pair

        :param amount_asset:
        :param price_asset:
        :param order_id:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request('get', '/matcher/orderbook/{}/{}/{}'.format(amount_asset, price_asset, order_id))

    async def matcher_transactions_order(self, order_id):
        """
        Get exchange transactions created on DEX for the given order

        :param order_id:
        :return:
        :rtype: AcrylAsyncClientResponse
        """
        return self.request('get', '/matcher/transactions/{}'.format(order_id))

    async def start_session(self):
        """
        Create aiothttp client session
        :return: nothing
        :rtype: None
        """
        self.session = ClientSession(**self._default_session_args)
        acryl_client_logger.debug("Started session for {}".format(self))

    async def close_session(self):
        """
        Close aiothttp client session
        :return: nothing
        :rtype: None
        """
        acryl_client_logger.debug("Closing session for {}".format(self))
        await self.session.close()
        self.session = None
        acryl_client_logger.debug("Session closed for {}".format(self))

    async def request(self, method, endpoint, params=None, data=None, json_data=None, headers=None, matcher=False):
        """
        Make a asynchronous request to API
        If session was created outside (e.g. in context manager method) don't create new and don't close on
        request finish, else create new session and close it after request

        :param method: HTTP method
        :param endpoint: API endpoint
        :param params: query params
        :param data: body data
        :param json_data: body data in json
        :param headers: HTTP headers
        :param: matcher: matcher request
        :return: handled result if online else request params dict
        :rtype: AcrylAsyncClientResponse or dict
        """
        request_params = self._setup_request_params(endpoint, params, data, json_data, headers, matcher)
        if not self.online:
            acryl_client_logger.debug("Offline request '{}' in {}".format(endpoint, self))
            return request_params

        close_session = False
        if not self.session:
            self.session = ClientSession(**self._default_session_args)
            close_session = True

        try:
            session_method = getattr(self.session, method)
            acryl_client_logger.debug("Requesting '{}' in {}".format(endpoint, self))
            async with session_method(**request_params) as response:
                acryl_client_logger.debug("Finished request '{}' in {}".format(endpoint, self))
                result = await self._handle_response(response, endpoint)

        finally:
            if self.session and close_session:
                await self.session.close()
                self.session = None

        return result

    async def _handle_response(self, response, endpoint):
        """
        Handle aiohttp client response object
        :param response: requests response object
        :param endpoint: API endpoint
        :return: async client response object
        :rtype: AcrylAsyncClientResponse
        :raises: AcrylAsyncClientException
        """
        if response.status > 399:  # like `not response.ok` in requests
            try:
                error_data = await response.json()
            except (ValueError, ContentTypeError):
                error_code = None
                error_message = await response.text()
            else:
                error_code = error_data.get('code')
                error_message = error_data.get('message')

            if self.raise_exception:
                raise AcrylAsyncClientException(
                    "HTTP error code {}, error text: {}".format(response.status, error_message)
                )

            return AcrylAsyncClientResponse(
                successful=False, endpoint=endpoint, error_code=error_code, error_message=error_message
            )

        try:
            result = await response.json()
        except (ValueError, ContentTypeError):
            result = await response.text()

        return AcrylAsyncClientResponse(successful=True, endpoint=endpoint, response_data=result)

    async def __aenter__(self):
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()


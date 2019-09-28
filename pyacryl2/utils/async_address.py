"""
pyacryl2.utils.async_address
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Acryl address with async methods
"""

from pyacryl2.async_client import AcrylAsyncClient
from pyacryl2.utils.address import (
    BaseAcrylAddress, sign_required, DEFAULT_BURN_TRANSACTION_FEE,
    DEFAULT_SPONSORSHIP_TRANSACTION_FEE, DEFAULT_REISSUE_TRANSACTION_FEE, DEFAULT_ISSUE_TRANSACTION_FEE,
    DEFAULT_TRANSACTION_VERSION, DEFAULT_ALIAS_TRANSACTION_FEE, DEFAULT_CANCEL_LEASE_TRANSACTION_FEE,
    DEFAULT_LEASE_TRANSACTION_FEE, DEFAULT_TRANSFER_TRANSACTION_FEE, DEFAULT_SET_SCRIPT_TRANSACTION_FEE,
    DEFAULT_SET_ASSET_SCRIPT_TRANSACTION_FEE
)


class AcrylAsyncAddress(BaseAcrylAddress):
    """
    Acryl address with async client. Object methods will return coroutines, so you should run them in event loop
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_client = AcrylAsyncClient(
            node_address=self.node_address, chain_id=self.chain_id, online=self.online,
            request_params=self.client_request_params
        )
        
    async def from_alias(self, alias):
        """
        Set address value from alias

        :param alias: alias of address
        :return: address object with address value
        """
        address_data = await self._api_client.alias_by_alias(alias)
        self.value = address_data["address"]

    async def get_balance(self):
        """
        Get address balance

        :return: balance value
        :rtype: int
        """
        data = await self._api_client.address_balance(self.value)
        if not self.online:
            return data

        return data["balance"]

    async def get_effective_balance(self):
        """
        Get address effective balance

        :return: balance value
        :rtype: int
        """
        data = await self._api_client.address_effective_balance(self.value)
        if not self.online:
            return data
        
        return data["balance"]

    async def get_confirmed_balance(self, confirmations):
        """
        Get address balance

        :return: balance value
        :rtype: int
        """
        data = await self._api_client.address_balance_confirmed(self.value, confirmations)
        if not self.online:
            return data
        
        return data["balance"]

    async def get_assets(self):
        """
        Get address assets

        :return: asset balances in dict
        :rtype: dict
        """
        data = await self._api_client.assets_balance(self.value)
        if not self.online:
            return data
        
        return data["balances"]

    async def get_address_data(self):
        """
        Get address data from blockchain

        :return: data in dict
        :rtype: dict
        """
        data = await self._api_client.address_data_address(self.value)
        if not self.online:
            return data
        
        return data

    async def get_aliases(self, flat=True):
        """
        Get address aliases

        :param flat: get only alias names without chain ids
        :return: list of dicts with prefix, chain ids and alias names or only alias names
        :rtype: list
        """
        aliases = []
        data = await self._api_client.alias_by_address(self.value)
        if not self.online:
            return data
        
        for alias_data_string in data.response_data:
            prefix, chain_id, alias = alias_data_string.split(":")
            if flat:
                aliases.append(alias)
            else:
                aliases.append({"chain_id": chain_id, "alias": alias, "prefix": prefix})

        return aliases

    async def validate(self):
        """
        Validate address

        :return: validation result
        :rtype: bool
        """
        data = await self._api_client.address_validate(self.value)
        if not self.online:
            return data
        
        return data["valid"]

    async def get_address_info(self):
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
    async def data_transaction(self, data, version=DEFAULT_TRANSACTION_VERSION, timestamp=0):
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
        :rtype: AcrylAsyncClientResponse or dict
        """
        transaction_data = self._generate_data_transaction(data, version, timestamp)
        result = await self._api_client.transaction_broadcast(transaction_data)
        return result

    @sign_required
    async def transfer_acryl(self, recipient, amount, attachment=None, transaction_fee=DEFAULT_TRANSFER_TRANSACTION_FEE,
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
        :rtype: AcrylAsyncClientResponse or dict
        """
        transaction_data = self._generate_transfer_transaction(
            recipient, None, None, amount, attachment, transaction_fee, timestamp
        )
        result = await self._api_client.asset_broadcast_transfer(transaction_data)
        return result

    @sign_required
    async def transfer_asset(self, recipient, asset_id, fee_asset_id, amount, attachment=None,
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
        :rtype: AcrylAsyncClientResponse or dict
        """
        transaction_data = self._generate_transfer_transaction(
            recipient, asset_id, fee_asset_id, amount, attachment, transaction_fee, timestamp
        )
        result = await self._api_client.asset_broadcast_transfer(transaction_data)
        return result

    @sign_required
    async def mass_transfer_acryl(self, transfer_data, attachment=None, timestamp=None):
        """
        Mass transfer acryl

        :param transfer_data: list of dicts with recipient and amount i.e.
            `[{ 'recipient': '3N1xca2DY8AEwqRDAJpzUgY99eq8J9h4rB3', 'amount': 1000 }]`
        :param attachment: transaction attachment
        :param transaction_fee: mass transfer transaction fee
        :param timestamp: transaction timestamp
        :return:
        :rtype: AcrylAsyncClientResponse or dict
        """
        transaction_data = self._generate_mass_transfer_transaction(transfer_data, None, attachment, timestamp)
        result = await self._api_client.transaction_broadcast(transaction_data)
        return result

    @sign_required
    async def mass_transfer_assets(self, transfer_data, asset_id=None, attachment=None,
                                   version=DEFAULT_TRANSACTION_VERSION, timestamp=None):
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
        result = await self._api_client.transaction_broadcast(transaction_data)
        return result

    @sign_required
    async def lease_acryl(self, recipient, amount, transaction_fee=DEFAULT_LEASE_TRANSACTION_FEE, timestamp=0):
        """
        Lease acryl to address

        :param recipient:
        :param amount:
        :param transaction_fee:
        :param timestamp:
        :return:
        """
        transaction_data = self._generate_lease_transaction(recipient, amount, transaction_fee, timestamp)
        result = await self._api_client.leasing_broadcast_lease(transaction_data)
        return result

    @sign_required
    async def lease_cancel(self, transaction_id, transaction_fee=DEFAULT_CANCEL_LEASE_TRANSACTION_FEE, timestamp=0):
        """
        Cancel acryl lease

        :param transaction_id:
        :param transaction_fee:
        :param timestamp:
        :return:
        """
        transaction_data = self._generate_cancel_lease_transaction(transaction_id, transaction_fee, timestamp)
        result = await self._api_client.leasing_broadcast_cancel_lease(transaction_data)
        return result

    @sign_required
    async def create_alias(self, alias, transaction_fee=DEFAULT_ALIAS_TRANSACTION_FEE, timestamp=0):
        """
        Create alias for address

        :param alias: alias (min 4, max 30 chars)
        :param transaction_fee:
        :param timestamp:
        :return:
        """
        transaction_data = self._generate_alias_transaction(alias, transaction_fee, timestamp)
        result = await self._api_client.alias_broadcast_create(transaction_data)
        return result

    @sign_required
    async def issue_asset(self, name, description, quantity, decimals, reissuable,
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
            result = await self._api_client.asset_broadcast_issue(transaction_data)
        else:
            result = await self._api_client.transaction_broadcast(transaction_data)

        return result

    @sign_required
    async def issue_smart_asset(self, name, description, quantity, decimals, reissuable, script,
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
        result = await self._api_client.transaction_broadcast(transaction_data)
        return result

    @sign_required
    async def reissue_asset(self, asset_id, quantity, reissuable, transaction_fee=DEFAULT_REISSUE_TRANSACTION_FEE,
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
        result = await self._api_client.asset_broadcast_reissue(transaction_data)
        return result

    @sign_required
    async def burn_asset(self, asset_id, quantity, transaction_fee=DEFAULT_BURN_TRANSACTION_FEE, timestamp=0):
        """
        Burn asset

        :param asset_id: asset id
        :param quantity: asset quantity
        :param transaction_fee:
        :param timestamp: transaction timestamp
        :return:
        """
        transaction_data = self._generate_asset_burn_transaction(asset_id, quantity, transaction_fee, timestamp)
        result = await self._api_client.asset_broadcast_burn(transaction_data)
        return result

    @sign_required
    async def asset_sponsorship(self, asset_id, min_sponsored_asset_fee,
                                transaction_fee=DEFAULT_SPONSORSHIP_TRANSACTION_FEE, timestamp=0):
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
        result = await self._api_client.transaction_broadcast(transaction_data)
        return result

    @sign_required
    async def set_script(self, script, transaction_fee=DEFAULT_SET_SCRIPT_TRANSACTION_FEE, timestamp=None,
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
        result = await self._api_client.transaction_broadcast(transaction_data)
        return result

    @sign_required
    async def set_asset_script(self, script, asset_id, transaction_fee=DEFAULT_SET_ASSET_SCRIPT_TRANSACTION_FEE,
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
        result = await self._api_client.transaction_broadcast(transaction_data)
        return result

    def __repr__(self):
        return "AcrylAsyncAddress({})".format(self.value)

    def __str__(self):
        return self.value

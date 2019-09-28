Utilities
=========

With :mod:`pyacryl2.utils` you can easily create or verify Acryl addresses, generate
transaction data and simplify API requests.


Addresses
---------

With :class:`~pyacryl2.utils.address.AcrylAddress` you can create, sign and broadcast transactions.
For example Acryl transfer transaction:

.. code:: python

    from pyacryl2.utils import AcrylAddress
    address = AcrylAddress('address_base58_value', 'address_private_key')
    print(address.transfer_acryl('recipient_address', 1000))

Also it can be used to receive information from node, e.g. balance:

.. code:: python

    from pyacryl2.utils import AcrylAddress
    address = AcrylAddress('address_base58_value', 'address_private_key')
    print(address.get_balance())


:class:`~pyacryl2.utils.address.AsyncAcrylAddress` provides the same functionality as
:class:`~pyacryl2.utils.address.AcrylAddress` but with asynchronous API client:

.. code:: python

    from pyacryl2.utils import AcrylAddress
    address = AsyncAcrylAddress('address_base58_value', 'address_private_key')
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(
        address.transfer_acryl('recipient_address', 1000))
    print(result)

Address generator
-----------------

:class:`~pyacryl2.utils.address.AcrylAddressGenerator` provides functionality for address
creation and verification. Create new Acryl address:

.. code:: python

    from pyacryl2.utils import AcrylAddressGenerator
    new_address = AcrylAddressGenerator()

Create from existing seed, private or public key:

.. code:: python

    address = AcrylAddressGenerator().generate(seed="your_seed_here")
    address = AcrylAddressGenerator().generate(private_key="your_private_key")
    address = AcrylAddressGenerator().generate(public_key="your_public_key")

Validate address and get address object:

.. code:: python

    address_generator = AcrylAddressGenerator()
    address = address_generator.generate(value="address", private_key="your_private_key",
                                         public_key="your_public_key")

By default :meth:`~pyacryl2.utils.address.AcrylAddressGenerator.generate` returns :class:`.AcrylAddress` object. If you
need address object with async API client :class:`~pyacryl2.utils.address.AcrylAsyncAddress`

.. code:: python

    async_generator = AcrylAddressGenerator(async_address=True)
    new_async_address = async_generator.generate()

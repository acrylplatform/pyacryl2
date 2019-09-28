.. pyacryl2 documentation master file, created by
   sphinx-quickstart on Tue Sep  3 14:56:55 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyacryl2's documentation!
====================================

``pyacryl2`` is Python API client for Acryl node. It provides sync HTTP client based
on `requests <https://2.python-requests.org>`_ module and async based on
`aiohttp <https://docs.aiohttp.org/en/stable/client.html>`_.
Also it has some useful features e.g. Acryl address generation and validation, transaction data generation.

pyacryl2?
---------

There is already a module named ``pyacryl`` based on ``pywaves``. ``pyacryl2`` is not
compatible with ``pyacryl`` so it can't be used in old projects.

Installation
------------

.. code:: bash

      pip install pyacryl2

From source:

.. code:: bash

      python setup.py install

Tests:

From source:

.. code:: bash

      python setup.py test


Making requests to node API
---------------------------

Using sync client:

.. code:: python

      from pyacryl2.client import AcrylClient
      client = AcrylClient()
      print(client.node_version())

Or using async client:

.. code:: python

      import asyncio
      from pyacryl2.async_client import AcrylAsyncClient
      client = AcrylAsyncClient()

      # Python 3.6
      loop = asyncio.get_event_loop()
      print(loop.run_until_complete(client.node_version()))
      # Python 3.7
      print(asyncio.run(client.node_version()))


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   clients
   utilities
   pyacryl2_api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

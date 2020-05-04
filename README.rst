async-rpc
=========

Non-blocking XML-RPC client for Python. Provides base classes
``async_rpc.BaseSerializer`` and ``async_rpc.BaseServerProxy``,
you can write your own implementation of RPC (JSON RPC, ...).

Usage
-----

.. code-block:: python

    from async_rpc import XmlRpcServerProxy

    async def get_data():
        proxy = XmlRpcServerProxy('http://example.com/RPC2:8000')
        response = await proxy.methodName(123, 456)
        return response

License
-------

3-clause BSD

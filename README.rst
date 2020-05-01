async-rpc
=========

Non-blocking XML-RPC client for Python. Provides base class for any RPC
implementation, you can define your own serializer.

Usage
-----

.. code-block:: python

    async def get_data():
        proxy = XmlRpcServerProxy('http://example.com/RPC2:8000')
        response = await proxy.call('methodName', 123, 456)
        return response

License
-------

3-clause BSD

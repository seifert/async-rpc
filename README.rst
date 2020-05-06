async-rpc
=========

Non-blocking XML-RPC client for Python. Provides base classes
``async_rpc.BaseSerializer`` and ``async_rpc.BaseServerProxy``,
you can write your own implementation of RPC (JSON RPC, …).

Usage
-----

.. code-block:: python

    from async_rpc import XmlRpcServerProxy

    async def get_data():
        proxy = XmlRpcServerProxy('http://example.com/RPC2:8000')
        response = await proxy.methodName(123, 456)
        return response

API documentation
-----------------

*class* async_rpc.\ **BaseRpcServerProxy**\ (*uri, timeout=None,
max_clients=None, user_agent=None, use_dns_cache=None, ttl_dns_cache=None,
http_version=None, keepalive_timeout=None, \*\*kwargs*)

Base class for server proxies. It is responsible for HTTP transport. For
concrete RPC implementation uses descendant of the *BaseSerializer*.

- **uri** (*str*) – URL of the remote server
- **timeout** (*float*) – timeout in seconds for network operations,
  includes DNS requests, default is 1.0 seconds.
- **max_clients** (*int*) – size of the connections pool,
  default is 16 connections.
- **user_agent** (*str*) – user agent which is sent to server,
  default is ``"Python async-rpc"``.
- **use_dns_cache** (*bool*) – use internal cache for DNS lookups,
  default is ``True``.
- **ttl_dns_cache** (*float*) – store DNS lookups into internal cache
  for a *ttl_dns_cache* seconds, default is 10.0 seconds.
- **http_version** (*str*) – version of the HTTP protocol, can be
  ``"1.0"`` or ``"1.1"``, default is ``"1.0"``.
- **keepalive_timeout** (*float*) – close connection after *keepalive_timeout*
  seconds, if ``None``, keep-alive is disabled, default is ``None``.
- **kwargs**  (*dict*) – additional keyword arguments, which will be passed
  into serializer constructor.

*attribute* async_rpc.BaseRpcServerProxy.\ **serializer_cls**
(*BaseSerializer*) – serializer class

*coroutine* async_rpc.BaseRpcServerProxy.\ **call**\ (*name, \*\*params*)

- **name** (*str*) – mame of the remote function.
- **params**  (*dict*) – parameters, which will be passed to remote function.

Instance of the **BaseServerProxy** is callable, so you can call remote
function directly on server proxy instance. These calls are equivalent:

.. code-block:: python

    res = await proxy.getData('12345678901234567890')
    res = await proxy.call('getData', '12345678901234567890')


*class* async_rpc.\ **BaseSerializer**\ (*\*\*kwargs*)

Ancestor for concrete implementation of RPC. Contains four abstract methods,
which must be overriden in inherited classes.

- *kwargs* (*dict*) – additional keyword arguments, which are passed from
  server proxy.

*method* async_rpc.BaseSerializer.\ **initialize**\ (*\*\*kwargs*)

Initialize instance. It is called from constructor when instance is
created.

- **kwargs** (*dict*) – additional keyword arguments, which are passed from
  server proxy.

*abstractmethod* async_rpc.BaseSerializer.\ **prepare_request_headers**\ (
*params*)

Return ``dict`` containig HTTP headers. Method is called before RPC call
is sent. You can add additional HTTP header, which are be sent in request
to remote server.

- **params** (*tuple*) – params for RPC call.

*abstractmethod* async_rpc.BaseSerializer.\ **dumps**\ (*response_headers*)

Return data, which will be sent as POST body in request to remote
server. Method is called before RPC call is sent.

- **params** (*tuple*) – params for RPC call.
- **menthodname** (*str*) – name of the RPC method.

*abstractmethod* async_rpc.BaseSerializer.\ **process_response_headers**\ (
*response_headers*)

Check headers from response. Method is called after response is
received from server.

- **response_headers** (*Mapping*) – mapping containing response
  HTTP headers.

*abstractmethod* async_rpc.BaseSerializer.\ **loads**\ (*data,
response_headers*)

Return response from remote server as Python objects. Method is
called after response is received from server.

- **data** (*bytes*) – response body.
- **response_headers** (*Mapping*) – mapping containing response
  HTTP headers.

License
-------

3-clause BSD

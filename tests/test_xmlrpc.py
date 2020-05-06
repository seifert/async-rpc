
import asyncio
import socket
import threading
import xmlrpc.server

import pytest

from async_rpc import XmlRpcServerProxy


@pytest.fixture(scope='module')
def xml_rpc_server():
    sock = socket.socket()
    sock.bind(('', 0))
    try:
        port = sock.getsockname()[1]
    finally:
        sock.close()

    def server_thread():
        server.serve_forever(poll_interval=0.1)

    server = xmlrpc.server.SimpleXMLRPCServer(
            ('localhost', port),
            requestHandler=xmlrpc.server.SimpleXMLRPCRequestHandler)
    try:
        server.register_introspection_functions()
        server.register_function(lambda a, b: a+b, 'sum')

        t = threading.Thread(target=server_thread, daemon=True)
        t.start()

        yield ('localhost', port)
    finally:
        server.shutdown()


@pytest.mark.asyncio
async def test_xml_rpc_server_proxy(xml_rpc_server):
    proxy = XmlRpcServerProxy('http://{}:{}/'.format(*xml_rpc_server))
    assert await proxy.sum(3, 7) == 10


@pytest.mark.asyncio
async def test_xml_rpc_server_proxy_fail_when_timeout(xml_rpc_server):
    proxy = XmlRpcServerProxy(
        'http://{}:{}/'.format(*xml_rpc_server), timeout=0.0)
    with pytest.raises(asyncio.TimeoutError):
        await proxy.sum(3, 7)

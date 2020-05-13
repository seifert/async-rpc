
from unittest import mock

import aiohttp
import pytest

from async_rpc import BaseSerializer, BaseServerProxy


class Serializer(BaseSerializer):

    def initialize(self, dummy_param=None):
        self.dummy_param = dummy_param

    def prepare_request_headers(self, unused_params):
        return {
            'Content-Type': 'application/x.foo',
            'Accept': 'application/x.foo',
        }

    def dumps(self, params, methodname):
        return {'method': methodname, 'args': params}

    def process_response_headers(self, response_headers):
        if response_headers['Content-Type'] != 'application/x.foo':
            raise ValueError('Invalid content type')

    def loads(self, data, response_headers):
        return (data['response'], response_headers['Content-Type'])


class ServerProxy(BaseServerProxy):

    serializer_cls = Serializer


@pytest.mark.parametrize(
    'proxy_kwargs, expected', [
        (
            {},
            {'timeout': 1.0, 'max_clients': 16, 'use_dns_cache': True,
             'ttl_dns_cache': 10.0, 'user_agent': 'Python async-rpc'}
        ),
        (
            {'timeout': 0.02, 'max_clients': 32,
             'user_agent': 'AasyncRPC',
             'use_dns_cache': False, 'ttl_dns_cache': 60.0},
            {'timeout': 0.02, 'max_clients': 32, 'use_dns_cache': False,
             'ttl_dns_cache': 60.0, 'user_agent': 'AasyncRPC'}
        ),
    ])
def test_base_server_proxy_constructor(proxy_kwargs, expected):
    proxy = ServerProxy('https://rpc.example.com/RPC2', **proxy_kwargs)
    assert proxy.uri == 'https://rpc.example.com/RPC2'
    assert proxy.host == 'rpc.example.com'
    assert proxy.timeout == expected['timeout']
    assert proxy.max_clients == expected['max_clients']
    assert proxy.user_agent == expected['user_agent']
    assert proxy.use_dns_cache is expected['use_dns_cache']
    assert proxy.ttl_dns_cache == expected['ttl_dns_cache']
    assert proxy.keepalive_timeout is None
    assert proxy.http_version == aiohttp.HttpVersion10
    assert isinstance(proxy.serializer, Serializer)


@pytest.mark.parametrize('http_version, expected', [
    (None, aiohttp.HttpVersion10), ('1.0', aiohttp.HttpVersion10),
    ('1.1', aiohttp.HttpVersion11)])
def test_base_server_proxy_constructor_http_version(http_version, expected):
    proxy = ServerProxy('https://example.com/RPC2', http_version=http_version)
    assert proxy.http_version == expected


def test_base_server_proxy_constructor_fail_when_invalid_http_version():
    with pytest.raises(ValueError):
        ServerProxy('https://example.com/RPC2', http_version='2.0')


def test_base_server_proxy_session():
    proxy = ServerProxy('https://rpc.example.com/RPC2')
    assert 'session' not in vars(proxy)
    with mock.patch('aiohttp.ClientSession') as m_client_session:
        with mock.patch('aiohttp.TCPConnector') as m_tcp_connector:
            with mock.patch('aiohttp.ClientTimeout') as m_client_timeout:
                session = proxy.session
    assert 'session' in vars(proxy)
    assert session == m_client_session.return_value
    m_client_timeout.assert_called_once_with()
    m_tcp_connector.assert_called_once_with(
        keepalive_timeout=None,
        force_close=True,
        limit=16,
        use_dns_cache=True,
        ttl_dns_cache=10)
    m_client_session.assert_called_once_with(
        connector=m_tcp_connector.return_value,
        version=aiohttp.HttpVersion10,
        timeout=m_client_timeout.return_value,
        raise_for_status=True,
        skip_auto_headers=['Accept-Encoding'])


@pytest.mark.asyncio
async def test_base_server_callable():
    async def call_m(name, *args):
        return (name, *args)
    proxy = ServerProxy('https://rpc.example.com/RPC2')
    with mock.patch.object(proxy, 'call', call_m):
        res = await proxy.sum(1, 2)
    assert res == ('sum', 1, 2)


@pytest.mark.asyncio
async def test_base_server_call_method():
    session_post_m_calls = []

    async def session_post(*args, **kwargs):
        async def response_read():
            return {
                'response': 3,
            }
        session_post_m_calls.append((args, kwargs))
        return mock.Mock(
            read=response_read,
            headers={'Content-Type': 'application/x.foo'},
        )
    session_post_m = mock.Mock(post=session_post)

    proxy = ServerProxy('https://rpc.example.com/RPC2')
    with mock.patch.dict(proxy.__dict__, {'session': session_post_m}):
        res = await proxy.call('sum', 1, 2)
    assert res == (3, 'application/x.foo')
    assert len(session_post_m_calls) == 1
    assert session_post_m_calls[0] == (
        ('https://rpc.example.com/RPC2',),
        {
            'data': {'method': 'sum', 'args': (1, 2)},
            'headers': {
                'User-Agent': 'Python async-rpc',
                'Host': 'rpc.example.com',
                'Content-Type': 'application/x.foo',
                'Accept': 'application/x.foo',
            },
        },
    )

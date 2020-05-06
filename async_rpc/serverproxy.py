
import abc
import functools
import urllib.parse

import aiohttp
import async_timeout

__all__ = ['BaseSerializer', 'BaseServerProxy']


class BaseSerializer(abc.ABC):

    def __init__(self, **kwargs):
        self.initialize(**kwargs)

    def initialize(self, **kwargs):
        pass

    @abc.abstractmethod
    def prepare_request_headers(self, params):
        pass

    @abc.abstractmethod
    def dumps(self, params, methodname):
        pass

    @abc.abstractmethod
    def process_response_headers(self, response_headers):
        pass

    @abc.abstractmethod
    def loads(self, data, response_headers):
        pass


class BaseServerProxy(object):

    serializer_cls = BaseSerializer

    _http_versions = {
        None: aiohttp.HttpVersion10,
        '1.0': aiohttp.HttpVersion10,
        '1.1': aiohttp.HttpVersion11,
    }

    def __init__(
            self, uri, timeout=None, max_clients=None, user_agent=None,
            use_dns_cache=None, ttl_dns_cache=None, http_version=None,
            keepalive_timeout=None, **kwargs):
        self.uri = uri
        self.host = urllib.parse.urlparse(uri).netloc
        self.timeout = 1.0 if timeout is None else timeout
        self.max_clients = 16 if max_clients is None else max_clients
        self.user_agent = (
            'Python async-rpc' if user_agent is None else user_agent)
        self.use_dns_cache = True if use_dns_cache is None else use_dns_cache
        self.ttl_dns_cache = 10.0 if ttl_dns_cache is None else ttl_dns_cache
        self.keepalive_timeout = keepalive_timeout
        try:
            self.http_version = self._http_versions[http_version]
        except KeyError:
            raise ValueError(
                'Unsupported HTTP version {}'.format(http_version))
        self.serializer = self.serializer_cls(**kwargs)

    @property
    def session(self):
        if 'session' not in self.__dict__:
            session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(
                    keepalive_timeout=self.keepalive_timeout,
                    force_close=False if self.keepalive_timeout else True,
                    limit=self.max_clients,
                    use_dns_cache=self.use_dns_cache,
                    ttl_dns_cache=self.ttl_dns_cache,
                ),
                version=self.http_version,
                timeout=aiohttp.ClientTimeout(),
                raise_for_status=True,
                skip_auto_headers=['Accept-Encoding'],
            )
            self.__dict__['session'] = session
        return self.__dict__['session']

    def __getattr__(self, name):
        return functools.partial(self.call, name)

    async def call(self, name, *params):
        headers = {
            'User-Agent': self.user_agent,
            'Host': self.host,
        }
        request_headers = self.serializer.prepare_request_headers(params)
        if request_headers:
            headers.update(request_headers)
        data = self.serializer.dumps(params, name)
        async with async_timeout.timeout(self.timeout):
            response = await self.session.post(
                self.uri, data=data, headers=headers)
            data = await response.read()
        self.serializer.process_response_headers(response.headers)
        return self.serializer.loads(data, response.headers)

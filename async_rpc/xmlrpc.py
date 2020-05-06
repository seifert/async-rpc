
import xmlrpc.client

from .serverproxy import BaseSerializer, BaseServerProxy

__all__ = ['XmlRpcServerProxy']


class XmlRpcSerializer(BaseSerializer):

    def initialize(
            self, encoding=None, allow_none=False, use_builtin_types=False):
        self.encoding = 'utf8' if encoding is None else encoding
        self.allow_none = allow_none
        self.use_builtin_types = use_builtin_types

    def prepare_request_headers(self, unused_params):
        return {
            'Content-Type': 'text/xml',
            'Accept': 'text/xml',
        }

    def dumps(self, params, methodname):
        return xmlrpc.client.dumps(
            params, methodname=methodname, encoding=self.encoding,
            allow_none=self.allow_none)

    def process_response_headers(self, response_headers):
        ct = response_headers['Content-Type']
        if ct != 'text/xml':
            raise ValueError("Invalid response content type '{}'".format(ct))

    def loads(self, data, unused_response_headers):
        return xmlrpc.client.loads(
            data, use_builtin_types=self.use_builtin_types)[0][0]


class XmlRpcServerProxy(BaseServerProxy):

    serializer_cls = XmlRpcSerializer

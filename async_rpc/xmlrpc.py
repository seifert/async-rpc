
import xmlrpc.client

from . import BaseSerializer, BaseServerProxy

__all__ = ['XmlRpcServerProxy']


class XmlRpcSerializer(BaseSerializer):

    def initialize(
            self, encoding=None, allow_none=False, use_builtin_types=False):
        self.encoding = 'utf8' if encoding is None else encoding
        self.allow_none = allow_none
        self.use_builtin_types = use_builtin_types

    def prepare_request_headers(self):
        return {
            'Content-Type': 'text/xml',
            'Accept': 'text/xml',
        }

    def process_response_headers(self, headers):
        ct = headers['Content-Type']
        if ct != 'text/xml':
            raise ValueError("Invalid response content type '{}'".format(ct))

    def dumps(self, params, methodname):
        return xmlrpc.client.dumps(
            params, methodname=methodname, encoding=self.encoding,
            allow_none=self.allow_none)

    def loads(self, data):
        return xmlrpc.client.loads(
            data, use_builtin_types=self.use_builtin_types)[0][0]


class XmlRpcServerProxy(BaseServerProxy):

    serializer_cls = XmlRpcSerializer

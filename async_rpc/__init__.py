
import importlib
import pkgutil
import sys

from .serverproxy import BaseSerializer, BaseServerProxy
from .version import __version__ as _version
from .xmlrpc import XmlRpcServerProxy

__all__ = ['BaseSerializer', 'BaseServerProxy', 'XmlRpcServerProxy']

__version__ = _version

for extension_pkg_info in pkgutil.iter_modules():
    extension_name = extension_pkg_info[1]
    if not extension_name.startswith('async_rpc_'):
        del extension_name
        del extension_pkg_info
        continue
    extension_pkg = importlib.import_module(extension_name)
    for obj_name in getattr(extension_pkg, '__all__', []):
        async_rpc_pkg = sys.modules[__package__]
        setattr(async_rpc_pkg, obj_name, getattr(extension_pkg, obj_name))
        async_rpc_pkg.__all__.append(obj_name)
        del async_rpc_pkg
        del obj_name
    del extension_pkg
    del extension_name
    del extension_pkg_info

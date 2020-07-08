
import sys

from pathlib import Path
from runpy import run_path

from setuptools import setup

description = 'Library for launching tasks in parallel environment'

try:
    with open('README.rst', 'rt') as f:
        long_description = f.read()
except Exception:
    long_description = description

version_file = Path(__file__).parent / 'async_rpc' / 'version.py'
if sys.version_info < (3, 6):
    version_file = str(version_file)
version = run_path(version_file)['__version__']

setup(
    name='async-rpc',
    version=version,
    author='Jan Seifert',
    author_email='jan.seifert@fotkyzcest.net',
    description=description,
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license='BSD',
    url='https://github.com/seifert/async-rpc',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
    ],
    platforms=['any'],
    packages=['async_rpc'],
    zip_safe=True,
    install_requires=[
        'aiodns',
        'aiohttp',
        'async-timeout',
    ],
)

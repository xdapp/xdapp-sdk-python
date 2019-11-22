import sys
from distutils.core import setup
if sys.version_info < (3, 5):
    print >> sys.stderr, 'error: python 3.5 or higher is required, you are using %s' %'.'.join([str(i) for i in sys.version_info])

    sys.exit(1)

args = dict(
    name = 'xdapp',
    version = '1.0.1',
    description = 'XDAPP Python SDK',
    long_description = open('README.md').read(),
    keywords = "xdapp hprose rpc service",
    author = 'Jonwang',
    author_email = 'jonwang@xindong.com',
    platforms = 'any')

args['packages'] = ["xdapp"]
args['package_dir'] = dict(
    xdapp = "src"
)

args['classifiers'] = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.0',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Internet',
    'Topic :: Internet :: WWW/HTTP :: WSGI',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Object Brokering',
    'Topic :: System :: Networking',
    'Topic :: System :: Distributed Computing']

setup(**args)

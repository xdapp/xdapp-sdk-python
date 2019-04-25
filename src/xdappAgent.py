# encoding: utf-8

import asyncio
import logging
from xdapp.sysService import SysService
from xdapp.context import *
from xdapp.server import *

def _getStaticMethods(cls):
    v = vars(cls)
    return [name for name in v if isinstance(v[name], staticmethod)]


RPC_VERSION = 1          # RPC协议版本
FLAG_RESULT_MODE = 2     # 返回模式
FLAG_FINISH = 4          # 已完成


class XDAppServiceAgent(HproseService):
    def __init__(self, appName, serviceName, serviceKey):
        super(XDAppServiceAgent, self).__init__()
        self.appName = appName
        self.serviceName = serviceName
        self.serviceKey = serviceKey
        self.addStaticMethods(SysService, 'sys')
        self.serviceData = {}
        logging.basicConfig(
            level = logging.DEBUG,
            format = '[%(levelname)s]#%(threadName)-10s %(message)s',
        )

    # 连接到本地测试环境
    def connectToLocalDev(self, host = '127.0.0.1', port = 8061, serviceKey = '123456'):
        opt = {
            'tls': False,
            'localDev': True,
            'dev': True,
            'serviceKey': None,
        }
        if (serviceKey != None):
            opt['serviceKey'] = serviceKey

        return self.connectTo(host, port, opt)

    # 连接到测试环境
    def connectToDev(self, serviceKey):
        opt = {
            'tls': True,
            'localDev': False,
            'dev': True,
            'serviceKey': None,
        }
        if (serviceKey != None):
            opt['serviceKey'] = serviceKey

        return self.connectTo(host, port, opt)

    # 连接到生产环境
    def connectToProduce(self):
        opt = {
            'tls': True,
            'localDev': False,
            'dev': False,
            'serviceKey': None,
        }
        return self.connectTo(host, port, opt)

    def connectTo(self, host, port, option):
        serviceKey = self.serviceKey
        if (option['serviceKey'] != None):
            serviceKey = option['serviceKey']
        
        option['appName'] = self.appName
        option['serviceName'] = self.serviceName

        loop = asyncio.get_event_loop()
        protocol = XDAppProtocol(loop, self, option['serviceKey'])
        loop.run_until_complete(do_connect(loop, host, port, protocol))

        # client = XDAppClient(loop, self, serviceKey)
        # coro = loop.create_connection(lambda: client, host, port)
        # loop.run_until_complete(coro)
        # client.coro = coro

        # return client
                
    def runForever(self):
        loop = asyncio.get_event_loop()
        loop.run_forever()
        loop.close()
        
    # 获取当前上下文对象
    def getCurrentContext():
        return getCurrentContext()

    def register(self, function, alias = None, resultMode = HproseResultMode.Normal, simple = None):
        if isinstance(function, str):
            function = getattr(modules['__main__'], function, None)
        if not hasattr(function, '__call__'):
            raise HproseException('Argument function is not callable')
        if alias == None:
            alias = function.__name__

        alias = self.serviceName +'_'+ alias

        self.addFunction(function, alias, resultMode, simple)

    def log(self, log, type = 'info', data = None):
        if (type == 'info'):
            logging.info(log)
        elif (type == 'debug'):
            logging.debug(log)
        elif (type == 'warn'):
            logging.warn(log)

class XDAppProtocol(asyncio.Protocol):
    def __init__(self, loop, service, serviceKey):
        self.loop = loop
        self.service = service
        self.serviceKey = serviceKey
        self.host = None
        self.port = None
        self.regSuccess = False
        self.isRegError = False

    def connection_made(self, transport):
        self.transport = transport
        self.host, self.port = transport.get_extra_info('peername')

    def data_received(self, data):
        # b = new BytesIO(data)
        dataLength = len(data)
        if (dataLength < 20):
            return

        flag = data[0]
        ver = data[1]
        length = int.from_bytes(data[2:6], byteorder='big', signed=True)
        contextLength = data[22]
        bodyOffset = 23 + contextLength
        
        request = {
            'flag': flag,
            'ver': ver,
            'length': length,
            'appId': int.from_bytes(data[6:10], byteorder='big', signed=True),
            'serviceId': int.from_bytes(data[10:14], byteorder='big', signed=True),
            'requestId': int.from_bytes(data[14:18], byteorder='big', signed=True),
            'adminId': int.from_bytes(data[18:22], byteorder='big', signed=True),
            'contextLength': contextLength,
            'context': '',
            'body': data[bodyOffset:dataLength],
        }
        if (contextLength > 0):
            request['context'] = data[23:bodyOffset]

        context = Context()
        context.service = self.service
        context.client = self
        context.requestId = request['requestId']
        context.appId = request['appId']
        context.serviceId = request['serviceId']
        context.adminId = request['adminId']
        context.userdata = {}

        rs = self.service._handle(request['body'], context)
        self._send(rs, request)

    def connection_lost(self, exc):
        self.service.log('The server %s:%s closed the connection, registered error: %s' % (self.host, self.port, self.isRegError))
        # self.loop.stop()
        if (False == self.isRegError):
            # 重新连接
            self.service.log('retrying connect to %s:%s in 3 seconds' % (self.host, self.port));
            self.loop.call_later(3, reconnect, self)

    def close():
        return None

    def _send(self, body, request):
        packagePrefix = 6
        headerLength = 17
        length = headerLength + request['contextLength'] + len(body)

        # packagePrefix
        flag = request['flag'] | FLAG_RESULT_MODE | FLAG_FINISH
        buffer = bytes([flag, RPC_VERSION])

        buffer += length.to_bytes(4, byteorder='big')     # length
        # # header
        buffer += request['appId'].to_bytes(4, byteorder='big')             # appId
        buffer += request['serviceId'].to_bytes(4, byteorder='big')         # serviceId
        buffer += request['requestId'].to_bytes(4, byteorder='big')         # requestId
        buffer += request['adminId'].to_bytes(4, byteorder='big')           # adminId
        buffer += request['contextLength'].to_bytes(1, byteorder="little")  # contextLength
        if (request['contextLength'] > 0):
            buffer += request['context']

        buffer += body

        self.transport.write(buffer)

# see https://blog.csdn.net/jacke121/article/details/87897081

@asyncio.coroutine
def do_connect(loop, ip, port, protocol):
    while True:
        try:
            yield from loop.create_connection(lambda: protocol, host=ip, port=port)
        except OSError as e:
            logging.info("Can't connect %s:%s, retrying in 3 seconds" % (ip, port))
            yield from asyncio.sleep(3)
        else:
            break

def reconnect(old):
    protocol = XDAppProtocol(old.loop, old.service, old.serviceKey)
    old.loop.create_connection(lambda: protocol, host=old.host, port=old.port)
    asyncio.async(do_connect(old.loop, old.host, old.port, protocol))
import hashlib
import time as Time
import random
import string
from xdapp.context import *

def sha1(str):
    sha1 = hashlib.sha1()
    sha1.update(str.encode('utf-8'))
    return sha1.hexdigest()

def getHash(context, time, rand):
    return sha1('%s.%s.%s.%s.%s.xdapp.com' % (context.service.appName, context.service.serviceName, time, rand, context.client.serviceKey))

def getRand(len = 10):
    return ''.join(random.sample(string.ascii_letters + string.digits, len))

class SysService:
    @staticmethod
    def reg(time, rand, hash):
        context = getCurrentContext()
        if (None == context.service):
            return False
        
        if (context.client.regSuccess == True):
            return False

        if (hash != sha1('%s.%s.xdapp.com' % (time, rand))):
            # 验证失败
            return False

        now = int(Time.time())
        if (abs(now - time) > 60):
            # 超时
            return False

        context.client.isRegError = False
        newRand = getRand()
        return {
            'app': context.service.appName,
            'name': context.service.serviceName,
            'time': now,
            'rand': newRand,
            'version': 'v1',
            'hash': getHash(context, time, newRand),
        }

    @staticmethod
    # 注册失败
    def regErr(msg, data = None):
        context = getCurrentContext()
        context.client.isRegError = True
        context.service.log('Error: ' + msg)

    @staticmethod
    # 注册失败
    def regOk(data, time, rand, hash):
        context = getCurrentContext()
        if (None == context.service):
            return None
        
        if (context.client.regSuccess):
            return None

        now = int(Time.time())
        if (abs(now - time) > 60):
            # 超时
            service.log('RPC验证超时，服务名: %s->%s' % (context.service.appName, context.service.serviceName))
            return None

        if (getHash(context, time, rand) != hash):
            # 验证失败
            context.service.log('RPC验证失败，服务名: %s->%s' % (context.service.appName, context.service.serviceName))
            context.client.close()
            return None

        # 注册成功
        context.service.serviceData = data;
        context.client.regSuccess = True;

        context.service.log('RPC服务注册成功，服务名: %s->%s' % (context.service.appName, context.service.serviceName))

    @staticmethod
    def log(log, type, data = None):
        context = getCurrentContext()
        context.service.log(log, type, data)

    @staticmethod
    def getFunctions():
        context = getCurrentContext()
        if (False == context.client.regSuccess):
            return []
        return context.service.getNames()
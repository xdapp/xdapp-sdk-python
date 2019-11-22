# XDApp Python SDK

## 安装

下载SDK包后进入目录执行安装命令

```
python3 setup.py install
```

## 使用说明

```python
#!/usr/bin/env python
# encoding: utf-8

import xdapp

def hello(name):
    # 获取 context 对象
    context = xdapp.getCurrentContext()
    print(context.adminId)

    # 返回内容
	return 'Hello %s!' % name

def main():
	service = xdapp.ServiceAgent('appName', 'serviceName', 'key')
	service.register(hello, 'hello')
	service.connectToProduce()
    service.runForever()

if __name__ == '__main__':
	main()
```

## 常用方法

```python
service = xdapp.ServiceAgent('appName', 'serviceName', 'key')
```

`ServiceAgent` 接受3个参数，分别是应用英文名、服务名和密钥，应用是在 https://www.xdapp.com/ 里创建的应用，服务是在应用后台内自行创建的服务名，密钥是对应每个应用的连接密钥

### 关于 `context` 上下文对象

在RPC请求时，如果需要获取到请求时的管理员ID等等参数，可以用此获取，如上面 `hello` 的例子，通过 `context = xdapp.getCurrentContext()` 可获取到 `context`，包括：

参数         |   说明
------------|---------------------
service     | 当前服务
client      | 通信的 `XDAppProtocol` 对象，可以使用 `close()` 方法关闭连接
requestId   | 请求的ID
appId       | 请求的应用ID
serviceId   | 请求发起的服务ID，0表示XDApp系统请求，1表示来自浏览器的请求
adminId     | 请求的管理员ID，0表示系统请求
userdata    | 默认 {} 对象，可以自行设置参数

返回的 `service` 对象常用方法如下：

### `connectToProduce()`

连接到国内生产环境，将会创建一个异步tls连接接受和发送RPC数据，无需自行暴露端口，如果遇到网络问题和服务器断开可以自动重连，除非是因为密钥等问题导致的断开将不会重新连接

### `connectToProduceAsia()`

连接到东南亚正式环境，同 `connectToProduce()` 差别在于项目是部署在东南亚的

### `connectToProduceEurope()`

连接到欧洲正式环境，同 `connectToProduce()` 差别在于项目是部署在欧洲的

### `connectToDev(serviceKey = None)`

同上，连接到研发环境, 不设置 serviceKey 则使用 new ServiceAgent 时传入的密钥

### `connectToLocalDev(self, host = '127.0.0.1', port = 8061, serviceKey = None)`

同上，连接到本地研发服务器，请下载 XDApp-Console-UI 服务包，https://hub000.xindong.com/core-system/xdapp-console-ui ，启动服务

### 同时连接多个环境

一个 `service` 可以同时连接 `connectToProduce`, `connectToDev`, `connectToLocalDev` 3个，但需要保证使用正确的密钥。但不建议将测试环境的连接到生产环境服务器里

### `addWebFunction(function, alias = None, resultMode = HproseResultMode.Normal, simple = None)`

注册一个可用于Web调用的RPC方法到服务上，它是 `service.addFunction()` 方法的封装，差别在于会自动对 `alias` 增加 `serviceName` 前缀

`register.addWebFunction(hello, 'hello')` 相当于 `register.addFunction(hello, 'servicename_hello')`

### `addFunction(function, alias = None, resultMode = HproseResultMode.Normal, simple = None)`

注册一个RPC方法到服务上


### `addStaticMethods(cls, aliasPrefix = None, resultMode = HproseResultMode.Normal, simple = None)`

批量的将一个对象的所有静态方法全部注册到服务里

```python

class MyService:
    @staticmethod
    def fun1():
        return true

    @staticmethod
    def fun2():
        return '123'


# 创建一个服务
service = xdapp.ServiceAgent('demo', 'test', '123456')
# 添加方法，请注意，必须和服务名一样开头的rpc服务才会允许被其它服务或网页访问
service.addStaticMethods(MyService, 'test_myservice')

# 打印所有已注册服务列表
# 输出: dict_values(['test_myservice_fun1', 'test_myservice_fun2'])
print(service.getNames())
```

### `addMissingFunction(function, resultMode = HproseResultMode.Normal, simple = None)`

此方法注册后，所有未知RPC请求都降调用它，它将传入2个参数，分别是RPC调用名称和参数

### `addFilter() / removeFilter()` 过滤器

可以方便开发调试

see [https://github.com/hprose/hprose-nodejs/wiki/Hprose-过滤器](https://github.com/hprose/hprose-nodejs/wiki/Hprose-过滤器)


### 更多方法

都是 addFunction 的封装，见如下代码

```python
def addMethod(self, methodname, belongto, alias = None, resultMode = HproseResultMode.Normal, simple = None):
    function = getattr(belongto, methodname, None)
    if alias == None:
        self.addFunction(function, methodname, resultMode, simple)
    else:
        self.addFunction(function, alias, resultMode, simple)

def addMethods(self, methods, belongto, aliases = None, resultMode = HproseResultMode.Normal, simple = None):
    aliases_is_null = (aliases == None)
    if not isinstance(methods, (list, tuple)):
        raise HproseException('Argument methods is not a list or tuple')
    if isinstance(aliases, str):
        aliasPrefix = aliases
        aliases = [aliasPrefix + '_' + name for name in methods]
    count = len(methods)
    if not aliases_is_null and count != len(aliases):
        raise HproseException('The count of methods is not matched with aliases')
    for i in range(count):
        method = methods[i]
        function = getattr(belongto, method, None)
        if aliases_is_null:
            self.addFunction(function, method, resultMode, simple)
        else:
            self.addFunction(function, aliases[i], resultMode, simple)

def addInstanceMethods(self, obj, cls = None, aliasPrefix = None, resultMode = HproseResultMode.Normal, simple = None):
    if cls == None: cls = obj.__class__
    self.addMethods(_getInstanceMethods(cls), obj, aliasPrefix, resultMode, simple)

def addFunctions(self, functions, aliases = None, resultMode = HproseResultMode.Normal, simple = None):
    aliases_is_null = (aliases == None)
    if not isinstance(functions, (list, tuple)):
        raise HproseException('Argument functions is not a list or tuple')
    count = len(functions)
    if not aliases_is_null and count != len(aliases):
        raise HproseException('The count of functions is not matched with aliases')
    for i in range(count):
        function = functions[i]
        if aliases_is_null:
            self.addFunction(function, None, resultMode, simple)
        else:
            self.addFunction(function, aliases[i], resultMode, simple)
```

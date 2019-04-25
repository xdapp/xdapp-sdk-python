#!/usr/bin/env python
# encoding: utf-8

import xdapp

def hello(name):
	return 'Hello %s!' % name

def main():
	service = xdapp.ServiceAgent('demo', 'test', '123')
	service.register(hello, 'abc')
	# service.connectToLocalDev('127.0.0.1', 8612)
	service.connectToLocalDev()		# 连接到本地测试环境
	# service.connectToProduce()	# 连接到生产环境
	# service.connectToDev()		# 连接到研发环境
	service.runForever()

if __name__ == '__main__':
	main()
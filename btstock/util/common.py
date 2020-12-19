#!/usr/bin/python
#-*- coding: UTF-8 -*-

DEF='\033[0m'
RED = '\033[1;31m'
GRE='\033[1;32m'
YEL='\033[1;33m'
BLU='\033[1;34m'
class FuncTime(object):
	'function_time'
	def __init__(self):
		self.start = 0
		self.end = 0
		'''获取行号'''
		self.line_num = sys._getframe().f_back.f_lineno
		'''获取调用函数名'''
		self.func_name = sys._getframe().f_back.f_code.co_name
		self.__FuncStart()

	def __FuncStart(self):
		self.start = time.time()
		print("\r{}{}{: <20}{}{: <20}{}{: <30}{: >10}{}".format(YEL,"文件：","["+F+"]"," 执行函数：","<"+self.func_name+">","行号：",self.line_num,"[执行中]",DEF),end='')

	def FuncEnd(self):
		self.end = time.time()
		d = self.end - self.start
		print("\r{}{}{: <20}{}{: <20}{}{: <30}{: >10}{}{: >10.4f}s".format(GRE,"文件：","["+F+"]"," 执行函数：","<"+self.func_name+">","行号：",self.line_num,"[已完成]",DEF,d))

#!/usr/bin/python
#-*- coding: UTF-8 -*-
'''---------------------------------------------------------
# 本程序用于获取金融数据(股票)并进行实时跟踪股票
# auther by huangxl 20201215
---------------------------------------------------------'''

'''通用包'''
import os
import sys,getopt
import xlwt
import requests
import ssl
import urllib
from urllib.parse import urlparse
import http.client
from urllib.parse import urlencode
import time
from prettytable import PrettyTable
from bs4 import BeautifulSoup
import pymysql
#from DBUtils.PooledDB import PooledDB
from dbutils.pooled_db import PooledDB
import threading
from threading import Timer
import datetime
import json
import math
import subprocess
'''特殊包'''
import tushare as ts
from sqlalchemy import create_engine

p_level = 5#打印信息级别，1为最低，只打印报错信息，5为最高，打印任何信息。
F = os.path.split(__file__)[-1]
DEF='\033[0m'
RED = '\033[1;31m'
GRE='\033[1;32m'
YEL='\033[1;33m'
BLU='\033[1;34m'
def prcc(content,color=''):
	try:
		line_num = sys._getframe().f_back.f_lineno		#获取行号
		func_name = sys._getframe().f_back.f_code.co_name #获取调用函数名
		curr_name = sys._getframe().f_code.co_name		# 获取当前函数名
		if(p_level>=5 and color=='r'):
			print(RED+"\r\n*****************************************************\r\n*** "+F+" >> "+func_name+" >> line:"+str(line_num)+" \r\n*** "+content+"\r\n*****************************************************"+DEF)
		elif(p_level>=4 and color=='y'):
			print(YEL+"\r\n*****************************************************\r\n*** "+F+" >> "+func_name+" >> line:"+str(line_num)+" \r\n*** "+content+"\r\n*****************************************************"+DEF)
		elif(p_level>=3 and color=='b'):
			print(BLU+"\r\n*****************************************************\r\n*** "+F+" >> "+func_name+" >> line:"+str(line_num)+" \r\n*** "+content+"\r\n*****************************************************"+DEF)
		elif(p_level>=2 and color=='g'):
			print(GRE+"\r\n*****************************************************\r\n*** "+F+" >> "+func_name+" >> line:"+str(line_num)+" \r\n*** "+content+"\r\n*****************************************************"+DEF)
		elif(p_level>=1 and color==''):
			print(DEF+"\r\n*****************************************************\r\n*** "+F+" >> "+func_name+" >> line:"+str(line_num)+" \r\n*** "+content+"\r\n*****************************************************"+DEF)
	except UnicodeEncodeError:
		print(bad_filename(content))

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


class Mysql(object):
	'Mysql element'
	def __init__(self):
		self.mysql_host = '127.0.0.1'
		self.user = 'root'
		self.password = '123456'
		self.db = 'tushare'
		self.conn_num = 5
		self.port = 3306
		self.pool = PooledDB(pymysql,self.conn_num, host=self.mysql_host, user=self.user, passwd=self.password, db=self.db, port=self.port)
		self.conn = self.pool.connection()
		self.cur = self.conn.cursor()

	def set_mysql_host(self,data):
		self.mysql_host = data
	def set_user(self,data):
		self.user = data
	def set_password(self,data):
		self.password = data
	def set_db(self,data):
		self.db = data
	def set_port(self,data):
		self.port = data

	def execute_sql_file(self,sql_file_path):
		try:
			with open(sql_file_path,'r+',encoding = 'utf8') as f:
				print(f)
				sql_list = f.read().split(';')[:-1]
				sql_list = [x.replace('\n',' ') if '\n' in x else x for x in sql_list]
			for sql_item in sql_list:
				self.insert(sql_item)
		except Exception as e:
			prcc("错误描述："+str(e)+" 错误行："+str(e.__traceback__.tb_lineno),'r')
			sys.exit()
	def select(self,sql):
		try:
			self.cur.execute(sql)
			data = self.cur.fetchall()
			return data
		except Exception as e:
			prcc("错误描述："+str(e)+" 错误行："+str(e.__traceback__.tb_lineno),'r')
			sys.exit()
		else:
			pass
		finally:
			pass
	def select_one(self,sql):
		try:
			self.cur.execute(sql)
			data = self.cur.fetchone()
			return data
		except Exception as e:
			prcc("错误描述："+str(e)+" 错误行："+str(e.__traceback__.tb_lineno),'r')
			sys.exit()
	def insert(self,sql):
		try:
			self.cur.execute(sql)
			self.cur.fetchone()
			self.conn.commit()
		except Exception as e:
			prcc("错误描述："+str(e)+" 错误行："+str(e.__traceback__.tb_lineno),'r')
			sys.exit()
	def delete(self,sql):
		try:
			self.cur.execute(sql)
			self.cur.fetchone()
			self.conn.commit()
		except Exception as e:
			prcc("错误描述："+str(e)+" 错误行："+str(e.__traceback__.tb_lineno),'r')
			sys.exit()
	def update(self,sql):
		try:
			self.cur.execute(sql)

			self.conn.commit()
		except Exception as e:
			prcc("错误描述："+str(e)+" 错误行："+str(e.__traceback__.tb_lineno),'r')
			sys.exit()

class Tushare(object):
	'tushare_api'
	def __init__(self):
		print("init")
		'''初始化'''
		self.ts = ts
		self.version = self.ts.__version__
		self.token = '995be613a9323157f9af37899b92c26659fba4d9d1183184cd9c5b71'
		self.set_token(self.token)
		self.pro = self.ts.pro_api()
		self.engine = create_engine('mysql://tushare:tushare@127.0.0.1/tushare?charset=utf8')
		self.mysql = Mysql()
		self.init_database()
		
	def init_database(self):
		print('init_database')
		sql = "select table_schema from information_schema.TABLES where table_schema = 'tushare'"
		database = self.mysql.select(sql)
		if(len(database)==0):
			sql_db_tushare = "./tushare.sql"
			self.mysql.execute_sql_file(sql_db_tushare)
		else:
			# print('获取当前所有股票列表')
			# data = self.pro.stock_basic(exchange='', list_status='L', fields='')
			# self.to_sql('stock_basic',data)
			# sql = "select * from stock_basic where 1"
			# basic_now = self.mysql.select(sql)
			# length_now = len(basic_now)

			# data = self.pro.stock_basic(exchange='', list_status='L', fields='')
			# length_data = len(data)
			# print("length_now:"+str(length_now)+" length_data:"+str(length_data))
			# if(length_data!=length_data):
			# 	sql = "DROP TABLE IF EXISTS `stock_basic`;"
			# 	self.mysql.delete(sql)
			# 	self.to_sql('stock_basic',data)
			print("stock_basic OK")
		

	def set_token(self,token=''):
		if(token==""):
			self.ts.set_token(self.token)
		else:
			self.ts.set_token(str(token))

	def to_sql(self,table_name,df):
		try:
			df.to_sql(table_name,self.engine)
		except Exception as e:
			prcc("错误描述："+str(e)+" 错误行："+str(e.__traceback__.tb_lineno),'r')
			sys.exit()

	def help(self,api_name='',api_class=''):
		if(api_class=="" or api_class=="pro"):
			if(api_name=="" or api_name=="daily"):
				print("daily")
		elif(api_class=="" or api_class=="standard" or api_class=="sta"):
			print("bypass")

	def __init_stock_policy_yycsx(self,start,end):
		try:
			'''获取当前所有股票列表'''
			print('获取当前所有股票列表')
			sql = "select * from stock_basic where 1"
			basic_now = self.mysql.select(sql)
			length_now = len(basic_now)

			data = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
			length_data = len(data)

			if(length_data!=length_data):
				sql = "DROP TABLE IF EXISTS `stock_basic`;"
				self.mysql.delete(sql)
				self.to_sql('stock_basic',data)
			print("stock_basic OK")
			print('获取单只股票均线数据')
			'''获取单只股票均线数据'''
			# sql = "CREATE TABLE `stock_yycsx` (  `ts_code` varchar(20) NOT NULL,  `symbol` varchar(20) DEFAULT NULL,  `name` varchar(255) NOT NULL,  `close` double DEFAULT '0',  `ma5` double DEFAULT '0',  `ma10` double DEFAULT '0',  `ma20` double DEFAULT '0',  `up5` int(11) DEFAULT '0',  `up10` int(11) DEFAULT '0',  `up20` int(11) DEFAULT '0',  `flag` int(11) DEFAULT '0') ENGINE=MyISAM DEFAULT CHARSET=utf8;"
			# self.mysql.insert(sql)
			sql = "delete from stock_yycsx where 1"
			#self.mysql.delete(sql)
			sql = "insert into `stock_yycsx` (`ts_code`,`symbol`,`name`) select `ts_code` ,`symbol`,`name` from `stock_basic`;"
			#self.mysql.insert(sql)
			sql = "select ts_code from stock_yycsx where flag = '0'"
			ts_code = self.mysql.select(sql)
			t_start = time.time()
			count = 0
			for i in range(len(ts_code)):
				count = count + 1
				if(count==500):
					count = 0
					t_end = time.time()
					t_fine = int((t_end - t_start))
					print("本轮500条耗时："+str(t_fine)+" 秒")
					if(t_fine > 61):
						pass
					else:
						t_fine = 61 - int((t_end - t_start))
						print("需要等待 "+str(t_fine)+" 秒")
						time.sleep(t_fine)
					t_start = t_end
				temp_ts_code = ts_code[i][0]
				print("temp_ts_code:"+str(temp_ts_code))
				df = self.ts.pro_bar(ts_code=temp_ts_code, start_date='2020-11-01', end_date=end, ma=[5, 10, 20])
				if(len(df)==0):
					pass
				else:
					t = df[['close','ma5','ma10','ma20','change','pct_chg']]
					temp_close = t.values[0][0]
					temp_ma5 = t.values[0][1]
					temp_ma10 = t.values[0][2]
					temp_ma20 = t.values[0][3]
					temp_change = t.values[0][4]
					temp_pct_chg = t.values[0][5]
					temp_flag = 1
					print("temp_trade_date:"+temp_trade_date)
					if(math.isnan(t.values[0][1]) or math.isnan(t.values[0][2]) or math.isnan(t.values[0][3])):
						temp_ma5 = 0
						temp_ma10 = 0
						temp_ma20 = 0
						temp_flag = 0
						temp_change = 0
						temp_pct_chg = 0
					sql = "update `stock_yycsx` set `close`="+str(temp_close)+",`change`="+str(temp_change)+",`pct_chg`="+str(temp_pct_chg)+",ma5 ="+str(temp_ma5)+",ma10="+str(temp_ma10)+",ma20 ="+str(temp_ma20)+",flag="+str(temp_flag)+" where ts_code='"+str(temp_ts_code)+"'"
					print(sql)
					self.mysql.update(sql)
			sql = "update sys_init_info set status = 1 where stock_policy_name='yycsx' and date = '"+str(end)+"'"
			print(sql)
			self.mysql.update(sql)
		except Exception as e:
			prcc("错误描述："+str(e)+" 错误行："+str(e.__traceback__.tb_lineno),'r')
			sys.exit()

	def __timer_stock_policy_yycsx(self):
		try:
			#sys.exit()
			print(datetime.datetime.today())
			sql = "DROP TABLE IF EXISTS `get_today_all`;"
			self.mysql.delete(sql)
			df = self.ts.get_today_all()
			t = df[['code','name','trade']]
			#print(t)
			#df = self.pro.daily_basic(ts_code='', trade_date='20201211', fields='symbol,name,close')
			#t = df[['symbol','name','close']]
			self.to_sql('get_today_all',df)
			up5 =0
			up10 = 0
			up20 = 0
			flag = 0
			for i in range(len(t)):
				temp_code = t.values[i][0]
				temp_name = t.values[i][1]
				temp_trade = t.values[i][2]
				#print("temp_code:"+str(temp_code)+" temp_trade:"+str(temp_trade))
				sql = "select symbol,close,ma5,ma10,ma20 from stock_yycsx where symbol = '"+str(temp_code)+"'"
				temp_data = self.mysql.select(sql)
				if(temp_data):
					if(temp_data[0][1]<temp_data[0][2] and temp_data[0][1]<temp_data[0][3] and temp_data[0][1]<temp_data[0][4]):
						up5 = 1 if temp_trade>temp_data[0][2] else 0
						up10 = 1 if temp_trade>temp_data[0][3] else 0
						up20 = 1 if temp_trade>temp_data[0][4] else 0
						flag = up5 + up10 + up20
						sql = "update stock_yycsx set trade="+str(temp_trade)+", up5 = "+str(up5)+",up10 = "+str(up10)+",up20 = "+str(up20)+",flag = "+str(flag)+" where symbol = '"+str(temp_code)+"'"
						self.mysql.update(sql)
					else:
						sql = "update stock_yycsx set trade="+str(temp_trade)+", flag = 9 where symbol = '"+str(temp_code)+"'"
						self.mysql.update(sql)
			t_all = Timer(60, self.__timer_stock_policy_yycsx)
			t_all.start()
		except Exception as e:
			prcc("错误描述："+str(e)+" 错误行："+str(e.__traceback__.tb_lineno),'r')
			sys.exit()
		finally:
			str_filter = " and symbol not like '3%' and user_filter = '1'"
			sql = "select count(*) from stock_yycsx where 1"+str_filter
			data = self.mysql.select(sql)
			total = data[0][0]
			sql = "select count(*) from stock_yycsx where flag <> 9"+str_filter
			data = self.mysql.select(sql)
			contain = data[0][0]
			sql = "select count(*) from stock_yycsx where flag = 0"+str_filter
			data = self.mysql.select(sql)
			zero = data[0][0]
			sql = "select count(*) from stock_yycsx where flag = 1"+str_filter
			data = self.mysql.select(sql)
			one = data[0][0]
			sql = "select count(*) from stock_yycsx where flag = 2"+str_filter
			data = self.mysql.select(sql)
			two = data[0][0]
			sql = "select count(*) from stock_yycsx where flag = 3"+str_filter
			data = self.mysql.select(sql)
			three = data[0][0]
			pt=PrettyTable()
			pt.field_names = ["总数","符合开盘条件数","突破0条均线","突破1条均线","突破2条均线","突破3条均线"]
			pt.add_row([total,contain,zero,one,two,three])
			print(pt)
			pt=PrettyTable()
			pt.field_names = ["代码","名称","现价","开盘价","涨跌值","涨跌比","5日均线","10日均线","20日均线"]
			sql = "select ts_code,name,trade,close,change,ptc_chg,ma5,ma10,ma20,symbol from stock_yycsx where flag = 3"+str_filter
			data = self.mysql.select(sql)
			stock_array = ()
			for i in range(len(data)):
				stock_array.append(data[i][9])
				pt.add_row([data[i][0],data[i][1],data[i][2],data[i][3],data[i][4],data[i][5],data[i][6],data[i][7],data[i][8]])
			print(pt)
			sys.exit()
		

	def stock_policy_yycsx(self):
		print("stock_policy_yycsx")
		'''初始化'''
		today = datetime.datetime.today()
		yesterday = today - datetime.timedelta(days=1)
		start = str(yesterday).split(" ")[0]
		end = str(today).split(" ")[0]
		print(str(end))
		sql = "select * from sys_init_info where stock_policy_name ='yycsx' and date='"+str(end)+"';"
		print(sql)
		init_data = self.mysql.select(sql)
		if(len(init_data)==0):
			print("stock_policy_yycsx: in 1")
			sql = "insert into sys_init_info values ('yycsx','"+str(end)+"',0)"
			self.mysql.insert(sql)
			self.__init_stock_policy_yycsx(start,end)
			self.__timer_stock_policy_yycsx()
		elif(init_data[0][2]==0):
			print("stock_policy_yycsx: in 2")
			self.__init_stock_policy_yycsx(start,end)
			self.__timer_stock_policy_yycsx()
		else:
			print("stock_policy_yycsx: in 3")
			self.__timer_stock_policy_yycsx()
			
	def my_focus(self):
		#os.system('cls')
		df = ts.get_realtime_quotes(['601952','600900','002341','601099','000725'])
		t = df[['code','name','price','time']]
		print(t)
		timer = Timer(5, self.my_focus)
		timer.start()

def create_today_record(tus,table_name):
	print("create_today_record...")
	sql = "select table_name from information_schema.TABLES where table_name = '"+table_name+"'"
	data = tus.mysql.select(sql)
	flag_table = 1 if len(data)==1 else 0
	print("flag_table:"+str(flag_table))
	if(flag_table==0):
		sql = "create table `"+table_name+"` select * from `stock_yycsx`"
		print("建立今日记录："+sql)
		tus.mysql.insert(sql)
		sql = "delete from "+table_name+" where 1"
		tus.mysql.delete(sql)
		sql = "select ts_code,symbol,name,area,industry,market from stock_basic where 1"
		data = tus.mysql.select(sql)
		count = 0
		for i in range(len(data)):
			count = count + 1
			sql = "insert into "+table_name+" (`ts_code`,`symbol`,`name`,`area`,`industry`,`market`) values \
			('"+str(data[i][0])+"','"+str(data[i][1])+"','"+str(data[i][2])+"','"+str(data[i][3])+"','"+str(data[i][4])+"','"+str(data[i][5])+"')"
			tus.mysql.insert(sql)
		print("count:"+str(count))
	else:
		print("今日记录已建立。")

def make_today_base_data(tus,table_name,start,end):
	print("make_today_base_data...")
	sql = "select ts_code from "+str(table_name)+" where is_build = '0'"
	ts_code = tus.mysql.select(sql)
	if(len(ts_code)==0):
		print("今日构建已建立。")
		return
	t_start = time.time()
	count = 0
	for i in range(len(ts_code)):
		count = count + 1
		print("count:"+str(count))
		if(count==500):
			count = 0
			t_end = time.time()
			t_fine = int((t_end - t_start))
			print("本轮500条耗时："+str(t_fine)+" 秒")
			if(t_fine > 60):
				t_fine = 120 - int((t_end - t_start))
				print("需要等待 "+str(t_fine)+" 秒")
				time.sleep(t_fine)
			else:
				t_fine = 60 - int((t_end - t_start))
				print("需要等待 "+str(t_fine)+" 秒")
				time.sleep(t_fine)
			t_start = t_end
		temp_ts_code = ts_code[i][0]
		df = tus.ts.pro_bar(ts_code=temp_ts_code, start_date=start, end_date=end, ma=[5, 10, 20])
		if(len(df)==0):
			pass
		else:
			t = df[['close','ma5','ma10','ma20','change','pct_chg']]
			temp_close = t.values[0][0]
			temp_ma5 = t.values[0][1]
			temp_ma10 = t.values[0][2]
			temp_ma20 = t.values[0][3]
			temp_change = t.values[0][4]
			temp_pct_chg = t.values[0][5]
			if(math.isnan(t.values[0][1]) or math.isnan(t.values[0][2]) or math.isnan(t.values[0][3])):
				temp_ma5 = 0
				temp_ma10 = 0
				temp_ma20 = 0
				temp_change = 0
				temp_pct_chg = 0
			sql = "update `"+str(table_name)+"` set is_build='1', `close`="+str(temp_close)+",`change`="+str(temp_change)+",`pct_chg`="+str(temp_pct_chg)+",ma5 ="+str(temp_ma5)+",ma10="+str(temp_ma10)+",ma20 ="+str(temp_ma20)+" where ts_code='"+str(temp_ts_code)+"'"
			tus.mysql.update(sql)

def build_filter(tus,table_name):
	print("build_filter...")
	sql = "select count(*) from "+table_name
	cp1 = tus.mysql.select(sql)
	sql = "select count(*) from "+table_name+" where is_build = '1'"
	cp2 = tus.mysql.select(sql)
	if(len(cp1)==len(cp2)):
		print("今日过滤已完成。")
		return
	sql = "update "+table_name+" set user_filter = '1' where 1"
	tus.mysql.update(sql)
	sql = "update "+table_name+" set user_filter = '0' where market in ('创业板','科创板','CDR')"
	tus.mysql.update(sql)
	sql = "select symbol,close,ma5,ma10,ma20 from "+table_name+" where user_filter = '1'"
	data = tus.mysql.select(sql)
	count = 0
	for i in range(len(data)):
		symbol = data[i][0]
		close = data[i][1]
		ma5 = data[i][2]
		ma10 = data[i][3]
		ma20 = data[i][4]
		if(close>ma5 or close>ma10 or close>ma20):
			sql = "update "+table_name+" set user_filter = '0' where symbol = "+str(symbol)
			tus.mysql.update(sql)
			count = count + 1
	print("过滤高于均线 "+str(count)+" 条记录")

def do_search(tus,table_name):
	print("do_search...")
	status = 1
	while status == 1:
		tt = int(str(datetime.datetime.today()).split(" ")[1].split(":")[0])
		if(tt>=9 and tt<=15):
			time.sleep(0)
		else:
			print("未开盘，休息10分钟。"+str(datetime.datetime.today()))
			time.sleep(10*60)
		sql = "select symbol from "+table_name+" where user_filter = '1'"
		data = tus.mysql.select(sql)
		len_data = len(data)
		if(len_data == 0):
			print("今日没有适合个股，不参与。")
			return
		total_symbol = []
		count = 0
		for i in range(len_data):
			count = count + 1
			total_symbol.append(data[i][0])
			if(count == 100):
				count = 0
				df = tus.ts.get_realtime_quotes(total_symbol)
				t = df[['code','price']]
				total_symbol=[]
				for j in range(len(t)):
					code = t.values[j][0]
					price = t.values[j][1]
					sql = "select symbol,ma5,ma10,ma20,date,close from "+table_name+" where symbol = '"+str(code)+"'"
					j_data = tus.mysql.select(sql)
					up5 = 1 if float(price) > float(j_data[0][1]) else 0
					up10 = 1 if float(price) > float(j_data[0][2]) else 0
					up20 = 1 if float(price) > float(j_data[0][3]) else 0
					flag = up5 + up10 + up20
					change = float(price) - float(j_data[0][5])
					pct_chg = change*100/float(j_data[0][5])
					date = 0
					date_count = 0
					if(flag == 3):
						if(j_data[0][4]!=0):
							date = j_data[0][4]
							date_count = time.time() - j_data[0][4]
						else:
							date = time.time()
							date_count = 0

					sql = "update "+table_name+" set price="+str(price)+",`change`='"+str(round(change,2))+"',pct_chg='"+str(round(pct_chg,2))+"',date="+str(round(date,2))+",date_count="+str(round(date_count,2))+", up5 = "+str(up5)+",up10 = "+str(up10)+", up20 = "+str(up20)+",flag = "+str(flag)+" where symbol = '"+str(code)+"'"
					tus.mysql.update(sql)
		if(str(datetime.datetime.today()).split(" ")[1].split(":")[0]=="15"):
			status = 0
		else:
			#os.system('cls')
			print("time:"+str(datetime.datetime.today()))
			str_filter = " and user_filter = '1'"
			sql = "select count(*) from "+table_name+" where 1"
			data = tus.mysql.select(sql)
			total = data[0][0]
			sql = "select count(*) from "+table_name+" where flag <> 9"+str_filter
			data = tus.mysql.select(sql)
			contain = data[0][0]
			sql = "select count(*) from "+table_name+" where flag = 0"+str_filter
			data = tus.mysql.select(sql)
			zero = data[0][0]
			sql = "select count(*) from "+table_name+" where flag = 1"+str_filter
			data = tus.mysql.select(sql)
			one = data[0][0]
			sql = "select count(*) from "+table_name+" where flag = 2"+str_filter
			data = tus.mysql.select(sql)
			two = data[0][0]
			sql = "select count(*) from "+table_name+" where flag = 3"+str_filter
			data = tus.mysql.select(sql)
			three = data[0][0]
			pt=PrettyTable()
			pt.field_names = ["总数","符合开盘条件数","突破0条均线","突破1条均线","突破2条均线","突破3条均线"]
			pt.add_row([total,contain,zero,one,two,three])
			print(pt)
			arr = ['601952','600900','002341','601099','000725']
			sql = "select symbol from "+table_name+" where flag = 3"+str_filter
			arr_data = tus.mysql.select(sql)
			if(len(arr_data)>0):
				for i in range(len(arr_data)):
					arr.append(arr_data[i][0])
			df = ts.get_realtime_quotes(arr)
			t = df[['code','name','price','time']]
			print(t)
			

def main():
	try:
		print("main")
		subprocess.Popen('python ./test.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
		IS_BUILD = 0
		tus = Tushare()
		today = datetime.datetime.today()
		other = today - datetime.timedelta(days=40)
		start = str(other).split(" ")[0].replace("-","")
		end = str(today).split(" ")[0].replace("-","")
		print("start:"+start+" end:"+end)
		table_name = "stock_yycsx_"+end
		print("table_name:"+str(table_name))
		if(IS_BUILD==0):
			create_today_record(tus,table_name)
			make_today_base_data(tus,table_name,start,end)
			build_filter(tus,table_name)
		do_search(tus,table_name)
		
	except Exception as e:
		prcc("错误描述："+str(e)+" 错误行："+str(e.__traceback__.tb_lineno),'r')
		sys.exit()

#程序入口__main__
if __name__ == '__main__':
	pymysql.install_as_MySQLdb()
	main()


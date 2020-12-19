#!/usr/bin/python
#-*- coding: UTF-8 -*-
import os

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

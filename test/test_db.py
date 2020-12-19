#!/usr/bin/python
#-*- coding: UTF-8 -*-

import unittest

import btstock.db.db_mysql as db

class Test(unittest.TestCase):
	print("import btstock.db.db_mysql")
	mysql = db.Mysql()
	sql = "select * from stock_basic where 1"
	data = mysql.select(sql) 
	print(data)

if __name__ == "__main__":
    unittest.main()
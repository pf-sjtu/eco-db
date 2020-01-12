# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 03:50:37 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""

import MySQLdb
from utils.global_variables import ROOT_PATH, station_info

# 打开数据库连接
db = MySQLdb.connect(
        host='localhost',
        port = 3306,
        user='root',
        passwd='mmtt2356',
        db ='mysql',
        )

st_no = 0
st_name = station_info[st_no, 'db_table_name']

# 使用cursor()方法获取操作游标 
cursor = db.cursor()

# 创建并且使用数据库
cursor.execute("""create database if not exists station_db;
                  use station_db;
                  create table if not exists {};
                  use station_db;""".format(st_name, st_name))

# 如果数据表已经存在使用 execute() 方法删除表。
cursor.execute("DROP TABLE IF EXISTS EMPLOYEE")

# 创建数据表SQL语句
sql = """CREATE TABLE EMPLOYEE (
         FIRST_NAME  CHAR(20) NOT NULL,
         LAST_NAME  CHAR(20),
         AGE INT,  
         SEX CHAR(1),
         INCOME FLOAT )"""

cursor.execute(sql)

# 关闭数据库连接
db.close()
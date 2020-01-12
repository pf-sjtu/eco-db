# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 03:50:37 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""

import pandas as pd
import MySQLdb
from utils.global_variables import ROOT_PATH, station_info, col_info, clean_series


# 打开数据库连接
db = MySQLdb.connect(
        host='localhost',
        port = 3306,
        user='root',
        passwd='mmtt2356',
        db ='mysql',
        )


# 使用cursor()方法获取操作游标 
cursor = db.cursor()

# 创建并且使用数据库
cursor.execute("""create database if not exists station_db;
                  use station_db;""")

def creat_table(cursor, tb_name, col_names, col_types, key_col, unique_cols = []):
    sql_line = "create table if not exists {}(".format(tb_name)
    for col_no, col_name in enumerate(col_names):
        params = ""
        if col_name == key_col:
            params += " primary key"
        if col_name in unique_cols:
            params += " unique"
        sql_line += " {} {} {}, ".format(col_name, col_types[col_no], params)
    sql_line = sql_line.strip(', ')
    sql_line += ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    #print(sql_line)
    cursor.execute(sql_line)

def aval_col_types(station_no):
    aval_cols = clean_series(col_info['en_name'])[col_info['station'+str(station_no)] == 1]
    aval_cols = pd.DataFrame(aval_cols)
    aval_cols.reset_index(drop = True, inplace = True)
    aval_cols['type'] = 'float'
    aval_cols[aval_cols['en_name'] == 'datetime'] = 'datetime'
    return aval_cols

for ii in range(4):
    aval_cols = aval_col_types(ii)
    tb_cols = aval_cols[0:0, :]
    tb_cols[0] = ['no', ]
    tb_name = station_info.loc[ii, 'db_table_name']
    creat_table(cursor, tb_name, aval_cols['en_name'], aval_cols['type'],
                'datetime')
    print("Table for {} checked.".format(station_info.loc[ii, 'station_name2']))

'''
cursor.execute("""create table if not exists {};
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
db.close()'''
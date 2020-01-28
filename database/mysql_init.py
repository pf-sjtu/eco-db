# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 03:50:37 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""

import pandas as pd
import MySQLdb
from utils.global_variables import station_info, \
                                   col_info, \
                                   clean_series

add_id = False

def connect_db():
    # 打开数据库连接
    db = MySQLdb.connect(
            host='localhost',
            port = 3306,
            user='root',
            passwd='mmtt2356',
            db ='mysql')
    return db

def close_db(db):
    db.close()

def creat_table(cursor, tb_name, col_names, col_types):
    col_names = '`' + col_names + '`'
    sql_line = "create table if not exists {}(".format(tb_name)
    for col_name, col_type in zip(col_names, col_types):
        col_info = "{} {}, ".format(col_name, col_type)
        sql_line += col_info
    sql_line = sql_line.strip(', ')
    sql_line += ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
    #print(sql_line)
    cursor.execute(sql_line)

def add_col_front(aval_cols, col_name, col_type):
    tb_cols = aval_cols.iloc[0:1, :].copy()
    tb_cols.loc[0, :] = [col_name, col_type]
    tb_cols = tb_cols.append(aval_cols)
    return tb_cols

def aval_col_types(station_no):
    aval_cols = clean_series(col_info['en_name'])[col_info['station'+str(station_no)] == 1]
    aval_cols = pd.DataFrame(aval_cols)
    aval_cols.reset_index(drop = True, inplace = True)
    aval_cols['type'] = 'float'
    if add_id:
        aval_cols.loc[aval_cols['en_name'] == 'datetime', 'type'] = 'datetime'
        aval_cols = add_col_front(aval_cols, 'ID', 'int unsigned auto_increment primary key')
    else:
        aval_cols.loc[aval_cols['en_name'] == 'datetime', 'type'] = 'datetime primary key'
    return aval_cols

if __name__ == '__main__':
    db = connect_db()
    cursor = db.cursor()
    
    cursor.execute("""create database if not exists station_db;
                      use station_db;""")
    for ii in range(4):
        tb_cols = aval_col_types(ii)
    
        tb_name = station_info.loc[ii, 'db_table_name']
        creat_table(cursor, tb_name, tb_cols['en_name'], tb_cols['type'])
        print("Table for {} checked.".format(station_info.loc[ii, 'station_name2']))
    
    
    close_db(db)
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 03:50:37 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""

import pandas as pd
import MySQLdb

import add_path
from utils.global_variables import TEMP_DIR, STATION_NUM, EN2CLEAN_DICT, station_info, col_info, clean_series

add_id = False

def connect_db(root_database = False):
    # 打开数据库连接
    db_name = 'station_db'
    if root_database:
        db_name = 'mysql'
    db = MySQLdb.connect(
            host='localhost',
            port = 3306,
            user='root',
            passwd='mmtt2356',
            db = db_name)
    return db

def close_db(db):
    db.close()

def creat_table(db_cursor, tb_name, col_names, col_types):
    col_names = '`' + col_names + '`'
    sql_line = "create table if not exists {}(".format(tb_name)
    for col_name, col_type in zip(col_names, col_types):
        col_info = "{} {}, ".format(col_name, col_type)
        sql_line += col_info
    sql_line = sql_line.strip(', ')
    sql_line += ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
    db_cursor.execute(sql_line)
    print("表{}已创建。".format(tb_name))

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

def insert_to_db(db, csv_dir, db_table_name, col_name_series, replace = False):
    col_name_string = ('`' + col_name_series + '`,').sum().strip(',')
    db_cursor = db.cursor()
    method = 'REPLACE' if replace else 'IGNORE'
    sql_insert = """
        LOAD DATA INFILE '{}' 
            {} INTO TABLE {}
            CHARACTER SET utf8
            FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED by '\\r\\n'
            IGNORE 1 LINES
            ({});""".format(csv_dir, method, db_table_name, col_name_string)
    n_row_insert = db_cursor.execute(sql_insert)
    db.commit()
    return n_row_insert

def num_filter(string, remove_num = True):
    if remove_num:
        return ''.join(list(filter(lambda x:x not in '0123456789', string)))
    else:
        return ''.join(list(filter(lambda x:x in '0123456789', string)))

def update_table(db, table_name_str, csv_dir, df, primary_str, primary_type_str):
    cols = pd.DataFrame()
    cols['name'] = list(df.columns)
    cols['types'] = list(df.dtypes.astype(str).apply(num_filter).replace('object', 'varchar(100)'))
    cols.loc[cols['name'] == primary_str, 'types'] = primary_type_str
    creat_table(db_cursor, table_name_str, cols['name'], cols['types'])
    df.to_csv(csv_dir, encoding = 'utf-8', index = False)
    row_num = insert_to_db(db, 
                           csv_dir, 
                           table_name_str, 
                           cols['name'],
                           replace = True)
    return row_num

def delete_table(db, table_name_str):
    db_cursor = db.cursor()
    sql_drop = "DROP TABLE IF EXISTS {};".format(table_name_str)
    db_cursor.execute(sql_drop)
    print("成功删除表{}。".format(table_name_str))

if __name__ == '__main__':
    db = connect_db(True)
    db_cursor = db.cursor()
    
    db_cursor.execute("""create database if not exists station_db;
                      use station_db;""")
    for ii in range(STATION_NUM):
        tb_cols = aval_col_types(ii)
        tb_name = station_info.loc[ii, 'db_table_name']
        creat_table(db_cursor, tb_name, tb_cols['en_name'], tb_cols['type'])
    
    # create station info
    delete_table(db, 'station_info')
    s_info_tmp_dir = TEMP_DIR + '/s_info.csv'
    station_info.to_csv(s_info_tmp_dir, encoding = 'utf-8', index = False)
    s_num = update_table(db, 'station_info', s_info_tmp_dir, station_info,\
                         'station_no', 'int primary key')
    print("{}条站点信息已更新。".format(s_num))
    
    # create column info
    delete_table(db, 'col_info')
    c_info = col_info.loc[~col_info['data_label'].isin(['日期','时间']), :].reset_index(drop = True)
    c_info = c_info.reset_index(drop = False)
    c_info.rename(columns={'index': 'id'}, inplace=True) 
    c_info['db_name'] = c_info['en_name'].map(EN2CLEAN_DICT)
    c_info_tmp_dir = TEMP_DIR + '/c_info.csv'
    c_info.to_csv(c_info_tmp_dir, encoding = 'utf-8', index = False)
    c_num = update_table(db, 'col_info', c_info_tmp_dir, c_info, 
                         'id', 'int primary key')
    print("{}条表头信息已更新。".format(c_num))

    close_db(db)

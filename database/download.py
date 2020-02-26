# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 21:55:29 2019

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import numpy as np
import pandas as pd
from urllib import parse
import time
import datetime

import add_path
from utils.global_variables import STATION_NUM, TEMP_DIR, station_info, CH2EN_DICT, EN2CLEAN_DICT
from mysql_init import connect_db, close_db, insert_to_db


class Download(): 
    def __init__(self, station_no, beg_arr = [], end_arr = []):
        # Connect to the website and get ready to download.
        if type(beg_arr) == datetime.datetime and type(end_arr) == datetime.datetime:
            self.beg_dt = beg_arr
            self.end_dt = end_arr
        else:
            if len(beg_arr) == 0:
                while True:
                    try:
                        beg_arr = np.array(input("请输入数据开始时间(年 月 日 时 分):").split(), dtype = np.int16)
                        self.beg_dt = self.creat_dt(beg_arr)
                        end_arr = np.array(input("请输入数据结束时间(年 月 日 时 分):").split(), dtype = np.int16)
                        self.end_dt = self.creat_dt(end_arr)
                        break
                    except ValueError as e:
                        print('输入格式有误(', e, ')，请重新输入！')
                        continue
            else:
                self.beg_dt = self.creat_dt(beg_arr)
                self.end_dt = self.creat_dt(end_arr)
        self.station_no = station_no

        self.params = {'station_id':   station_info.loc[station_no, 'station_id'],
                       'start_time':   self.beg_dt.strftime("%Y-%m-%d %H:%M:%S"),
                       'stop_time':    self.end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                       'station_name': station_info.loc[station_no, 'station_name1']
                       }        
        self.link = 'http://ycmets.com/PC/download.asp?' + parse.urlencode(self.params)

    def creat_dt(self, arr):
        return datetime.datetime(arr[0], arr[1], arr[2], arr[3], arr[4])
    def download(self, filename = '', verbose = False):
        # Download the data from Internet and save as csv.
        # Input: filename
        self.df = pd.read_excel(self.link)
        if len(self.df) == 0:
            print("警告：当前时间段内无数据或数据已经是最新，请2-5分钟后再重试。")
            self.is_empty = True
            return np.nan
        else:
            self.is_empty = False
            self.mem_size = self.size_unify(np.sum(self.df.memory_usage()))
            if verbose: print('成功获取数据，内存大小：{}'.format(self.mem_size))
            return self.save(filename, verbose)
    def size_unify(self, bit):
        units = ['B', 'KB', 'MB', 'GB']
        unit_loc = int(np.power(bit, 1/1024))
        return '{:.2f}{}'.format(bit/np.power(1024, unit_loc), units[unit_loc])
    def save(self, filename, verbose = False):
        if filename != '':
            filename = filename.split('.')[0]
        else:
            filename = station_info.loc[self.station_no, 'db_table_name'] + \
                '_' + self.beg_dt.strftime("%Y%m%d-%H%M%S") + \
                '_' + self.end_dt.strftime("%Y%m%d-%H%M%S")
        self.csv_dir = "{}/{}.csv".format(TEMP_DIR, filename)
        self.df = self.data_pre_process(self.df)
        self.df.to_csv(self.csv_dir, index = False, encoding = 'utf-8')
        if verbose: print('成功保存数据，位置：{}'.format(self.csv_dir))
        return self.csv_dir
    def data_pre_process(self, df):
        df = df.reindex(columns = ['datetime'] + df.columns.tolist())
        df['datetime'] = df.apply(lambda x: datetime.datetime.strptime(x['日期'] + ' ' + x['时间'], "%Y-%m-%d %H:%M"), axis = 1)
        df.drop(['日期','时间'], axis = 1, inplace = True)
        df.columns = df.columns.map(CH2EN_DICT).map(EN2CLEAN_DICT)
        df = df[df.columns[~df.columns.isnull()]]
        return df
    def insert_to_db(self, db):
        if not self.is_empty:
            n_row_insert = insert_to_db(db, 
                                        self.csv_dir, 
                                        station_info.loc[self.station_no, 'db_table_name'], 
                                        self.df.columns.to_series())

            print("成功向数据库中插入数据条数：" + str(n_row_insert))
        else:
            print("向数据库中插入数据失败：数据为空。")

def check_station(db, db_table_name): 
    db_cursor = db.cursor()
    # check empty
    db_cursor.execute("SELECT COUNT(*) FROM {};".format(db_table_name))
    n_row_table = db_cursor.fetchone()
    if n_row_table[0] == 0:
        return np.nan
    else:
        datetime_firstlast = []
        for order in ['ASC', 'DESC']:
            sql_datetime_edge = "SELECT datetime FROM {} ORDER BY datetime {} LIMIT 1".format(db_table_name, order)
            db_cursor.execute(sql_datetime_edge)
            datetime_firstlast += [db_cursor.fetchone()[0]]
        return datetime_firstlast

def download_step(station_no, dt_beg, dt_end, verbose = False):
    print("正在下载[{}]数据（{}->{})...".format(station_info.loc[station_no, 'station_name2'], 
                                                dt_beg.strftime("%Y/%m/%d-%H:%M:%S"), 
                                                dt_end.strftime("%Y/%m/%d-%H:%M:%S")))
    dl = Download(station_no, dt_beg, dt_end)
    dl.download(verbose = verbose)
    dl.insert_to_db(db)

def auto_download_period(station_no, datetime_beg, datetime_end, max_data_int, verbose = False):
    while datetime_beg + max_data_int < datetime_end:
        download_step(station_no, datetime_beg, datetime_beg + max_data_int, verbose)
        datetime_beg += max_data_int
    download_step(station_no, datetime_beg, datetime_end, verbose)

def auto_download(db, datetime_beg = datetime.datetime(2020, 1, 1), 
                  int_min = 5, max_data_int = datetime.timedelta(days=7), 
                  verbose = False):
    print('正在自动更新数据库数据，时间间隔：每{}分钟...'.format(int_min))
    db_cursor = db.cursor()
    # check empty
    db_cursor.execute("USE station_db;")
    while(True):
        for station_no in range(STATION_NUM):
            db_table_name = station_info.loc[station_no, 'db_table_name']
            datetime_firstlast = check_station(db, db_table_name)
            # if the table is empty, skip
            if type(datetime_firstlast) != list: continue
            datetime_first, datetime_last = datetime_firstlast
            # if early data missing
            if datetime_first > datetime_beg + max_data_int:
                print('之前数据有缺失（{}->{}），正在补充...'.format(datetime_beg.strftime("%Y/%m/%d-%H:%M:%S"),
                                              datetime_first.strftime("%Y/%m/%d-%H:%M:%S")))
                auto_download_period(station_no, datetime_beg, datetime_first, max_data_int, verbose = verbose)
            # if new data is not up to date
            datetime_now = datetime.datetime.now()
            if datetime_now > datetime_last:
                auto_download_period(station_no, datetime_last, datetime_now, max_data_int, verbose = verbose)
        print('本次同步完成（{}->{}），休眠{}分钟。'.format(datetime_beg.strftime("%Y/%m/%d-%H:%M:%S"),
                                              datetime_now.strftime("%Y/%m/%d-%H:%M:%S"),
                                              int_min))
        for sleep_period in range (int_min * 12):
            time.sleep(5)

    
def test(db):
    print('In test mode...')
    beg_arr = [2019, 12, 8, 12, 0]
    end_arr = [2019, 12, 8, 13, 0]
    dl = Download(3, beg_arr, end_arr)
    dl.download(verbose = True)
    dl.insert_to_db(db)

if __name__ == '__main__':
    db = connect_db()
    auto_download(db)
    #test(db)
    close_db(db)





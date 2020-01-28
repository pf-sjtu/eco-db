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
from utils.global_variables import TEMP_DIR, station_info, CH2EN_DICT, EN2CLEAN_DICT
from database.mysql_init import connect_db, close_db


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
        col_name_string = ('`' + self.df.columns.to_series() + '`,').sum().strip(',')
        db_table_name = station_info.loc[self.station_no, 'db_table_name']
        
        db_cursor = db.cursor()
        db_cursor.execute("USE station_db;")
        sql_insert = """
            LOAD DATA INFILE '{}' 
                IGNORE INTO TABLE {}
                CHARACTER SET utf8
                FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED by '\\r\\n'
                IGNORE 1 LINES
                ({});""".format(self.csv_dir, db_table_name, col_name_string)
        n_row_insert = db_cursor.execute(sql_insert)
        db.commit()
        print("成功向数据库中插入数据条数：" + str(n_row_insert))

'''
def check_n_row(db, db_table_name):
    db_cursor = db.cursor()
    # check empty
    n_row_table = db_cursor.fetchone(db_cursor.execute("SELECT COUNT(*) FROM {};".format(db_table_name)))
    if n_row_table == 0:
        return {'complete': True, 'empty': True, 'incomplete_beg': np.nan, 'incomplete_end': np.nan}
    else:
'''
def check_station(db, db_table_name): 
    db_cursor = db.cursor()
    # check empty
    db_cursor.execute("SELECT COUNT(*) FROM {};".format(db_table_name))
    n_row_table = db_cursor.fetchone()
    if n_row_table[0] == 0:
        return np.nan
    else:
        sql_datetime_last = "SELECT datetime FROM {} ORDER BY datetime DESC LIMIT 1;".format(db_table_name)
        print(sql_datetime_last)
        db_cursor.execute(sql_datetime_last)
        datetime_last = db_cursor.fetchone()[0]
        return datetime_last

def download_step(station_no, dt_beg, dt_end):
    print("正在下载{}\t自{}至{}的数据...".format(station_info.loc[station_no, 'station_name2'], 
                                                dt_beg.strftime("%Y/%m/%d-%H:%M:%S"), 
                                                dt_end.strftime("%Y/%m/%d-%H:%M:%S")))
    dl = Download(station_no, dt_beg, dt_end)
    dl.download(verbose = True)
    dl.insert_to_db(db)
                    
def auto_download(db, int_min = 5, max_data_int = datetime.timedelta(days=7)):
    print('正在自动更新数据库数据，时间间隔：每{}分钟...'.format(int_min))
    db_cursor = db.cursor()
    # check empty
    db_cursor.execute("USE station_db;")
    while(True):
        for station_no in range(4):
            db_table_name = station_info.loc[station_no, 'db_table_name']
            datetime_last = check_station(db, db_table_name)
            if datetime_last == np.nan: continue
            datetime_now = datetime.datetime.now()
            if type(datetime_last) == datetime.datetime and datetime_now > datetime_last:
                while datetime_last + max_data_int < datetime_now:
                    datetime_now = datetime_last + max_data_int
                    download_step(station_no, datetime_last, datetime_now)
                    datetime_last = datetime_now
                    datetime_now = datetime.datetime.now()
                download_step(station_no, datetime_last, datetime_now)
        print('完成，休眠{}分钟。'.format(int_min))
        time.sleep(int_min * 60)

    
def test():
    print('In test mode...')
    beg_arr = [2019, 12, 8, 12, 0]
    end_arr = [2019, 12, 8, 13, 0]
    dl = Download(0, beg_arr, end_arr)
    dl.download(verbose = True)
    
    db = connect_db()
    dl.insert_to_db(db)
    close_db(db)

if __name__ == '__main__':
    db = connect_db()
    auto_download(db)
    close_db(db)





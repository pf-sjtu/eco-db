# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 21:55:29 2019

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import numpy as np
import pandas as pd
import requests
from urllib import parse
import datetime
#http://ycmets.com/PC/download.asp?station_id=152&start_time=2019-12-08 00:00&stop_time=2019-12-08 21:51:30&station_name=崇明01
from utils.global_variables import ROOT_PATH, TEMP_DIR, station_info, CH2EN_DICT, EN2CLEAN_DICT

class Download(): 
    def __init__(self, station_no, beg_arr = [], end_arr = []):
        # Connect to the website and get ready to download.
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
                        
        print(self.link)
    def creat_dt(self, arr):
        return datetime.datetime(arr[0], arr[1], arr[2], arr[3], arr[4])
    def download(self, filename = '', verbose = False):
        # Download the data from Internet and save as csv.
        # Input: filename
        self.df = pd.read_excel(self.link)
        self.mem_size = self.size_unify(np.sum(self.df.memory_usage()))
        if verbose: print('成功获取数据，内存大小： {}'.format(self.mem_size))
        return self.save(filename, verbose)
    def size_unify(self, bit):
        units = ['B', 'KB', 'MB', 'GB']
        unit_loc = int(np.power(bit, 1/1024))
        return '{:.2f}{}'.format(bit/np.power(1024, unit_loc), units[unit_loc])
    def save(self, filename, verbose = False):
        if filename != '':
            filename = filename.split('.')[0]
        else:
            filename = station_info.loc[self.station_no, 'station_name2'] + \
                '_' + self.beg_dt.strftime("%Y-%m-%d-%H-%M-%S") + \
                '_' + self.end_dt.strftime("%Y-%m-%d-%H-%M-%S")
        csv_name = "{}\{}.csv".format(TEMP_DIR, filename)
        self.data_pre_process(self.df)
        self.df.to_csv(csv_name, index = False, encoding = 'utf-8')
        if verbose: print('成功保存数据，位置： {}'.format(csv_name))
        return csv_name
    def data_pre_process(self, df):
        df.reindex(columns = ['datetime'] + df.index.tolist())
        df['datetime'] = df.apply(lambda x: datetime.datetime.strptime(x['日期'] + ' ' + x['时间'], "%Y-%m-%d %H:%M"), axis = 1)
        df.drop(['日期','时间'], axis = 1, inplace = True)
        df.columns = df.columns.map(CH2EN_DICT).map(EN2CLEAN_DICT)
    
def test():
    print('In test mode...')
    beg_arr = [2019, 12, 8, 12, 0]
    end_arr = [2019, 12, 8, 13, 0]
    dl = Download(0, beg_arr, end_arr)
    return dl.download(verbose = True)

if __name__ == '__main__':
    test()





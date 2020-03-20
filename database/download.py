# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 21:55:29 2019

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import numpy as np
import pandas as pd
from urllib import parse
import urllib.error
import time
import datetime
import argparse

import add_path
from utils.global_variables import (
    TEMP_DIR,
    STATION_NUM,
    STATION_NUM_ORI,
    station_info,
    station_info_ori,
    col_info_ori,
    CH2EN_DICT,
    EN2CLEAN_DICT,
    rm_tmp_file,
)
from database.mysql_init import connect_db, close_db, init_db, insert_to_db
from utils.color_log import Logger


class Download:
    def __init__(self, station_no_ori, beg_arr=[], end_arr=[]):
        self.info = [self.generate_links(station_no_ori, beg_arr, end_arr)]
        for ii in range(STATION_NUM_ORI):
            s_merge_to_no = station_info_ori.loc[ii, "merge_to_no"]
            if s_merge_to_no == station_no_ori:
                self.info.append(self.generate_links(ii, beg_arr, end_arr))

    def generate_links(self, station_no_ori, beg_arr=[], end_arr=[]):
        if type(beg_arr) == datetime.datetime and type(end_arr) == datetime.datetime:
            beg_dt = beg_arr
            end_dt = end_arr
        else:
            if len(beg_arr) == 0:
                while True:
                    try:
                        beg_arr = np.array(
                            # input("请输入数据开始时间(年 月 日 时 分):").split(), dtype=np.int16
                            input(
                                "Please enter start time of data (yyyy, mm, dd):"
                            ).split(),
                            dtype=np.int16,
                        )
                        beg_dt = self.creat_dt(beg_arr)
                        end_arr = np.array(
                            # input("请输入数据结束时间(年 月 日 时 分):").split(), dtype=np.int16
                            input(
                                "Please enter end time of data (yyyy, mm, dd):"
                            ).split(),
                            dtype=np.int16,
                        )
                        end_dt = self.creat_dt(end_arr)
                        break
                    except ValueError as e:
                        # print("输入格式有误(", e, ")，请重新输入！")
                        Logger.log_fail(
                            "FAILURE:",
                            "wrong format of input, please retry. {}.".format(e),
                        )
                        continue
            else:
                beg_dt = self.creat_dt(beg_arr)
                end_dt = self.creat_dt(end_arr)

        params = {
            "station_id": station_info_ori.loc[station_no_ori, "station_id"],
            "start_time": beg_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "stop_time": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "station_name": station_info_ori.loc[station_no_ori, "station_name1"],
        }
        return {
            "link": "http://ycmets.com/PC/download.asp?" + parse.urlencode(params),
            "params": params,
            "station_no_ori": station_no_ori,
            "beg_dt": beg_dt,
            "end_dt": end_dt,
        }

    def creat_dt(self, arr):
        return datetime.datetime(arr[0], arr[1], arr[2], arr[3], arr[4])

    def download(self, filename="", verbose=False):
        # Download the data from Internet and save as csv.
        # Input: filename
        count = 0
        try:
            for no, info in enumerate(self.info):
                online_data = pd.read_excel(info["link"])
                if len(online_data) != 0:
                    count += 1
                    station_no_ori = info["station_no_ori"]
                    required_labels = col_info_ori.loc[
                        col_info_ori["station" + str(station_no_ori)] == 1,
                        "label" + str(station_no_ori),
                    ]
                    required_labels = ["日期", "时间"] + list(required_labels)[1:]
                    online_data = self.data_pre_process(online_data[required_labels])
                    if count == 1:
                        self.df = online_data
                    else:
                        self.df = self.df.merge(online_data, on="datetime", how="outer")
        except urllib.error.URLError as e:
            Logger.log_fail("FAILURE:", "error in network connection. {}".format(e))
            self.is_empty = True
            return np.nan
        if count == 0:
            Logger.log_warn("WARNING:", "no more recent data available in the period.")
            # print("警告：本时间段内暂无更新数据。")
            self.is_empty = True
            return np.nan
        else:
            self.is_empty = False
            self.mem_size = self.size_unify(np.sum(self.df.memory_usage()))
            if verbose:
                Logger.log_high(
                    "FETCH:", "data fetched, size:{}.".format(self.mem_size)
                )
                # print("成功获取数据，内存大小：{}".format(self.mem_size))
            return self.save(filename, verbose)

    def size_unify(self, bit):
        units = ["B", "KB", "MB", "GB"]
        unit_loc = int(np.power(bit, 1 / 1024))
        return "{:.2f}{}".format(bit / np.power(1024, unit_loc), units[unit_loc])

    def save(self, filename, verbose=False):
        if filename != "":
            filename = filename.split(".")[0]
        else:
            filename = (
                station_info_ori.loc[self.info[0]["station_no_ori"], "db_table_name"]
                + "_"
                + self.info[0]["beg_dt"].strftime("%Y%m%d-%H%M%S")
                + "_"
                + self.info[0]["end_dt"].strftime("%Y%m%d-%H%M%S")
            )
        self.csv_dir = "{}/{}.csv".format(TEMP_DIR, filename)
        self.df.to_csv(self.csv_dir, index=False, encoding="utf-8")
        if verbose:
            Logger.log_high("SAVE:", "data saved, location:{}.".format(self.csv_dir))
            # print("成功保存数据，位置：{}".format(self.csv_dir))
        return self.csv_dir

    def data_pre_process(self, df):
        df = df.reindex(columns=["datetime"] + df.columns.tolist())
        df["datetime"] = df.apply(
            lambda x: datetime.datetime.strptime(
                x["日期"] + " " + x["时间"], "%Y-%m-%d %H:%M"
            ),
            axis=1,
        )
        df.drop(["日期", "时间"], axis=1, inplace=True)
        df.columns = df.columns.map(CH2EN_DICT).map(EN2CLEAN_DICT)
        df = df[df.columns[~df.columns.isnull()]]
        return df

    def insert_to_db(self, db):
        if not self.is_empty:
            n_row_insert = insert_to_db(
                db,
                self.csv_dir,
                station_info_ori.loc[self.info[0]["station_no_ori"], "db_table_name"],
                self.df.columns.to_series(),
            )
            Logger.log_high(
                "INSERT:",
                "insert into database, number of lines:{}.".format(n_row_insert),
            )
            # print("成功向数据库中插入数据条数：" + str(n_row_insert))
            rm_tmp_file(self.csv_dir)
        else:
            Logger.log_warn(
                "WARNING:", "fail to insert into database, for data is empty."
            )
            # print("向数据库中插入数据失败：数据为空。")


def station_no_to_ori(station_no):
    db_table_name = station_info.loc[station_no, "db_table_name"]
    for ii, name in enumerate(station_info_ori["db_table_name"]):
        if db_table_name == name:
            station_no_ori = ii
            break
    return station_no_ori


def check_station(db, db_table_name):
    db_cursor = db.cursor()
    # check empty
    db_cursor.execute("SELECT COUNT(*) FROM {};".format(db_table_name))
    n_row_table = db_cursor.fetchone()
    if n_row_table[0] == 0:
        return np.nan
    else:
        datetime_firstlast = []
        for order in ["ASC", "DESC"]:
            sql_datetime_edge = "SELECT datetime FROM {} ORDER BY datetime {} LIMIT 1".format(
                db_table_name, order
            )
            db_cursor.execute(sql_datetime_edge)
            datetime_firstlast += [db_cursor.fetchone()[0]]
        return datetime_firstlast


def download_step(db, station_no, dt_beg, dt_end, verbose=False):
    print(
        "Downloading from [{}]({}->{})...".format(
            station_info.loc[station_no, "db_table_name"],
            dt_beg.strftime("%Y/%m/%d-%H:%M:%S"),
            dt_end.strftime("%Y/%m/%d-%H:%M:%S"),
        )
    )
    # print(
    #     "正在下载[{}]数据（{}->{})...".format(
    #         station_info.loc[station_no, "station_name2"],
    #         dt_beg.strftime("%Y/%m/%d-%H:%M:%S"),
    #         dt_end.strftime("%Y/%m/%d-%H:%M:%S"),
    #     )
    # )
    station_no_ori = station_no_to_ori(station_no)
    dl = Download(station_no_ori, dt_beg, dt_end)
    dl.download(verbose=verbose)
    dl.insert_to_db(db)


def auto_download_period(
    db, station_no, datetime_beg, datetime_end, max_data_int, verbose=False
):
    while datetime_beg + max_data_int < datetime_end:
        download_step(
            db, station_no, datetime_beg, datetime_beg + max_data_int, verbose
        )
        datetime_beg += max_data_int
    download_step(db, station_no, datetime_beg, datetime_end, verbose)


def auto_download(
    db,
    datetime_beg=datetime.datetime(2020, 1, 1),
    int_min=1,
    max_data_int=datetime.timedelta(days=7),
    verbose=False,
):
    Logger.log_high(
        "LOOP:",
        "updating database automatically, interval:{} minute(s).".format(int_min),
    )
    # print("正在自动更新数据库数据，时间间隔：每{}分钟...".format(int_min))
    # check empty
    while True:
        for station_no in range(STATION_NUM):
            db_table_name = station_info.loc[station_no, "db_table_name"]
            datetime_firstlast = check_station(db, db_table_name)
            # if the table is empty, skip
            if type(datetime_firstlast) != list:
                continue
            datetime_first, datetime_last = datetime_firstlast
            # if early data missing
            if datetime_first > datetime_beg + max_data_int:
                Logger.log_warn(
                    "WARNING:",
                    "previous data missing ({}->{}), re-downloading...".format(
                        datetime_beg.strftime("%Y/%m/%d-%H:%M:%S"),
                        datetime_first.strftime("%Y/%m/%d-%H:%M:%S"),
                    ),
                )
                # print(
                #     "之前数据有缺失（{}->{}），正在补充...".format(
                #         datetime_beg.strftime("%Y/%m/%d-%H:%M:%S"),
                #         datetime_first.strftime("%Y/%m/%d-%H:%M:%S"),
                #     )
                # )
                auto_download_period(
                    db,
                    station_no,
                    datetime_beg,
                    datetime_first,
                    max_data_int,
                    verbose=verbose,
                )
            # if new data is not up to date
            datetime_now = datetime.datetime.now()
            if datetime_now > datetime_last:
                auto_download_period(
                    db,
                    station_no,
                    datetime_last,
                    datetime_now,
                    max_data_int,
                    verbose=verbose,
                )
        datetime_now = datetime.datetime.now()
        print(
            "Synchronization step finished ({}->{}), sleeps for {} minute(s).".format(
                datetime_beg.strftime("%Y/%m/%d-%H:%M:%S"),
                datetime_now.strftime("%Y/%m/%d-%H:%M:%S"),
                int_min,
            )
        )
        # print(
        #     "本次同步完成（{}->{}），休眠{}分钟。".format(
        #         datetime_beg.strftime("%Y/%m/%d-%H:%M:%S"),
        #         datetime_now.strftime("%Y/%m/%d-%H:%M:%S"),
        #         int_min,
        #     )
        # )
        for sleep_period in range(int_min * 12):
            time.sleep(5)


def test_download(db, beg_arr, end_arr):
    # print('In test mode...')
    # beg_arr = [2020, 1, 2, 12, 0]
    # end_arr = [2020, 1, 2, 13, 0]
    for ii in range(STATION_NUM):
        station_no_ori = station_no_to_ori(ii)
        dl = Download(station_no_ori, beg_arr, end_arr)
        # print(dl.info[0]['station_no_ori'], dl.info[0]['link']
        dl.download(verbose=True)
        dl.insert_to_db(db)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="loop",
        choices=["init", "loop", "once"],
        help='Input "loop" or ignore the parameter to download the data recursively to keep the database up-to-date; Or "init" to init the database when you first deploy the program (will turn to "loop" mode after that); Input "once" to just download once. (loop)',
    )
    argparser.add_argument(
        "-i",
        "--int",
        type=int,
        default=1,
        help='The interval (minutes) of two downloads in "loop" mode. (1)',
    )
    argparser.add_argument(
        "-a",
        "--max",
        type=int,
        default=7,
        help="The max interval (days) of the data in one download. (7)",
    )
    argparser.add_argument(
        "-b",
        "--beg",
        nargs="+",
        type=int,
        default=[2020, 1, 2, 12, 0],
        help='The datetime of the begin of data in "init" and "once" mode. (2020 1 2 12 0)',
    )
    argparser.add_argument(
        "-e",
        "--end",
        nargs="+",
        type=int,
        default=[2020, 1, 2, 13, 0],
        help='The datetime of the end of data in "init" and "once" mode. (2020 1 2 13 0)',
    )

    args = argparser.parse_args()

    db = connect_db()

    if args.mode == "init":
        init_db()
        test_download(db, args.beg, args.end)
        datetime_beg = datetime.datetime(2017, 1, 1)
        auto_download(
            db=db,
            datetime_beg=datetime_beg,
            int_min=args.int,
            max_data_int=datetime.timedelta(days=args.max),
            verbose=False,
        )
    elif args.mode == "loop":
        datetime_beg = datetime.datetime(2020, 1, 1)
        auto_download(
            db=db,
            datetime_beg=datetime_beg,
            int_min=args.int,
            max_data_int=datetime.timedelta(days=args.max),
            verbose=False,
        )
    elif args.mode == "once":
        test_download(db, args.beg, args.end)

    close_db(db)

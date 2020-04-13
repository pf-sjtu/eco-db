# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 11:27:09 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import pandas as pd

import add_path
from database.mysql_init import connect_db, close_db
from utils.global_variables import station_info

"""
sta_i = 0
dt_str_span = dt_str_span = ["2019-01-01 00:00:00", "2019-01-02 00:00:00"]
"""


def download_station_csv(sta_i, dt_str_span):
    db_table_name = station_info.loc[sta_i, "db_table_name"]
    station_name2 = station_info.loc[sta_i, "station_name2"]
    db = connect_db()
    db_curser = db.cursor()

    sql_code = "SELECT * FROM {} WHERE datetime >= '{}' AND datetime < '{}'".format(
        db_table_name, dt_str_span[0], dt_str_span[1]
    )

    db_curser.execute(sql_code)
    data = db_curser.fetchall()

    sql_code = "SELECT en_name, unit FROM col_info WHERE station{} = 1".format(sta_i)
    db_curser.execute(sql_code)
    cols = db_curser.fetchall()
    cols = pd.Series(cols).apply(
        lambda x: x[0] + " (" + x[1] + ")" if len(x[1]) else x[0]
    )

    close_db(db)

    df = pd.DataFrame(data=data, columns=cols)
    filename = (
        "{}_原始数据_{}_{}.csv".format(station_name2, dt_str_span[0], dt_str_span[1])
        .replace(":", "")
        .replace("-", "")
        .replace(" ", "")
    )
    df.to_csv(filename, index=False, encoding="GBK")


for sta_i in range(station_info.shape[0]):
    dt_str_span = ["2019-01-01 00:00:00", "2020-01-01 00:00:00"]
    download_station_csv(sta_i, dt_str_span)

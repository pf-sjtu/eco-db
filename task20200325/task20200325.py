# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 10:47:30 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""

import pandas as pd, numpy as np, datetime
import scipy.stats as stats

# import matplotlib.pyplot as plt


class MAD:
    @staticmethod
    def mad_thd(series, thresh=3):
        # if type(series) is list:
        #     series = np.asarray(series)
        # if len(series.shape) == 1:
        #     series = series[:, None]
        series = np.array(series)
        series = series[~np.isnan(series)]
        med = np.median(series)
        dev = series - med
        abs_dev = np.absolute(dev)
        med_abs_dev = np.median(abs_dev)
        thd = [
            med - med_abs_dev / stats.norm.ppf(0.75) * thresh,
            med + med_abs_dev / stats.norm.ppf(0.75) * thresh,
        ]
        return thd

    @staticmethod
    def gen_desc(df, thresh=3, exclude_col=["datetime"]):
        if len(exclude_col):
            df = df.copy()
            df.drop(columns=exclude_col, inplace=True)
        df_desc = df.describe()
        df_desc.loc["50%-25%", :] = df_desc.loc["50%", :] - df_desc.loc["25%", :]
        df_desc.loc["75%-50%", :] = df_desc.loc["75%", :] - df_desc.loc["50%", :]
        df_desc.loc["L/R", :] = df_desc.loc["50%-25%", :] / df_desc.loc["75%-50%", :]
        mad = df.apply(MAD.mad_thd, axis=0, args=(thresh,))
        df_desc.loc["mad_thd_L", :] = mad.apply(lambda x: x[0])
        df_desc.loc["mad_thd_R", :] = mad.apply(lambda x: x[1])
        return df_desc

    @staticmethod
    def mad_trim(df, thresh=3, exclude_col=["datetime"], method="drop"):
        df = df.copy()
        df_desc = MAD.gen_desc(df=df, thresh=thresh, exclude_col=exclude_col)
        if method == "drop":
            for col_name in df_desc:
                df[col_name] = np.where(
                    (df[col_name] >= df_desc.loc["mad_thd_L", col_name])
                    & (df[col_name] <= df_desc.loc["mad_thd_R", col_name]),
                    df[col_name],
                    np.nan,
                )
        elif method == "clip":
            for col_name in df_desc:
                df[col_name] = np.clip(
                    df[col_name],
                    df_desc.loc["mad_thd_L", col_name],
                    df_desc.loc["mad_thd_R", col_name],
                )
        return df


def zero2nan(series):
    return np.where(series == 0, np.nan, series)


def minus2nan(series):
    return np.where(series <= 0, np.nan, series)


def gen_day_data(min_data, aggfunc="mean"):
    min_data2 = min_data.copy()
    min_data2.reset_index(inplace=True)
    min_data2["datetime"] = pd.to_datetime(
        min_data2["datetime"], format="%Y/%m/%d %H:%M"
    )
    min_data2["datetime"] = min_data2["datetime"].apply(
        lambda x: datetime.datetime.strftime(x, "%Y-%m-%d")
    )
    day_data = min_data2.pivot_table(index="datetime", aggfunc=aggfunc)
    return day_data


data_dicts = [
    {"name": "中山公园站", "csv": "长宁区中山公园观测站_原始数据_20190101000000_20200101000000.csv"},
    {"name": "崇明站", "csv": "崇明区观测站_原始数据_20190101000000_20200101000000.csv"},
    {"name": "金海站", "csv": "浦东新区金海湿地公园观测站_原始数据_20190101000000_20200101000000.csv"},
]

# key_cols = ["PM10 (μg/cm3)", "PM2.5 (μg/cm3)", "SO2 (ppb)", "NOX (ppb)", "NO (ppb)", "CO (ppb)", "O3 (ppb)"]

for data_dicts in data_dicts:
    min_data_ori = pd.read_csv(
        data_dicts["csv"], encoding="GBK", dtype={"datetime": str},
    )
    min_data_ori.set_index("datetime", inplace=True)
    min_data_ori = min_data_ori.apply(minus2nan, axis=0)
    min_data_ori_desc = min_data_ori.describe()
    # min_data_drop = MAD.mad_trim(
    #     df=min_data_ori, thresh=3, exclude_col=["datetime"], method="drop"
    # )
    # min_data_drop_desc = min_data_drop.describe()
    min_data_clip = MAD.mad_trim(
        df=min_data_ori, thresh=3, exclude_col=[], method="clip"
    )
    min_data_clip_desc = min_data_clip.describe()

    day_data = gen_day_data(min_data_clip)
    day_data_desc = day_data.describe()

    col_order = [i for i in min_data_ori.columns if i in day_data.columns]

    day_data[col_order].to_csv(
        "2019年{}_日平均数据.csv".format(data_dicts["name"]), encoding="GBK", index=True
    )
    min_data_clip_desc[col_order].to_csv(
        "2019年{}_分钟数据特征.csv".format(data_dicts["name"]), encoding="GBK", index=True
    )
    day_data_desc[col_order].to_csv(
        "2019年{}_日平均数据特征.csv".format(data_dicts["name"]), encoding="GBK", index=True
    )
    print("{} finished".format(data_dicts["name"]))

# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 15:42:07 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import add_path
from constants import (
    pollutants,
    stations,
    years,
    seasons,
)

import numpy as np, pandas as pd
import datetime
from scipy import stats


class Wash:
    def __init__(self, series, P=0.99, verbose=False):
        self.series = np.array(series)
        self.series_full = self.series[
            (~np.isnan(self.series)) & (~np.isinf(self.series))
        ]
        self.mean = np.mean(self.series_full)
        self.sigma = np.std(self.series_full)
        self.change_P(P=P)
        self.change_verbose(verbose=verbose)

    def change_P(self, P):
        self.P = P
        Z_span = [stats.norm.ppf((1 - P) / 2)]
        Z_span.append(-Z_span[0])
        self.Z_span = np.array(Z_span)

    def change_verbose(self, verbose):
        self.verbose = verbose

    def sigma_trim(self, method="clip"):
        X_span = self.Z_span * self.sigma + self.mean
        return self.span_trim(X_span, method)

    def percentile_trim(self, method="clip"):
        X_span = np.array(
            [
                np.percentile(self.series_full, (1 - self.P) / 2 * 100),
                np.percentile(self.series_full, (1 + self.P) / 2 * 100),
            ]
        )
        return self.span_trim(X_span, method)

    def MAD_trim(self, method="clip"):
        median = np.percentile(self.series_full, 50)
        AD = np.abs(self.series_full - median)
        MAD = np.percentile(AD, 50)
        MAD_sigma = MAD / stats.norm.ppf(0.75)
        X_span = self.Z_span * MAD_sigma + self.mean
        return self.span_trim(X_span, method)

    def span_trim(self, X_span, method="clip"):
        if method == "drop":
            series2 = self.series[
                (self.series >= X_span[0]) & (self.series <= X_span[1])
            ]
        elif method == "clip":
            series2 = np.clip(self.series, X_span[0], X_span[1])
        elif method == "nan":
            series2 = np.where(
                (self.series >= X_span[0]) & (self.series <= X_span[1]),
                self.series,
                np.nan,
            )
        if self.verbose:
            return series2, X_span
        else:
            return series2


def nan_mean(series):
    series = np.array(series)
    series_full = series[~np.isnan(series)]
    if len(series_full) > 0:
        mean = np.mean(series_full)
    else:
        mean = np.nan
    return mean


def gen_period_data(min_data, dt_format="%Y-%m-%d %H"):
    min_data2 = min_data.copy()
    # min_data2.reset_index(inplace=True)
    # min_data2["datetime"] = pd.to_datetime(
    #     min_data2["datetime"], format="%Y-%m-%d %H:%M"
    # )
    min_data2["datetime"] = min_data2["datetime"].apply(
        lambda x: datetime.datetime.strftime(x, dt_format)
    )
    df = min_data2.pivot_table(index="datetime", aggfunc=nan_mean, dropna=False)
    return df


def gen_sta_period_data(min_data, dt_format="%Y-%m-%d %H"):
    df = min_data[["sta_i", "datetime"] + pollutants]
    df_per = ""
    for sta_i in range(len(stations)):
        df_per_sta = gen_period_data(
            df[df["sta_i"] == sta_i], dt_format=dt_format
        ).reset_index()
        if type(df_per) == str:
            df_per = df_per_sta
        else:
            df_per = pd.concat([df_per, df_per_sta], join="inner")
    return df_per


def sta_i_desc(df):
    desc = ""
    for sta_i in range(len(stations)):
        desc_sta = (
            df.loc[df["sta_i"] == sta_i, pollutants]
            .describe()
            .reset_index()
            .rename(columns={"index": "item"})
        )
        desc_sta["sta_i"] = sta_i
        if type(desc) == str:
            desc = desc_sta
        else:
            desc = pd.concat([desc, desc_sta], join="inner")
    desc = desc[["sta_i", "item"] + pollutants]
    return desc


def nan_mean_fill(df, columns=None):
    if columns == None:
        # exclude_type = [object, list, dict, datetime.datetime]
        # columns = df.columns[[i not in exclude_type for i in df.dtypes]]
        include_type = ["float64", "float32", "float"]
        columns = df.columns[[i in include_type for i in df.dtypes]]
    elif type(columns) == str:
        columns = [columns]
    df2 = df.copy()
    df_ffill = df2[columns].fillna(method="ffill").fillna(method="bfill")
    df_bfill = df2[columns].fillna(method="bfill").fillna(method="ffill")
    df2[columns] = (df_ffill + df_bfill) / 2
    return df2


def sta_nan_mean_fill(df, columns=None):
    df_filled = ""
    for sta_i in range(len(stations)):
        df_filled_sta = nan_mean_fill(df[df["sta_i"] == sta_i], columns=columns)
        if type(df_filled) == str:
            df_filled = df_filled_sta
        else:
            df_filled = pd.concat([df_filled, df_filled_sta], join="inner")
    return df_filled


def dt_slice(df, dt0="0000-00-00 00:00:00", dt1="9999-12-31 23:59:59"):
    if type(dt0) == str:
        dt0 = datetime.datetime.strptime(dt0, "%Y-%m-%d %H:%M:%S")
    if type(dt1) == str:
        dt1 = datetime.datetime.strptime(dt1, "%Y-%m-%d %H:%M:%S")
    return df[(df["datetime"] > dt0) & (df["datetime"] < dt1)]


if __name__ == "__main__":
    # t = [
    #     0,
    #     np.nan,
    #     np.nan,
    #     200,
    #     200,
    #     200,
    #     200,
    #     200,
    #     200,
    #     200,
    #     200,
    #     200,
    #     200,
    #     200,
    #     200,
    #     400,
    # ]
    # wt = Wash(t, verbose=True)
    # tws1, X_span1 = wt.sigma_trim(method="drop")
    # tws2, X_span2 = wt.percentile_trim(method="drop")
    # tws3, X_span3 = wt.MAD_trim(method="drop")

    df = pd.DataFrame(
        [
            [np.nan, 2, 2, 0],
            [3, 4, np.nan, 1],
            [np.nan, np.nan, np.nan, 5],
            [np.nan, 3, np.nan, 4],
        ],
        columns=list("ABCD"),
    )
    df2 = nan_mean_fill(df)

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
        return np.mean(series_full)
    else:
        return np.nan


def gen_period_data(min_data, dt_format="%Y-%m-%d %H"):
    min_data2 = min_data.copy()
    min_data2.reset_index(inplace=True)
    min_data2["datetime"] = pd.to_datetime(
        min_data2["datetime"], format="%Y-%m-%d %H:%M"
    )
    min_data2["datetime"] = min_data2["datetime"].apply(
        lambda x: datetime.datetime.strftime(x, dt_format)
    )
    df = min_data2.pivot_table(index="datetime", aggfunc=nan_mean)
    return df


def gen_sta_period_data(min_data, dt_format="%Y-%m-%d %H"):
    df = min_data[["sta_i", "datetime"] + pollutants]
    df_per = ""
    for sta_i in range(len(stations)):
        df_per_sta = gen_period_data(
            df[df["sta_i"] == sta_i].copy().set_index("datetime"), dt_format=dt_format
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


if __name__ == "__main__":
    t = [
        0,
        np.nan,
        np.nan,
        200,
        200,
        200,
        200,
        200,
        200,
        200,
        200,
        200,
        200,
        200,
        200,
        400,
    ]
    wt = Wash(t, verbose=True)
    tws1, X_span1 = wt.sigma_trim(method="drop")
    tws2, X_span2 = wt.percentile_trim(method="drop")
    tws3, X_span3 = wt.MAD_trim(method="drop")

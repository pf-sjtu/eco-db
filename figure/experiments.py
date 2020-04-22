# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 16:56:49 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""

import add_path
from wash import (
    Wash,
    sta_nan_mean_fill,
    gen_sta_period_data,
    sta_i_desc,
    dt_slice,
)
from project import Project
from stats import normal_stats, anova
from load_mysql_data import mysql_q
from constants import (
    pollutants,
    pollutant_labels,
    pollutant_log_labels,
    stations,
    station_names,
    station_snames,
    years,
    seasons,
    season_bundaries,
)

import pandas as pd, numpy as np
import math, pickle
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from matplotlib import cbook as mcbook
from scipy import stats
from patsy import dmatrices
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
import datetime

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 用来正常显示中文标签
plt.rcParams["axes.unicode_minus"] = False  # 用来正常显示负号
plt.rcParams["font.size"] = 16


# 获得站点、季节、年份数据
def load_pollutant_data(from_mysql=False):
    """
    Parameters
    ----------
    from_mysql : bool, optional
        True to load from MySQL database, False to load from pickle. The default is False.

    Returns
    -------
    df : pandas.Dataframe
        Data of the pollutats.

    """
    if from_mysql:
        df = pd.DataFrame(columns=["sta_i", "datetime", "ssn_i", "year_i"] + pollutants)
        for sta_i in range(len(stations)):
            q = "SELECT `datetime`,{} FROM {};".format(
                "`" + "`,`".join(pollutants) + "`", "`" + stations[sta_i] + "`",
            )
            result_df = pd.DataFrame(data=mysql_q(q), columns=["datetime"] + pollutants)
            result_df["sta_i"] = sta_i
            result_df["ssn_i"] = 0
            result_df["year_i"] = 0
            df = pd.concat([df, result_df], axis=0, join="inner")
        for ssn_i in range(len(season_bundaries)):
            for year_i in range(len(years)):
                ts_span = [
                    pd.Timestamp(str(years[year_i]) + "-" + season_bundaries[ssn_i]),
                    pd.Timestamp(
                        str(
                            years[year_i]
                            + math.floor((ssn_i + 1) / len(season_bundaries))
                        )
                        + "-"
                        + season_bundaries[(ssn_i + 1) % len(season_bundaries)]
                    ),
                ]
                df.loc[
                    (df["datetime"] >= ts_span[0]) & (df["datetime"] < ts_span[1]),
                    ["ssn_i", "year_i"],
                ] = (ssn_i, year_i)

        df = df.astype(dtype={i: np.uint8 for i in ["sta_i", "ssn_i", "year_i"]})
        with open("data_sta_ssn_year_pollutants.pickle", "wb") as f:
            pickle.dump(df, f)
    else:
        with open("data_sta_ssn_year_pollutants.pickle", "rb") as f:
            df = pickle.load(f)
    return df


df_ori = load_pollutant_data(from_mysql=False)

# 崇明区PM10原始数据探索
def proj_ori_hist(sta_i=0, plt_i=0, X_span=[0.01, 9999.98], P=0.99, bins=100):
    """
    Parameters
    ----------
    sta_i : uint, optional
        The serial number of the station. The default is 0.
    plt_i : uint, optional
        The serial number of the pullutant. The default is 0.
    X_span : list, optional
        The value outside of the range will be dropped directly at the very begining. The default is [0.01, 9999.98].
    P : float, optional
        P in the percentile trim. The default is 0.99.
    bins : unint, optional
        Number of bins in hist plot. The default is 100.

    Returns
    -------
    None.

    Project Output
    -------
    1.ori_hist
    """
    proj = Project(name="1.ori_hist", dir="fig", clear=False, verbose=True)
    df = df_ori.loc[df_ori["sta_i"] == sta_i, ["datetime", pollutants[plt_i]]]

    s_wash = Wash(df[pollutants[plt_i]], verbose=False)
    s = s_wash.span_trim(X_span, method="drop")
    s_wash2 = Wash(s, P=P, verbose=True)
    s2, s2_span = s_wash2.percentile_trim(method="drop")

    rec_all = df[pollutants[plt_i]].count()
    rec_smaller = (df[pollutants[plt_i]] < X_span[0]).sum()
    rec_larger = (df[pollutants[plt_i]] > X_span[1]).sum()
    proj.log(
        "{}@{}: from {} to {}. {} records total, {}({}%) records <{}, {}({}%) records >{}.".format(
            pollutants[plt_i],
            stations[sta_i],
            list(df["datetime"])[0],
            list(df["datetime"])[-1],
            rec_all,
            rec_smaller,
            rec_smaller / rec_all * 100,
            X_span[0],
            rec_larger,
            rec_larger / rec_all * 100,
            X_span[1],
        )
    )

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 4))
    ax[0].hist(s, bins=bins)
    ax[0].set_xlabel(pollutant_labels[plt_i])
    ax[0].set_ylabel("频数")
    ax[0].axvline(s2_span[0], linewidth=1, color="red", linestyle="dashed")
    ax[0].axvline(s2_span[1], linewidth=1, color="red", linestyle="dashed")
    ax[1].hist(s2, bins=bins)
    ax[1].set_xlabel(pollutant_labels[plt_i])
    ax[1].set_ylabel("频数")

    plt.subplots_adjust(
        left=None, bottom=None, right=None, top=None, wspace=0.3, hspace=None
    )

    proj.plt_save(
        fig,
        "{}@{}_100p_to_99p.png".format(pollutants[plt_i], stations[sta_i]),
        msg="左图为drop方式舍去{}之外的数据，右图为percentile clip方式处理{}数据，为作图虚线内区域的放大，bins={}".format(
            X_span, P, bins
        ),
        dpi=300,
        bbox_inches="tight",
    )
    fig.show()


def proj_ori_log_hist(sta_i=0, plt_i=0, X_span=[0.01, 9999.98], P=0.99, bins=100):
    """
    Parameters
    ----------
    sta_i : uint, optional
        The serial number of the station. The default is 0.
    plt_i : uint, optional
        The serial number of the pullutant. The default is 0.
    X_span : list, optional
        The value outside of the range will be dropped directly at the very begining. The default is [0.01, 9999.98].
    P : float, optional
        P in the percentile trim. The default is 0.99.
    bins : unint, optional
        Number of bins in hist plot. The default is 100.

    Returns
    -------
    None.

    Project Output
    -------
    2.ori_log_hist
    """
    proj = Project(name="2.ori_log_hist", dir="fig", clear=False, verbose=True)

    df = df_ori.loc[df_ori["sta_i"] == sta_i, ["datetime", pollutants[plt_i]]]
    df[pollutants[plt_i]] = np.log(df[pollutants[plt_i]])

    s_wash = Wash(df[pollutants[plt_i]], verbose=False)
    s = s_wash.span_trim(np.log(X_span), method="drop")
    s_wash2 = Wash(s, P=P, verbose=True)
    s2, s2_span = s_wash2.percentile_trim(method="drop")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 4))
    ax[0].hist(s, bins=bins)
    ax[0].set_xlabel(pollutant_log_labels[plt_i])
    ax[0].set_ylabel("频数")
    ax[0].axvline(s2_span[0], linewidth=1, color="red", linestyle="dashed")
    ax[0].axvline(s2_span[1], linewidth=1, color="red", linestyle="dashed")
    ax[1].hist(s2, bins=bins)
    ax[1].set_xlabel(pollutant_log_labels[plt_i])
    ax[1].set_ylabel("频数")

    plt.subplots_adjust(
        left=None, bottom=None, right=None, top=None, wspace=0.3, hspace=None
    )

    proj.plt_save(
        fig,
        "ln({})@{}_100p_to_99p.png".format(pollutants[plt_i], stations[sta_i]),
        msg="左图为drop方式舍去{}之外的数据，右图为percentile clip方式处理{}数据，为作图虚线内区域的放大，bins={}.".format(
            X_span, P, bins
        ),
        dpi=300,
        bbox_inches="tight",
    )
    fig.show()


def proj_normalized_check(X_span=[0.01, 9999.98], load=True, latex=False):
    # drop outliers
    proj = Project(name="3.ori_normality", dir="fig", clear=False, verbose=True)

    if not load:
        df_ori_drop = df_ori.copy()
        df_ori_log = df_ori.copy()
        for pollutant in pollutants:
            s_wash = Wash(df_ori_drop[pollutant], verbose=False)
            df_ori_drop[pollutant] = s_wash.span_trim(X_span, method="nan")
            df_ori_log[pollutant] = np.log(df_ori_drop[pollutant])
        df_ori_log.rename(columns={i: "log_" + i for i in pollutants}, inplace=True)
        df_ori_norm = normal_stats(
            df_ori_drop, groupby=["sta_i"], target_cols=pollutants
        )
        df_ori_log_norm = normal_stats(
            df_ori_log, groupby=["sta_i"], target_cols=["log_" + i for i in pollutants]
        )
        df_ori_norm = pd.concat([df_ori_norm, df_ori_log_norm], axis=1, join="inner")
        proj.pickle_dump(
            df_ori_norm, "station_original_data_normality", msg="Type = pd.Dataframe."
        )
    else:
        df_ori_norm = proj.pickle_load("station_original_data_normality")

    df_ori_norm.reset_index(inplace=True)
    df_ori_norm_rep = ""
    for i, i_name in zip(["skew", "kurtosis", "normality"], ["偏度", "峰度", "正态性"]):
        plt_norm_rep = pd.melt(
            df_ori_norm,
            id_vars=["sta_i"],
            value_vars=[j + "_" + i for j in pollutants],
            var_name="项目",
            value_name=i_name,
        )
        if type(df_ori_norm_rep) == str:
            df_ori_norm_rep = plt_norm_rep[["项目", "sta_i", i_name]]
        else:
            df_ori_norm_rep = pd.concat([df_ori_norm_rep, plt_norm_rep[i_name]], axis=1)
        df_ori_norm_rep = pd.concat(
            [
                df_ori_norm_rep,
                pd.melt(
                    df_ori_norm,
                    id_vars=["sta_i"],
                    value_vars=["log_" + j + "_" + i for j in pollutants],
                    var_name="项目",
                    value_name="对数化" + i_name,
                )["对数化" + i_name],
            ],
            axis=1,
        )
    df_ori_norm_rep["项目"] = df_ori_norm_rep["项目"].map(
        {pollutants[i] + "_skew": pollutant_labels[i] for i in range(len(pollutants))}
    )
    df_ori_norm_rep[["正态性", "对数化正态性"]] = df_ori_norm_rep[["正态性", "对数化正态性"]].applymap(
        lambda x: {True: "满足", False: "不满足"}.get(x)
    )
    df_ori_norm_rep["sta_i"] = df_ori_norm_rep["sta_i"].map(
        {i: station_names[i] for i in range(len(station_names))}
    )
    df_ori_norm_rep.rename(columns={"sta_i": "站点"}, inplace=True)
    df_ori_norm_rep_latex = df_ori_norm_rep.to_latex(
        index=False, longtable=True, escape=False, float_format="%.2f"
    )
    proj.log("Latex table write to log.")
    proj.set_verbose(False)
    proj.log(df_ori_norm_rep_latex)
    if latex:
        return df_ori_norm, df_ori_norm_rep_latex
    else:
        return df_ori_norm, df_ori_norm_rep


def trim_method_plot(plt_i=-1, sta_i=-1, X_span=[0.01, 9999.98], P=0.99, bins=100):
    proj = Project(name="4.trim_test", dir="fig", clear=False, verbose=True)
    plt_i_range = range(len(pollutants)) if plt_i == -1 else [plt_i]
    sta_i_range = range(len(stations)) if sta_i == -1 else [sta_i]
    for plt_i in plt_i_range:
        for sta_i in sta_i_range:
            plt_series = df_ori.loc[df_ori["sta_i"] == sta_i, pollutants[plt_i]]
            pw0 = Wash(plt_series).span_trim(X_span, method="drop")
            w = Wash(np.log(pw0), P=P, verbose=True)

            pw1, X_span1 = w.sigma_trim(method="clip")
            pw2, X_span2 = w.MAD_trim(method="clip")
            pw3, X_span3 = w.percentile_trim(method="clip")

            fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(12, 4))
            ax[0].hist(pw1, bins=bins)
            ax[0].set_xlabel(pollutant_log_labels[plt_i])
            ax[0].set_ylabel("频数")
            ax[1].hist(pw2, bins=bins)
            ax[1].set_xlabel(pollutant_log_labels[plt_i])
            ax[1].set_yticks([])
            ax[2].hist(pw3, bins=bins)
            ax[2].set_xlabel(pollutant_log_labels[plt_i])
            ax[2].set_yticks([])

            plt.subplots_adjust(
                left=None, bottom=None, right=None, top=None, wspace=0.1, hspace=None
            )
            proj.plt_save(
                fig,
                "ln{}@{}_trim.png".format(pollutants[plt_i], stations[sta_i]),
                dpi=300,
                bbox_inches="tight",
            )
            fig.show()


def trim(load=True, X_span=[0.01, 9999.98], P=0.99, method=-1):
    proj = Project(name="5.trim", dir="fig", clear=False, verbose=True)
    if method == -1:
        if not load:
            # station order: cm, jh, zsgy
            # mathod code: 0: 3sigma, 1: MAD, 2: percentile
            plt_log_trim_method = {
                "CO": [1, 1, 1],
                "NO": [1, 1, 1],
                "NOX": [0, 1, 0],
                "O3": [0, 1, 1],
                "PM2p5": [1, 1, 1],
                "PM10": [1, 1, 1],
                "SO2": [1, 0, 0],
            }
            plt_log_trim = {}
            for pollutant in pollutants:
                plt_log_trim[pollutant] = int(
                    stats.mode(plt_log_trim_method[pollutant])[0][0]
                )
            proj.json_dump(plt_log_trim, "pollutant_trim_method")
        else:
            plt_log_trim = proj.json_load("pollutant_trim_method")
    else:
        plt_log_trim = {}
        for pollutant in pollutants:
            plt_log_trim[pollutant] = method
    if not load:
        df_trimed = df_ori.copy()
        for pollutant in pollutants:
            w0 = Wash(df_ori[pollutant])
            s0 = w0.span_trim(X_span)
            method_i = plt_log_trim[pollutant]
            w = Wash(np.log(s0), P=P)
            if method_i == 0:
                df_trimed[pollutant] = np.exp(w.sigma_trim("nan"))
            elif method_i == 1:
                df_trimed[pollutant] = np.exp(w.MAD_trim("nan"))
            elif method_i == 2:
                df_trimed[pollutant] = np.exp(w.percentile_trim("nan"))
        if method == -1:
            df_trimed.reset_index(drop=True, inplace=True)
            proj.pickle_dump(df_trimed, "df_trimed", msg="dtype==pandas.Dataframe.")
            df_missing_report = ""
            for sta_i in range(len(stations)):
                df = df_trimed[df_trimed["sta_i"] == sta_i]
                df_r = pd.DataFrame(data=df[pollutants].count()).reset_index()
                df_r["missing_rate"] = 1 - df_r[0] / df.shape[0]
                df_r["sta"] = station_names[sta_i]
                df_r["sta_line_num"] = df.shape[0]
                dt_beg = df.loc[df.index[0], "datetime"]
                dt_end = df.loc[df.index[-1], "datetime"]
                time_lines = int(np.floor((dt_end - dt_beg).total_seconds() / 60 / 5))
                df_r["missing_rate_time"] = (
                    1 - df[pollutants].count().to_numpy() / time_lines
                )

                if type(df_missing_report) == str:
                    df_missing_report = df_r
                else:
                    df_missing_report = pd.concat(
                        [df_missing_report, df_r], join="inner"
                    )

            df_missing_report["index"] = df_missing_report["index"].map(
                {pollutants[i]: pollutant_labels[i] for i in range(len(pollutants))}
            )

            df_missing_report = df_missing_report[
                ["sta", "index", "sta_line_num", 0, "missing_rate", "missing_rate_time"]
            ]
            df_missing_report.rename(
                columns={
                    "sta": "站点",
                    "index": "项目",
                    "sta_line_num": "条目数",
                    0: "有效条目数",
                    "missing_rate": "条目内缺失率",
                    "missing_rate_time": "时间缺失率",
                },
                inplace=True,
            )

            proj.log("Latex table write to log.")
            proj.set_verbose(False)
            proj.log(
                df_missing_report.to_latex(
                    index=False,
                    longtable=True,
                    escape=False,
                    float_format="{:.2%}".format,
                ),
                "df_missing_report",
            )
    else:
        df_trimed = proj.pickle_load("df_trimed")

    return df_trimed, plt_log_trim


df_trimed, plt_log_trim = trim(load=True, X_span=[0.01, 9999.98], P=0.99, method=-1)


def hour_mean(load=True, plot=False, plt_i=-1, sta_i=-1):
    proj = Project(name="6.hour_mean", dir="fig", clear=False, verbose=True)
    if not load:
        df_hour = gen_sta_period_data(df_trimed, dt_format="%Y-%m-%d %H")
        proj.pickle_dump(df_hour, "df_hour", msg="dtype==pandas.Dataframe.")
    else:
        df_hour = proj.pickle_load("df_hour")
    if plot:
        df_hour["datetime"] = pd.to_datetime(df_hour["datetime"], format="%Y-%m-%d")
        plt_i_range = range(len(pollutants)) if plt_i == -1 else [plt_i]
        sta_i_range = range(len(stations)) if sta_i == -1 else [sta_i]
        for sta_i in sta_i_range:
            df_hour_sta = df_hour[df_hour["sta_i"] == sta_i]
            for plt_i in plt_i_range:
                fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 4))
                ax.plot(df_hour_sta["datetime"], df_hour_sta[pollutants[plt_i]])
                ax.set_xlabel("时间")
                ax.set_ylabel(pollutant_labels[plt_i])
                proj.plt_save(
                    fig,
                    "{}@{}_hour.png".format(pollutants[plt_i], stations[sta_i]),
                    dpi=300,
                    bbox_inches="tight",
                )
                fig.show()
    return df_hour


def day_mean(load=True, plot=False, plt_i=-1, sta_i=-1):
    proj = Project(name="7.day_mean", dir="fig", clear=False, verbose=True)
    if not load:
        df_day = gen_sta_period_data(df_trimed, dt_format="%Y-%m-%d")
        proj.pickle_dump(df_day, "df_day", msg="dtype==pandas.Dataframe.")
    else:
        df_day = proj.pickle_load("df_day")
    if plot:
        df_day["datetime"] = pd.to_datetime(df_day["datetime"], format="%Y-%m-%d")
        plt_i_range = range(len(pollutants)) if plt_i == -1 else [plt_i]
        sta_i_range = range(len(stations)) if sta_i == -1 else [sta_i]
        for sta_i in sta_i_range:
            df_day_sta = df_day[df_day["sta_i"] == sta_i]
            for plt_i in plt_i_range:
                fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 4))
                ax.plot(df_day_sta["datetime"], df_day_sta[pollutants[plt_i]])
                ax.set_xlabel("时间")
                ax.set_ylabel(pollutant_labels[plt_i])
                proj.plt_save(
                    fig,
                    "{}@{}_day.png".format(pollutants[plt_i], stations[sta_i]),
                    dpi=300,
                    bbox_inches="tight",
                )
                fig.show()
    return df_day


def month_mean(load=True, plot=False, plt_i=-1, sta_i=-1):
    proj = Project(name="8.month_mean", dir="fig", clear=False, verbose=True)
    if not load:
        df_month = gen_sta_period_data(df_trimed, dt_format="%Y-%m")
        proj.pickle_dump(df_month, "df_month", msg="dtype==pandas.Dataframe.")
    else:
        df_month = proj.pickle_load("df_month")
    if plot:
        df_month["datetime"] = pd.to_datetime(df_month["datetime"], format="%Y-%m")
        plt_i_range = range(len(pollutants)) if plt_i == -1 else [plt_i]
        sta_i_range = range(len(stations)) if sta_i == -1 else [sta_i]
        for sta_i in sta_i_range:
            df_month_sta = df_month[df_month["sta_i"] == sta_i]
            for plt_i in plt_i_range:
                fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 4))
                ax.plot(df_month_sta["datetime"], df_month_sta[pollutants[plt_i]])
                ax.set_xlabel("时间")
                ax.set_ylabel(pollutant_labels[plt_i])
                proj.plt_save(
                    fig,
                    "{}@{}_month.png".format(pollutants[plt_i], stations[sta_i]),
                    dpi=300,
                    bbox_inches="tight",
                )
                fig.show()
    return df_month


def plt_average_boxplot(plt_i=-1):
    proj = Project(name="9.plt_average_boxplot", dir="fig", clear=False, verbose=True)
    plt_i_range = range(len(pollutants)) if plt_i == -1 else [plt_i]
    # linestyle_list = ["-", "--", ":", "-."]
    for plt_i in plt_i_range:
        bstats = []
        for sta_i in range(len(stations)):
            a = np.log(df_trimed.loc[df_trimed["sta_i"] == sta_i, pollutants[plt_i]])
            bstats += mcbook.boxplot_stats(a[~np.isnan(a)])

        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 6))
        ax.bxp(bstats)
        ax.set_xlabel("站点")
        # ax.set_xticklabels(station_names, rotation=10, fontdict={"horizontalalignment": "right"})
        ax.set_xticklabels(station_snames)
        ax.set_ylabel(pollutant_log_labels[plt_i])
        proj.plt_save(
            fig,
            "ln{}_average_boxplot.png".format(pollutants[plt_i]),
            dpi=300,
            bbox_inches="tight",
        )
        fig.show()


def oneday(
    plt_i=0, sta_i=0, dt_beg="2019-05-12 00:00:00", dt_end="2019-05-13 00:00:00"
):
    dt_beg = datetime.datetime.strptime(dt_beg, "%Y-%m-%d %H:%M:%S")
    dt_end = datetime.datetime.strptime(dt_end, "%Y-%m-%d %H:%M:%S")
    df_oneday = df_trimed[
        (df_trimed["datetime"] >= dt_beg) & (df_trimed["datetime"] < dt_end)
    ][["sta_i", "datetime"] + pollutants]
    df_oneday_sta = df_oneday[df_oneday["sta_i"] == sta_i]
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 4))
    ax.plot(df_oneday_sta["datetime"], df_oneday_sta[pollutants[plt_i]])
    ax.set_xlabel("时间")
    ax.set_ylabel(pollutant_labels[plt_i])
    ax.set_xticklabels(rotation=15)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    fig.show()


def inday(load=True, plot=False, all_stations=False, plt_i=-1, sta_i=-1):
    proj = Project(name="10.inday_average", dir="fig", clear=False, verbose=True)
    if not load:
        df_inday = gen_sta_period_data(df_trimed, dt_format="%H")
        proj.pickle_dump(df_inday, "df_inday", msg="dtype==pandas.Dataframe.")
    else:
        df_inday = proj.pickle_load("df_inday")
    if plot:
        plt_i_range = range(len(pollutants)) if plt_i == -1 else [plt_i]
        sta_i_range = range(len(stations)) if sta_i == -1 else [sta_i]
        if all_stations:
            linestyle_list = ["-", "--", ":", "-."]
            for plt_i in plt_i_range:
                fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 4))
                for sta_i in sta_i_range:
                    ax.plot(
                        np.array(
                            df_inday.loc[df_inday["sta_i"] == sta_i, "datetime"],
                            dtype=int,
                        ),
                        df_inday.loc[df_inday["sta_i"] == sta_i, pollutants[plt_i]],
                        label=station_snames[sta_i],
                        linestyle=linestyle_list[sta_i],
                    )

                ax.set_xlabel("时间")
                ax.set_ylabel(pollutant_labels[plt_i])
                ax.set_xticks(range(24))
                ax.set_xticklabels(
                    [str(i) + ":00" if i % 2 == 0 else "" for i in range(24)]
                )
                ybound = ax.get_ybound()
                ax.set_ybound((ybound[0], ybound[1] * 1.25))
                ax.legend(loc="best", ncol=len(sta_i_range))
                proj.plt_save(
                    fig,
                    "{}_inday.png".format(pollutants[plt_i], stations[sta_i]),
                    dpi=300,
                    bbox_inches="tight",
                )
                fig.show()
        else:
            for sta_i in sta_i_range:
                df_inday_sta = df_inday[df_inday["sta_i"] == sta_i]
                for plt_i in plt_i_range:
                    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 4))
                    ax.plot(
                        np.array(df_inday_sta["datetime"], dtype=int),
                        df_inday_sta[pollutants[plt_i]],
                    )
                    ax.set_xlabel("时间")
                    ax.set_ylabel(pollutant_labels[plt_i])
                    ax.set_xticks(range(24))
                    ax.set_xticklabels(
                        [str(i) + ":00" if i % 2 == 0 else "" for i in range(24)]
                    )
                    proj.plt_save(
                        fig,
                        "{}@{}_inday.png".format(pollutants[plt_i], stations[sta_i]),
                        dpi=300,
                        bbox_inches="tight",
                    )
                    fig.show()
    return df_inday


def sta_anova(plt_i=-1, load=True):
    proj = Project(name="11.sta_anova", dir="fig", clear=False, verbose=True)
    if not load:
        plt_i_range = range(len(pollutants)) if plt_i == -1 else [plt_i]
        anova_sta = ""
        for plt_i in plt_i_range:
            # 直接对原始数据(trimed)进行方差分析
            print("ANOVA trimed@plt.No{}...".format(plt_i))
            anova_sta_line = anova(
                df_trimed,
                "{} ~ C(sta_i)".format(pollutants[plt_i]),
                qq=False,
                sta=False,
            ).loc[["C(sta_i)"], :]
            anova_sta_line.index = ["trimed"]
            anova_sta_line["plt_i"] = plt_i
            anova_sta_line["pollutant"] = pollutants[plt_i]
            if type(anova_sta) == str:
                anova_sta = anova_sta_line
            else:
                anova_sta = pd.concat([anova_sta, anova_sta_line], join="inner")
        df_inday = inday(load=True, plot=False, all_stations=False, plt_i=-1, sta_i=-1)
        for plt_i in plt_i_range:
            # 对一天以内平均数据(inday)数据进行方差分析
            print("ANOVA inday@plt.No{}...".format(plt_i))
            anova_sta_line = anova(
                df_inday, "{} ~ C(sta_i)".format(pollutants[plt_i]), qq=False, sta=False
            ).loc[["C(sta_i)"], :]
            anova_sta_line.index = ["inday"]
            anova_sta_line["plt_i"] = plt_i
            anova_sta_line["pollutant"] = pollutants[plt_i]
            anova_sta = pd.concat([anova_sta, anova_sta_line], join="inner")
        df_hours = df_trimed.copy()
        df_hours["datetime"] = pd.to_datetime(
            df_hours["datetime"], format="%Y-%m-%d %H:%M"
        )
        df_hours["datetime"] = df_hours["datetime"].apply(
            lambda x: datetime.datetime.strftime(x, "%H")
        )
        df_hours = df_hours.astype({"datetime": int})
        for hour in range(24):
            df_hour = df_hours.loc[df_hours["datetime"] == hour, :]
            for plt_i in plt_i_range:
                print("ANOVA hour{}@plt.No{}...".format(hour, plt_i))
                anova_sta_line = anova(
                    df_hour,
                    "{} ~ C(sta_i)".format(pollutants[plt_i]),
                    qq=False,
                    sta=False,
                ).loc[["C(sta_i)"], :]
                anova_sta_line.index = ["hour{}".format(hour)]
                anova_sta_line["plt_i"] = plt_i
                anova_sta_line["pollutant"] = pollutants[plt_i]
                anova_sta = pd.concat([anova_sta, anova_sta_line], join="inner")
        anova_sta = anova_sta.reset_index().rename(columns={"index": "data"})
        proj.pickle_dump(anova_sta, "anova_sta", msg="dtype==pandas.Dataframe.")
    else:
        anova_sta = proj.pickle_load("anova_sta")
    return anova_sta


if __name__ == "__main__":
    # proj_ori_hist(sta_i=0, plt_i=0, X_span=[0.01, 9999.98], P=0.99, bins=100)
    # proj_ori_log_hist(sta_i=0, plt_i=0, X_span=[0.01, 9999.98], P=0.99, bins=100)
    # df_ori_norm, df_ori_norm_rep = proj_normalized_check(X_span=[0.01, 9999.98], load=True)

    # df_hour_mean = hour_mean(load=True, plot=False, plt_i=-1, sta_i=-1)
    df_day_mean = day_mean(load=True, plot=False, plt_i=-1, sta_i=-1)
    # df_month_mean = month_mean(load=True, plot=False, plt_i=-1, sta_i=-1)

    # trim_method_plot(plt_i=-1, sta_i=-1, X_span=[0.01, 9999.98], P=0.99, bins=100)
    # oneday(plt_i=0, sta_i=0, dt_beg="2019-05-12 00:00:00", dt_end="2019-05-13 00:00:00")
    # plt_average_boxplot(plt_i=-1)

    # df_inday = inday(load=True, plot=False, all_stations=False, plt_i=-1, sta_i=-1)

    # r = sta_i_desc(df_inday)
    # 方差分析：站点
    # anova_sta = sta_anova(plt_i=-1, load=True)
    # data_sig = anova_sta.loc[anova_sta[]]

    # In[0]:
    # # fig, ax = plt.subplots(figsize=(8,6))
    plt_i = 0
    # # # sta_i = 0
    # # for sta_i in range(len(stations)):
    # #     df_inday_sta = df_inday.loc[df_inday['sta_i'] == sta_i]
    # #     ax.scatter(df_inday_sta['datetime'], df_inday_sta[pollutants[plt_i]], alpha=0.5, label=station_snames[sta_i])
    # #     ax.set_xlabel('datetime')
    # #     ax.set_ylabel(pollutant_labels[plt_i])
    # #     ax.legend(loc="top left")

    df_day_mean_filled = sta_nan_mean_fill(df_day_mean)
    formula="np.log({}) ~ C(sta_i)".format(pollutants[plt_i])

    model = smf.ols(formula=formula, data=df_day_mean_filled)
    result = model.fit()
    print(result.summary())
    anova = anova_lm(result, typ=3)
    # print(anova)

    # In[1]:


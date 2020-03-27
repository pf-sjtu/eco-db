# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 19:20:06 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""

# 春季：2月3--5日交节  [立春(节气)，黄经315度]；
# 夏季：5月5--7日交节  [立夏(节气)，黄经45度 ]；
# 秋季：8月7--9日交节  [立秋(节气)，黄经135度]；
# 冬季：11月7--8日交节 [立冬(节气)，黄经225度]；

import numpy as np, pandas as pd, time, sys, math, pickle, json, random
from matplotlib import pyplot as plt, patches as mpatches, cbook
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.graphics.factorplots import interaction_plot


import add_path
from utils.global_variables import TEMP_DIR, station_info, rm_tmp
from database.mysql_init import connect_db, close_db

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 用来正常显示中文标签
plt.rcParams["axes.unicode_minus"] = False  # 用来正常显示负号
plt.rcParams["font.size"] = 16


pollutants = ["PM10", "PM2p5", "SO2", "NOX", "NO", "CO", "O3"]
pollutant_labels = [
    "${\\rm PM_{10}}$浓度值",
    "${\\rm PM_{2.5}}$浓度值",
    "${\\rm SO_{2}}$浓度值",
    "${\\rm NO_{X}}$浓度值",
    "${\\rm NO}$浓度值",
    "${\\rm CO}$浓度值",
    "${\\rm O_{3}}$浓度值",
]
pollutant_log_labels = [
    "$log({\\rm PM_{10}}$浓度值$)$",
    "$log({\\rm PM_{2.5}}$浓度值$)$",
    "$log({\\rm SO_{2}}$浓度值$)$",
    "$log({\\rm NO_{X}}$浓度值$)$",
    "$log({\\rm NO}$浓度值$)$",
    "$log({\\rm CO}$浓度值$)$",
    "$log({\\rm O_{3}}$浓度值$)$",
]


# pollutants_thd = [[0,800]]
years = list(range(2017, time.localtime().tm_year + 1))
seasons = list("春夏秋冬")
season_bundaries = ["02-04", "05-06", "08-08", "11-08"]
stations = list(station_info["db_table_name"])
station_names = list(station_info["station_name2"])
box_colors = ["#000000", "#006000", "#AA0000"]
# box_colors = ["red", "blue", "green"]
lmt = ["LIMIT 50", ""]

plt_i = 0


class MAD:
    def __init__(
        self, obj=pollutants[plt_i], stations=stations, ratio=5, bundary=[-9999, 9999]
    ):
        self.MAD = self.get_MAD(obj, stations, ratio, bundary)

    def get_median(self, obj, stations, bundary):
        db = connect_db()
        db_cursor = db.cursor()
        median = []
        for sta_i in range(len(stations)):
            q = """SELECT
                            d.dNum AS median
                    FROM
                        (
                        SELECT
                            @rowIndex := @rowIndex + 1 AS rowIndex,
                            {} AS dNum
                        FROM
                            {},
                            ( SELECT @rowIndex := - 1 ) AS tmpI
                    WHERE {} > {} AND {} < {}
                        ORDER BY
                            {}
                        ) AS d
                    WHERE
                        rowIndex IN (
                        FLOOR( @rowindex / 2 ),
                        CEIL( @rowindex / 2 ));""".format(
                obj, stations[sta_i], obj, bundary[0], obj, bundary[1], obj
            )
            db_cursor.execute(q)
            m = db_cursor.fetchall()[0]
            median.append(np.mean(m))
        close_db(db)
        return median

    def get_MAD(self, obj, stations, ratio, bundary):
        db = connect_db()
        db_cursor = db.cursor()
        median = self.get_median(obj, stations, bundary)
        abs_dev_median = []
        for sta_i in range(len(stations)):
            q = """SELECT
                            d.absDev AS absDevMed
                    FROM
                            (
                            SELECT
                                @rowIndex := @rowIndex + 1 AS rowIndex,
                                absDev
                            FROM
                            (
                            SELECT
                                    ABS({}-{}) AS absDev
                                FROM
                                {}
                            WHERE {} > {} AND {} < {}
                            ) AS tmpAbsDevT,
                                ( SELECT @rowIndex := - 1 ) AS tmpI
                            ORDER BY
                                absDev
                            ) AS d
                    WHERE
                        rowIndex IN (
                        FLOOR( @rowindex / 2 ),
                        CEIL( @rowindex / 2 ));""".format(
                obj, median[sta_i], stations[sta_i], obj, bundary[0], obj, bundary[1]
            )
            db_cursor.execute(q)
            m = db_cursor.fetchall()[0]
            abs_dev_median.append(np.mean(m))
        close_db(db)
        MAD_span = [
            [m - adm * ratio, m + adm * ratio] for m, adm in zip(median, abs_dev_median)
        ]
        return {"median": median, "adm": abs_dev_median, "span": MAD_span}


class sigma3:
    def __init__(
        self, obj=pollutants[plt_i], stations=stations, ratio=3, bundary=[-9999, 9999]
    ):
        self.sigma3 = self.get_sigma3(obj, stations, ratio, bundary)

    def get_mean(self, obj, stations, bundary):
        db = connect_db()
        db_cursor = db.cursor()
        mean = []
        for sta_i in range(len(stations)):
            q = "SELECT AVG({}) FROM {} WHERE {} > {} AND {} < {};".format(
                obj, stations[sta_i], obj, bundary[0], obj, bundary[1]
            )
            db_cursor.execute(q)
            mean.append(db_cursor.fetchall()[0][0])
        close_db(db)
        return mean

    def get_std(self, obj, stations, bundary):
        db = connect_db()
        db_cursor = db.cursor()
        std = []
        for sta_i in range(len(stations)):
            q = "SELECT STDDEV({}) FROM {} WHERE {} > {} AND {} < {};".format(
                obj, stations[sta_i], obj, bundary[0], obj, bundary[1]
            )
            db_cursor.execute(q)
            std.append(db_cursor.fetchall()[0][0])
        close_db(db)
        return std

    def get_sigma3(self, obj, stations, ratio, bundary):
        mean = self.get_mean(obj, stations, bundary)
        std = self.get_std(obj, stations, bundary)
        sigma3_span = [[m - s * ratio, m + s * ratio] for m, s in zip(mean, std)]
        return {"mean": mean, "std": std, "span": sigma3_span}


class percentile:
    def __init__(
        self,
        obj=pollutants[plt_i],
        stations=stations,
        percentile=[0.005, 0.995],
        bundary=[-9999, 9999],
    ):
        self.p_data = self.get_p_data(obj, stations, percentile, bundary)

    def get_p_data(self, obj, stations, percentile, bundary):
        db = connect_db()
        db_cursor = db.cursor()
        p_data = []
        for sta_i in range(len(stations)):
            sta_p_list = []
            for p in percentile:
                q = """SELECT
                                d.dNum AS median
                        FROM
                            (
                            SELECT
                                @rowIndex := @rowIndex + 1 AS rowIndex,
                                {} AS dNum
                            FROM
                                {},
                                ( SELECT @rowIndex := - 1 ) AS tmpI
                        WHERE {} > {} AND {} < {}
                            ORDER BY
                                {}
                            ) AS d
                        WHERE
                            rowIndex IN (
                            FLOOR( @rowindex * {} ),
                            CEIL( @rowindex * {} ));""".format(
                    obj, stations[sta_i], obj, bundary[0], obj, bundary[1], obj, p, p
                )
                db_cursor.execute(q)
                m = db_cursor.fetchall()[0]
                sta_p_list.append(np.mean(m))
            p_data.append(sta_p_list)
        close_db(db)
        return p_data


def get_data_dict(plt_i, pollutants_thd, method="trim"):
    db = connect_db()
    db_cursor = db.cursor()

    data_dict = {}

    for sta_i in range(len(stations)):
        data_dict[stations[sta_i]] = {}
        for ssn_i in range(len(season_bundaries)):
            data_dict[stations[sta_i]][ssn_i] = {}
            for year_i in range(len(years)):
                time_span = [
                    str(years[year_i]) + "-" + season_bundaries[ssn_i],
                    str(years[year_i] + math.floor((ssn_i + 1) / len(season_bundaries)))
                    + "-"
                    + season_bundaries[(ssn_i + 1) % len(season_bundaries)],
                ]

                q = 'SELECT {} FROM {} WHERE datetime >= "{}" AND datetime < "{}" {};'.format(
                    pollutants[plt_i],
                    stations[sta_i],
                    time_span[0],
                    time_span[1],
                    lmt[1],
                )
                # print(q)
                if db_cursor.execute(q):
                    data = db_cursor.fetchall()
                    data_dict[stations[sta_i]][ssn_i][years[year_i]] = []
                    for d in data:
                        if method == "trim":
                            if (
                                d[0] > pollutants_thd[sta_i][0]
                                and d[0] < pollutants_thd[sta_i][1]
                            ):
                                data_dict[stations[sta_i]][ssn_i][years[year_i]].append(
                                    d[0]
                                )
                        elif method == "clip":
                            data_dict[stations[sta_i]][ssn_i][years[year_i]].append(
                                np.clip(
                                    d[0],
                                    pollutants_thd[sta_i][0],
                                    pollutants_thd[sta_i][1],
                                )
                            )

    close_db(db)
    del data

    with open("{}_data_dict.pickle".format(pollutants[plt_i]), "wb") as f:
        pickle.dump(data_dict, f)


# 读取第plt_i号污染物的数据
def load_data_dict(plt_i):
    with open("{}_data_dict.pickle".format(pollutants[plt_i]), "rb") as f:
        data_dict = pickle.load(f)
    return data_dict


# 从数据库选取sta_i号站点的原始数据，然后进行箱线图绘制，粗略查看极值范围
def ori_extreme(plt_i, sta_i):
    db = connect_db()
    db_cursor = db.cursor()
    obj = pollutants[plt_i]

    q = "SELECT {} FROM {};".format(obj, stations[sta_i])
    db_cursor.execute(q)
    ori_data = np.array([i[0] for i in db_cursor.fetchall()])
    close_db(db)

    box_stats = cbook.boxplot_stats(ori_data)

    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))
    _ = axs[0].bxp(box_stats, showfliers=True)
    _ = axs[1].bxp(box_stats, showfliers=False)

    axs[0].set_xticks([])
    axs[1].set_xticks([])
    axs[0].set_ylabel(pollutant_labels[plt_i])
    # axs[0].set_ylabel("$\\rm PM_{10} (\\mu g \\cdot cm^{-3})$")

    fig.savefig(
        "{}_{}_box.png".format(stations[sta_i], pollutants[plt_i]),
        dpi=300,
        bbox_inches="tight",
    )
    print(
        "{}站点{}数据：共{}条，<0有{}条，>999有{}条。".format(
            stations[sta_i],
            pollutants[plt_i],
            len(ori_data),
            len(ori_data[ori_data < 0]),
            len(ori_data[ori_data > 999]),
        )
    )


# 先用三种方式对三个站点的plt_i号污染物进行初步裁切（舍弃），并且做直方图
def way3_trim(plt_i):
    db = connect_db()
    db_cursor = db.cursor()

    obj = pollutants[plt_i]
    for obj, obj_label, obj_log_label in zip(
        pollutants, pollutant_labels, pollutant_log_labels
    ):
        t1 = MAD(obj=obj)
        t2 = sigma3(obj=obj)
        t3 = percentile(obj=obj)
        bundary_list = [t1.MAD["span"], t2.sigma3["span"], t3.p_data]
        method_names = ["MAD", "sigma3", "percentile005"]

        for method_name, bundarys in zip(method_names, bundary_list):
            t_data = []
            for sta_i in range(len(stations)):
                q = "SELECT {} FROM {} WHERE {} > {} AND {} < {};".format(
                    obj,
                    stations[sta_i],
                    obj,
                    bundarys[sta_i][0],
                    obj,
                    bundarys[sta_i][1],
                )
                db_cursor.execute(q)
                t_data.append([i[0] for i in db_cursor.fetchall()])

                tt_data = np.array(t_data[sta_i])
                tt_data = tt_data[tt_data > 0.0001]

                fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))
                _ = axs[0].hist(x=tt_data, bins=50, density=True)
                _ = axs[1].hist(x=np.log(tt_data), bins=100, density=True)
                axs[0].set_xlabel(obj_label)
                axs[1].set_xlabel(obj_log_label)
                axs[0].set_ylabel("频率")
                filename = "{}_{}_freq_trim_{}.png".format(
                    stations[sta_i], obj, method_name
                )
                fig.savefig(filename, dpi=300, bbox_inches="tight")
    close_db(db)


class log_sigma3:
    def __init__(
        self, obj=pollutants[plt_i], stations=stations, ratio=3, bundary=[-9999, 9999]
    ):
        self.sigma3 = self.get_sigma3(obj, stations, ratio, bundary)

    def get_mean(self, obj, stations, bundary):
        db = connect_db()
        db_cursor = db.cursor()
        mean = []
        for sta_i in range(len(stations)):
            q = "SELECT AVG(LOG({})) FROM {} WHERE {} > {} AND {} < {};".format(
                obj, stations[sta_i], obj, bundary[0], obj, bundary[1]
            )
            db_cursor.execute(q)
            mean.append(db_cursor.fetchall()[0][0])
        close_db(db)
        return mean

    def get_std(self, obj, stations, bundary):
        db = connect_db()
        db_cursor = db.cursor()
        std = []
        for sta_i in range(len(stations)):
            q = "SELECT STDDEV(LOG({})) FROM {} WHERE {} > {} AND {} < {};".format(
                obj, stations[sta_i], obj, bundary[0], obj, bundary[1]
            )
            db_cursor.execute(q)
            std.append(db_cursor.fetchall()[0][0])
        close_db(db)
        return std

    def get_sigma3(self, obj, stations, ratio, bundary):
        mean = self.get_mean(obj, stations, bundary)
        std = self.get_std(obj, stations, bundary)
        sigma3_span = [
            [np.exp(m - s * ratio), np.exp(m + s * ratio)] for m, s in zip(mean, std)
        ]
        return {"mean": mean, "std": std, "span": sigma3_span}


# 计算所有污染物对数化的3sigma边界，存档并且返回
def log_sigma3_trim():
    db = connect_db()
    db_cursor = db.cursor()

    bundarys_list = {}
    for obj, obj_label, obj_log_label in zip(
        pollutants, pollutant_labels, pollutant_log_labels
    ):
        trim_conf = log_sigma3(obj=obj)
        bundarys = trim_conf.sigma3["span"]

        bundarys_list[obj] = bundarys

        t_data = []
        for sta_i in range(1):
            q = "SELECT {} FROM {} WHERE {} > {} AND {} < {};".format(
                obj, stations[sta_i], obj, bundarys[sta_i][0], obj, bundarys[sta_i][1]
            )
            db_cursor.execute(q)
            t_data.append([i[0] for i in db_cursor.fetchall()])

        tt_data = np.array(t_data[0])
        tt_data = tt_data[tt_data > 0.0001]

        fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))
        _ = axs[0].hist(x=tt_data, bins=50, density=True)
        _ = axs[1].hist(x=np.log(tt_data), bins=100, density=True)
        axs[0].set_xlabel(obj_label)
        axs[1].set_xlabel(obj_log_label)
        axs[0].set_ylabel("频率")
        filename = "cm_{}_freq_trim2_{}.png".format(obj, "logsigma3")
        fig.savefig(filename, dpi=300, bbox_inches="tight")
        print(filename)
    close_db(db)
    with open("log_sigma3_trim_bundarys_list.json", "w") as f:
        json.dump(bundarys_list, f)
    return bundarys_list


# 做所有污染物按照对数3sigma边界裁切（clip）后的季节箱线图和对数季节箱线图
def season_boxplot(reload_data=False):
    with open("log_sigma3_trim_bundarys_list.json", "r") as f:
        bundarys_list = json.load(f)

    for plt_i in range(len(pollutants)):
        # for plt_i in range(1):
        if reload_data:
            get_data_dict(plt_i, bundarys_list[pollutants[plt_i]], method="clip")

        data_dict = load_data_dict()

        c = 0
        for i in stations:
            for j in range(len(seasons)):
                for k in data_dict[i][j]:
                    c += len(data_dict[i][j][k])
        print(
            "Size of {} data: {}MB\nCount of data: {}".format(
                pollutants[plt_i], sys.getsizeof(data_dict) / 1024 ** 2, c
            )
        )

        fig, axs = plt.subplots(2, 1, figsize=[10, 8])
        box_width = 0.2
        offest = 0.05
        positions = np.linspace(0, 3, 4)
        box_data = []
        box_log_data = []
        for i_index in range(len(stations)):
            i = stations[i_index]
            box_stats = []
            box_stats_log = []
            for j in range(len(seasons)):
                all_years = []
                for k in data_dict[i][j]:
                    all_years += data_dict[i][j][k]
                box_stats += cbook.boxplot_stats(all_years)
                box_stats_log += cbook.boxplot_stats(np.log(all_years))

            box_color = box_colors[i_index]
            _ = axs[0].bxp(
                box_stats,
                widths=box_width,
                showfliers=True,
                boxprops={"color": box_color},
                whiskerprops={"color": box_color},
                capprops={"color": box_color},
                medianprops={"color": box_color},
                flierprops={"color": box_color, "marker": "+"},
                positions=positions + i_index * (box_width + offest),
            )
            _ = axs[1].bxp(
                box_stats_log,
                widths=box_width,
                showfliers=True,
                boxprops={"color": box_color},
                whiskerprops={"color": box_color},
                capprops={"color": box_color},
                medianprops={"color": box_color},
                flierprops={"color": box_color, "marker": "+"},
                positions=positions + i_index * (box_width + offest),
            )
            box_data.append(box_stats)
            box_log_data.append(box_stats_log)

        patches = [
            mpatches.Patch(color=box_colors[i], label=station_names[i])
            for i in range(len(stations))
        ]

        axs[0].set_ylabel(pollutant_labels[plt_i])
        axs[1].set_ylabel(pollutant_log_labels[plt_i])
        scale_ls = positions + box_width + offest
        axs[0].set_xticks([])
        axs[1].set_xticks(scale_ls)
        axs[1].set_xticklabels(seasons)
        axs[0].legend(handles=patches, bbox_to_anchor=(1.1, 1.3), ncol=3)
        filename = "{}_log_box_fliers.png".format(pollutants[plt_i])
        fig.savefig(filename, dpi=300, bbox_inches="tight")

        for i in box_data:
            for j in i:
                j.pop("fliers")
        for i in box_log_data:
            for j in i:
                j.pop("fliers")

        with open("{}_box_data.json".format(pollutants[plt_i]), "w") as f:
            json.dump(box_data, f)
        with open("{}_box_log_data.json".format(pollutants[plt_i]), "w") as f:
            json.dump(box_log_data, f)


# 读取所有污染物按照对数3sigma边界裁切（clip）后的季节箱线图和对数季节箱线图的图像关键数据
def load_stats(log=True):
    box_stats_log = pd.DataFrame(
        columns=[
            "plt_i",
            "plt",
            "sta_i",
            "ssn_i",
            "mean",
            "iqr",
            "cilo",
            "cihi",
            "whishi",
            "whislo",
            "q1",
            "med",
            "q3",
        ]
    )
    for plt_i in range(len(pollutants)):
        # for plt_i in range(1):
        if log:
            filename = "{}_box_log_data.json".format(pollutants[plt_i])
        else:
            filename = "{}_box_data.json".format(pollutants[plt_i])
        with open(filename, "r") as f:
            box_stats_log = json.load(f)
        for sta_i, sta_stats in enumerate(box_stats_log):
            for ssn_i, ssn_stats in enumerate(sta_stats):
                box_stats_log.loc[box_stats_log.shape[0], :] = {
                    "plt_i": plt_i,
                    "plt": pollutants[plt_i],
                    "sta_i": sta_i,
                    "ssn_i": ssn_i,
                }
                for key_name in ssn_stats.keys():
                    box_stats_log.loc[box_stats_log.shape[0] - 1, key_name] = ssn_stats[
                        key_name
                    ]
    return box_stats_log


# 按照组进行正态化
def group_normalize(df, groupby, target_col=None, inplace=False, ddof=1):
    if not inplace:
        df = df.copy()
    df = df.reset_index(drop=True)
    if type(groupby) != list:
        groupby = [groupby]
    if target_col == None:
        target_col = [i for i in df.columns if i not in groupby]
    elif type(target_col) != list:
        target_col = [target_col]
    df_grouped = df.groupby(groupby)
    df_mean = df_grouped.mean()
    df_std = df_grouped.std(ddof=ddof)
    df_std_full = df[groupby].merge(df_std, on=groupby, how="left")
    df_mean_full = df[groupby].merge(df_mean, on=groupby, how="left")
    df[target_col] = (df[target_col] - df_mean_full[target_col]) / df_std_full[
        target_col
    ]
    return df, df_mean, df_std


# 按照正态化的信息反向还原数据
def group_inverse_normalize(
    df, df_mean, df_std, groupby, target_col=None, inplace=False
):
    if list(df_mean.columns) != list(df_std.columns):
        raise RuntimeError("The columns of 'df_mean' and 'df_std' is not equel.")
    if not inplace:
        df = df.copy()
    if type(groupby) != list:
        groupby = [groupby]
    if target_col == None:
        target_col = [i for i in df_mean.columns if i not in groupby]
    elif type(target_col) != list:
        target_col = [target_col]
    df_std_full = df[groupby].merge(df_std, on=groupby, how="left")
    df_mean_full = df[groupby].merge(df_mean, on=groupby, how="left")
    df[target_col] = df[target_col] * df_std_full[target_col] + df_mean_full[target_col]
    if not inplace:
        return df


# 做数据的平均数、标准差、偏度、峰度计算
def normal_stats(df, groupby, target_col=None, ddof=1):
    if type(groupby) != list:
        groupby = [groupby]
    if target_col == None:
        target_col = [i for i in df.columns if i not in groupby]
    elif type(target_col) != list:
        target_col = [target_col]
    df_grouped = df.groupby(groupby)
    df_mean = df_grouped.mean().rename(columns={i: i + "_mean" for i in target_col})
    df_std = df_grouped.std(ddof=ddof)[target_col].rename(
        columns={i: i + "_std" for i in target_col}
    )
    df_skew = df_grouped.skew()[target_col].rename(
        columns={i: i + "_skew" for i in target_col}
    )
    df_kurtosis = df_grouped.apply(pd.Series.kurtosis)[target_col].rename(
        columns={i: i + "_kurtosis" for i in target_col}
    )

    return pd.concat([df_mean, df_std, df_skew, df_kurtosis], axis=1, join="inner")


# 计算plt_i号污染物按照季节和站点分类的对数化数据特征
# RETURN: {log_data, normalized_log_data, log_data_mean, log_data_std, normalized_log_data_stats, figure_data}
def log_normal_stats(plt_i, figure=True):
    data_dict = load_data_dict(plt_i)
    data_df = ""
    if figure:
        fig, axs = plt.subplots(nrows=len(stations), ncols=len(seasons), figsize=[8, 4])
        fig_data = np.ndarray((len(stations), len(seasons)), dtype=dict)
    for i_index in range(len(stations)):
        i = stations[i_index]
        for j in range(len(seasons)):
            all_years = []
            for k in data_dict[i][j]:
                all_years += data_dict[i][j][k]
            all_years = np.log(all_years)
            if figure:
                fig_data_unit = axs[i_index, j].hist(all_years, bins=50)
                fig_data_unit = {"count": fig_data_unit[0], "x": fig_data_unit[1]}
                # print(fig_data_dict)
                fig_data[i_index, j] = fig_data_unit
                axs[i_index, j].set_xticks([])
                axs[i_index, j].set_yticks([])
                if j == 0:
                    axs[i_index, j].set_ylabel(station_names[i_index][0:2])
                if i_index + 1 == len(stations):
                    axs[i_index, j].set_xlabel(seasons[j])
                # axs[i_index, j].set_title("{}-{}季{}".format(station_names[i_index], seasons[i_index], pollutant_labels[plt_i]))
            all_years = pd.DataFrame(columns=[pollutants[plt_i]], data=all_years)
            all_years["sta_i"] = i_index
            all_years["ssn_i"] = j
            if type(data_df) == str:
                data_df = all_years
            else:
                data_df = pd.concat([data_df, all_years], axis=0, join="inner")
    data_df.reset_index(drop=True)
    n_data_df, data_df_mean, data_df_std = group_normalize(
        data_df, groupby=["sta_i", "ssn_i"]
    )
    n_stats_data = normal_stats(n_data_df, groupby=["sta_i", "ssn_i"])
    return_dict = {
        "log_data": data_df,
        "normalized_log_data": n_data_df,
        "log_data_mean": data_df_mean,
        "log_data_std": data_df_std,
        "normalized_log_data_stats": n_stats_data,
    }
    if figure:
        filename = "{}对数正态情况_行站点_列季节.png".format(pollutants[plt_i])
        fig.savefig(filename, dpi=300, bbox_inches="tight")
        return_dict["figure_data"] = fig_data
    # return data_df, n_stats_data
    return return_dict


# 计算plt_i号污染物按照季节和站点分类的正态化情况
def log_normal_check(plt_i, figure=False):
    stats_result = log_normal_stats(plt_i=plt_i, figure=figure)
    # log_data = stats_result["log_data"]
    log_data_stats = stats_result["normalized_log_data_stats"].copy()
    log_data_stats.reset_index(drop=False, inplace=True)
    col_drop = pollutants[plt_i] + pd.Series(["_mean", "_std"])
    log_data_stats.drop(columns=col_drop, inplace=True)
    # 偏度skew绝对值小于3，峰度kurtosis绝对值小于10
    # https://baijiahao.baidu.com/s?id=1635024024288052519&wfr=spider&for=pc
    log_data_stats["satisfy"] = pd.Series(
        log_data_stats[pollutants[plt_i] + "_skew"].abs() < 3
    ) & pd.Series(log_data_stats[pollutants[plt_i] + "_kurtosis"].abs() < 10)
    return stats_result, log_data_stats


# log_normal_check 对所有污染物处理
def log_normal_check_all(latex=False):
    log_data_stats_all = ""
    for plt_i in range(len(pollutants)):
        _, log_data_stats = log_normal_check(plt_i=plt_i, figure=False)
        log_data_stats.rename(
            columns={pollutants[plt_i] + "_" + i: i for i in ["skew", "kurtosis"]},
            inplace=True,
        )
        if latex:
            log_data_stats["pollutant"] = pollutant_log_labels[plt_i]
        else:
            log_data_stats["pollutant"] = pollutants[plt_i]
        if type(log_data_stats_all) == str:
            log_data_stats_all = log_data_stats
        else:
            log_data_stats_all = pd.concat(
                [log_data_stats_all, log_data_stats], axis=0, join="inner"
            )
    not_normal_list = []
    not_normal_lines = log_data_stats_all[log_data_stats_all["satisfy"] == False]
    for i in not_normal_lines.index:
        not_normal_list.append(
            {
                "plt_i": int(pollutants.index(not_normal_lines.loc[i, "pollutant"])),
                "sta_i": int(not_normal_lines.loc[i, "sta_i"]),
                "ssn_i": int(not_normal_lines.loc[i, "ssn_i"]),
            }
        )
    with open("log_not_normal_list.json", "w") as f:
        json.dump(not_normal_list, f)
    if latex:
        log_data_stats_all["ssn_i"] = log_data_stats_all["ssn_i"].map(
            {i: seasons[i] for i in range(len(seasons))}
        )
        log_data_stats_all["sta_i"] = log_data_stats_all["sta_i"].map(
            {i: station_names[i] for i in range(len(station_names))}
        )
        log_data_stats_all.reset_index(drop=True, inplace=True)
        cols = list(log_data_stats_all)
        cols.insert(0, cols.pop(cols.index("pollutant")))
        log_data_stats_all = log_data_stats_all.loc[:, cols]
        log_data_stats_all["satisfy"] = log_data_stats_all["satisfy"].map(
            {True: "满足", False: "不满足"}
        )
        log_data_stats_all.rename(
            columns={
                "sta_i": "站点",
                "ssn_i": "季节",
                "skew": "偏度",
                "kurtosis": "峰度",
                "pollutant": "项目",
                "satisfy": "正态性",
            },
            inplace=True,
        )
        log_data_stats_all = log_data_stats_all.to_latex(
            index=False, longtable=True, escape=False
        )
    return log_data_stats_all, not_normal_list


# 计算plt_i号污染物按照季节和站点分类频率最最高数据所在范围
def check_max_data_span(plt_i=0):
    max_data_span = pd.DataFrame(
        columns=pollutants[plt_i] + pd.Series(["_from", "_to"]),
        index=pd.MultiIndex.from_product(
            [range(len(stations)), range(len(seasons))], names=["sta_i", "ssn_i"]
        ),
        dtype=float,
    )

    stats_dict = log_normal_stats(plt_i, figure=True)
    for sta_i in range(len(stations)):
        for ssn_i in range(len(seasons)):
            fig_data_t = stats_dict["figure_data"][sta_i, ssn_i]
            # log_data_mean_t = stats_dict["log_data_mean"]
            # log_data_std_t = stats_dict["log_data_std"]
            fig_data_t_max_count_pos = fig_data_t["count"].argmax()
            max_data_span.loc[sta_i, ssn_i][pollutants[plt_i] + "_from"] = np.exp(
                fig_data_t["x"][fig_data_t_max_count_pos]
            )
            max_data_span.loc[sta_i, ssn_i][pollutants[plt_i] + "_to"] = np.exp(
                fig_data_t["x"][fig_data_t_max_count_pos + 1]
            )
    return max_data_span


# 备选的方差分析方式，速度较快但是自己造轮子
def f_twoway_m2(df_c, col_fac1, col_fac2, col_sta, interaction=False):
    df = df_c.copy()
    list_fac1 = df[col_fac1].unique()
    list_fac2 = df[col_fac2].unique()
    r = len(list_fac1)
    s = len(list_fac2)
    x_bar = df[col_sta].mean()
    list_Qa = []
    list_Qb = []
    for i in list_fac1:
        series_i = df[df[col_fac1] == i][col_sta]
        xi_bar = series_i.mean()
        list_Qa.append((xi_bar - x_bar) ** 2)
    for j in list_fac2:
        series_j = df[df[col_fac2] == j][col_sta]
        xj_bar = series_j.mean()
        list_Qb.append((xj_bar - x_bar) ** 2)
    Q = ((df[col_sta] - x_bar) ** 2).sum()
    df_res = pd.DataFrame(columns=["方差来源", "平方和", "自由度", "均方", "F值", "Sig."])
    if interaction == False:
        Qa = s * sum(list_Qa)
        Qb = r * sum(list_Qb)
        Qw = Q - Qa - Qb
        Sa = Qa / (r - 1)
        Sb = Qb / (s - 1)
        Sw = Qw / ((r - 1) * (s - 1))
        sig1 = stats.f.sf(Sa / Sw, r - 1, (r - 1) * (s - 1))
        sig2 = stats.f.sf(Sb / Sw, s - 1, (r - 1) * (s - 1))
        df_res["方差来源"] = [col_fac1, col_fac2, "误差", "总和"]
        df_res["平方和"] = [Qa, Qb, Qw, Q]
        df_res["自由度"] = [r - 1, s - 1, (r - 1) * (s - 1), r * s - 1]
        df_res["均方"] = [Sa, Sb, Sw, "-"]
        df_res["F值"] = [Sa / Sw, Sb / Sw, "-", "-"]
        df_res["Sig."] = [sig1, sig2, "-", "-"]
        return df_res
    elif interaction == True:
        list_Qw = []
        t = len(df[(df[col_fac1] == list_fac1[0]) & (df[col_fac2] == list_fac2[0])])
        for i in list_fac1:
            for j in list_fac2:
                series_ij = df[(df[col_fac1] == i) & (df[col_fac2] == j)][col_sta]
                list_Qw.append(((series_ij - series_ij.mean()) ** 2).sum())
        Qa = s * t * sum(list_Qa)
        Qb = r * t * sum(list_Qb)
        Qw = sum(list_Qw)
        Qab = Q - Qa - Qb - Qw
        Sa = Qa / (r - 1)
        Sb = Qb / (s - 1)
        Sab = Qab / ((r - 1) * (s - 1))
        Sw = Qw / (r * s * (t - 1))
        sig1 = stats.f.sf(Sa / Sw, r - 1, r * s * (t - 1))
        sig2 = stats.f.sf(Sb / Sw, s - 1, r * s * (t - 1))
        sig3 = stats.f.sf(Sab / Sw, (r - 1) * (s - 1), r * s * (t - 1))
        df_res["方差来源"] = [col_fac1, col_fac2, col_fac1 + "*" + col_fac2, "误差", "总和"]
        df_res["平方和"] = [Qa, Qb, Qab, Qw, Q]
        df_res["自由度"] = [
            r - 1,
            s - 1,
            (r - 1) * (s - 1),
            r * s * (t - 1),
            r * s * t - 1,
        ]
        df_res["均方"] = [Sa, Sb, Sab, Sw, "-"]
        df_res["F值"] = [Sa / Sw, Sb / Sw, Sab / Sw, "-", "-"]
        df_res["Sig."] = [sig1, sig2, sig3, "-", "-"]
        return df_res
    else:
        return "interaction参数错误"


def nova_2way_m2(plt_i):
    return_dict = log_normal_stats(plt_i, figure=False)
    df_t = return_dict["log_data"]

    df_t_group = df_t.groupby(["sta_i", "ssn_i"])
    df_t_count_min = df_t_group.count().min().values[0]
    df_t_sample = ""
    for i in df_t_group.groups.keys():
        df_t_sample_unit = df_t_group.get_group(i)
        df_t_sample_index = random.sample(list(df_t_sample_unit.index), df_t_count_min)
        df_t_sample_unit = df_t_sample_unit.loc[df_t_sample_index, :]
        if type(df_t_sample) == str:
            df_t_sample = df_t_sample_unit
        else:
            df_t_sample = pd.concat(
                [df_t_sample, df_t_sample_unit], axis=0, join="inner"
            )

    return f_twoway(
        df_c=df_t_sample,
        col_fac1="sta_i",
        col_fac2="ssn_i",
        col_sta=pollutants[plt_i],
        interaction=True,
    )


# 读取不符合正态假设的数据的字典
with open("log_not_normal_list.json", "r") as f:
    not_normal_list = json.load(f)

# 接下来三个函数是方差分析
def eta_squared(aov):
    aov["eta_sq"] = "NaN"
    aov["eta_sq"] = aov[:-1]["sum_sq"] / sum(aov["sum_sq"])
    return aov


def omega_squared(aov):
    mse = aov["sum_sq"][-1] / aov["df"][-1]
    aov["omega_sq"] = "NaN"
    aov["omega_sq"] = (aov[:-1]["sum_sq"] - (aov[:-1]["df"] * mse)) / (
        sum(aov["sum_sq"]) + mse
    )
    return aov


def nova_2way(plt_i, interaction_figure=False, qq_figure=True):
    return_dict = log_normal_stats(plt_i, figure=False)
    df_t = return_dict["log_data"]

    if interaction_figure:
        fig = interaction_plot(
            df_t["ssn_i"], df_t["sta_i"], df_t[pollutants[plt_i]], ms=10
        )
        ax = fig.axes[0]
        ax.set_xticks(range(len(seasons)))
        ax.set_xticklabels(seasons)
        ax.set_xlabel("季节")

    df_t_group = df_t.groupby(["sta_i", "ssn_i"])
    df_t_count_min = df_t_group.count().min().values[0]
    df_t_sample = ""
    for i in df_t_group.groups.keys():
        df_t_sample_unit = df_t_group.get_group(i)
        df_t_sample_index = random.sample(list(df_t_sample_unit.index), df_t_count_min)
        df_t_sample_unit = df_t_sample_unit.loc[df_t_sample_index, :]
        if type(df_t_sample) == str:
            df_t_sample = df_t_sample_unit
        else:
            df_t_sample = pd.concat(
                [df_t_sample, df_t_sample_unit], axis=0, join="inner"
            )

    formula = "{} ~ C(sta_i) + C(ssn_i) + C(sta_i):C(ssn_i)".format(pollutants[plt_i])
    model = ols(formula, df_t_sample).fit()
    aov_table = anova_lm(model, typ=2)

    eta_squared(aov_table)
    omega_squared(aov_table)

    if qq_figure:
        fig = sm.qqplot(model.resid, line="s")
        ax = fig.axes[0]
        # plt.show()

    return aov_table


# # 从数据库选取sta_i号站点的原始数据，然后进行箱线图绘制，粗略查看极值范围
# ori_extreme()

# # 先用三种方式对三个站点的plt_i号污染物进行初步裁切（舍弃），并且做直方图
# way3_trim()

# # 计算所有污染物对数化的3sigma边界，存档并且返回
# bundarys_list = log_sigma3_trim()

# # 做所有污染物按照对数3sigma边界裁切（clip）后的季节箱线图和对数季节箱线图
# season_boxplot(reload_data=False)
# season_boxplot(reload_data=True)

# # 读取所有污染物按照对数3sigma边界裁切（clip）后的季节箱线图和对数季节箱线图的图像关键数据
# log_stats = load_stats(log=True)
# tab_tex = log_stats.to_latex()

# # 计算plt_i号污染物按照季节和站点分类频率最最高数据所在范围
# max_data_span = check_max_data_span(plt_i=0)

# # 计算plt_i号污染物按照季节和站点分类的正态化情况
# stats_result, log_data_stats = log_normal_check(plt_i=0, figure=False)

# # log_normal_check 对所有污染物处理
# log_data_stats_all, not_normal_list = log_normal_check_all(latex=False)
# log_data_stats_all.reset_index(drop=True, inplace=True)
# log_data_stats_all_latex, not_normal_list = log_normal_check_all(latex=True)

# 对plt_i污染物的站点、季节分类进行方差分析
aov_table = nova_2way(plt_i=0, interaction_figure=False, qq_figure=True)

# TODO: 学习方差分析的效应量

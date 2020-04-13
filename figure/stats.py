# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 17:00:48 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import pandas as pd, numpy as np
import string

import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.graphics.factorplots import interaction_plot


# 做数据的平均数、标准差、偏度、峰度计算
def normal_stats(df, groupby, target_cols=None, ddof=1):
    if type(groupby) != list:
        groupby = [groupby]
    if target_cols == None:
        target_cols = [i for i in df.columns if i not in groupby]
    elif type(target_cols) != list:
        target_cols = [target_cols]
    df_grouped = df.groupby(groupby)[target_cols]
    df_mean = df_grouped.mean().rename(columns={i: i + "_mean" for i in target_cols})
    df_std = df_grouped.std(ddof=ddof).rename(
        columns={i: i + "_std" for i in target_cols}
    )
    df_skew = df_grouped.skew()
    df_kurtosis = df_grouped.apply(pd.Series.kurtosis)
    # 偏度skew绝对值小于3，峰度kurtosis绝对值小于10
    # https://baijiahao.baidu.com/s?id=1635024024288052519&wfr=spider&for=pc
    df_norm = ((df_skew.abs() < 3) & (df_kurtosis.abs() < 10)).rename(
        columns={i: i + "_normality" for i in target_cols}
    )
    df_skew.rename(columns={i: i + "_skew" for i in target_cols}, inplace=True)
    df_kurtosis.rename(columns={i: i + "_kurtosis" for i in target_cols}, inplace=True)
    df_stats = pd.concat(
        [df_mean, df_std, df_skew, df_kurtosis, df_norm], axis=1, join="inner"
    )
    return df_stats

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


def anova(df, formula="r ~ C(a) + C(b) + C(a):C(b)", num=2, qq=False):
    model = ols(formula, df).fit()
    aov_table = anova_lm(model, typ=2)
    if num == 1:
    elif num == 2:
        eta_squared(aov_table)
        omega_squared(aov_table)
    if qq:
        fig = sm.qqplot(model.resid, line="s")
        ax = fig.axes[0]
        fig.show()
    return aov_table


if __name__ == "__main__":
    d = [
        [1, 1, 3, 4, 7],
        [1, 1, 4, 5, 8],
        [1, 1, 5, 4, 5],
        [1, 2, 3, 5, 7],
        [1, 2, 4, 6, 8],
        [1, 2, 5, 4, 5],
        [2, 1, 3, 4, 7],
        [2, 1, 4, 5, 8],
        [2, 1, 5, 4, 5],
        [2, 2, 3, 5, 7],
        [2, 2, 4, 6, 8],
        [2, 2, 5, 4, 5],
        [1, 1, 3, 4, 7],
        [1, 1, 4, 5, 8],
        [1, 1, 5, 4, 5],
        [1, 2, 3, 5, 7],
        [1, 2, 4, 6, 8],
        [1, 2, 5, 4, 5],
        [2, 1, 3, 4, 7],
        [2, 1, 4, 5, 8],
        [2, 1, 5, 4, 5],
        [2, 2, 3, 5, 7],
        [2, 2, 4, 6, 8],
        [2, 2, 5, 4, 5],
    ]
    t = pd.DataFrame(data=d, columns=["a", "b", "c", "d", "e"])
    t_stats = normal_stats(t, groupby=["a", "b"])
    # t_stats2 = normal_stats2(t, groupby=["a", "b"], normality=True)
    t_anova = anova(t, "e ~ C(c)", qq=False)
    t.loc[2, "e"] = np.nan
    t.loc[5, "c"] = np.nan
    t.loc[10, "e"] = np.nan
    t.loc[10, "c"] = np.nan
    t_anova2 = anova(t, "e ~ C(c)", qq=False)
    t["c"] = t["c"].map({i: string.ascii_lowercase[i] for i in range(26)})
    t_anova3 = anova(t, "e ~ C(c)", qq=False)

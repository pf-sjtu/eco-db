# -*- coding: utf-8 -*-
""" Global variables.
"""
import tempfile
import os
import pandas as pd
import numpy as np
import platform
import json

## return: Windows / Linux
SYSTEM = platform.system()
CR_STR = "\\r\\n" if SYSTEM == "Windows" else "\\n"

## path
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace(
    "\\", "/"
)

STATION_INFO_PATH = "{}/config/station_info.csv".format(ROOT_PATH)
COL_INFO_PATH = "{}/config/col_info.csv".format(ROOT_PATH)

TEMP_DIR = os.path.abspath(tempfile.mkdtemp(prefix="eco-db_tmp")).replace("\\", "/")

## original info dataframe
station_info_ori = pd.read_csv(STATION_INFO_PATH, encoding="utf-8", sep=",")
col_info_ori = pd.read_csv(COL_INFO_PATH, encoding="utf-8", sep=",")

## number of stations
STATION_NUM_ORI = station_info_ori.shape[0]
STATION_NUM = np.sum(station_info_ori["merge_to_no"] == -1)

## modified info dataframe
station_info = station_info_ori.loc[
    station_info_ori["merge_to_no"] == -1,
    ~station_info_ori.columns.isin(["station_no", "merge_to_no"]),
].reset_index(drop=True)
col_info = col_info_ori.copy()
for ii in range(STATION_NUM_ORI):
    s_merge_to_no = station_info_ori.loc[ii, "merge_to_no"]
    if s_merge_to_no != -1:
        for jj, [c_station, c_label] in enumerate(
            np.array(col_info_ori.loc[:, ["station" + str(ii), "label" + str(ii)]])
        ):
            if c_station == 1:
                col_info.loc[jj, "station" + str(s_merge_to_no)] = c_station
                col_info.loc[jj, "label" + str(s_merge_to_no)] = c_label
for ii in range(STATION_NUM_ORI):
    s_merge_to_no = station_info_ori.loc[ii, "merge_to_no"]
    if s_merge_to_no != -1:
        col_info.drop(["station" + str(ii), "label" + str(ii)], axis=1, inplace=True)
        for jj in range(ii + 1, STATION_NUM_ORI):
            col_info.rename(
                columns={
                    "station" + str(jj): "station" + str(jj - 1),
                    "label" + str(jj): "label" + str(jj - 1),
                },
                inplace=True,
            )


# English name dict
# From: Chinese name; Into: English name
CH2EN_DICT = dict()
CH2EN = col_info["en_name"].copy()
for ii in range(STATION_NUM):
    CH2EN.index = col_info["label" + str(ii)]
    CH2EN_DICT.update(CH2EN.to_dict())

# replace " " with "_", delete "(", ")"
# Input: pd.Series
def clean_series(series):
    clean_series = (
        series.str.replace(" ", "_")
        .str.replace(".", "p")
        .str.replace("(", "")
        .str.replace(")", "")
    )
    return clean_series


# clean English name dict
# From: English name; Into: English name with underline
EN2CLEAN_DICT = dict()
EN2CLEAN = col_info["en_name"].copy()
EN2CLEAN.index = col_info["en_name"]
EN2CLEAN = clean_series(EN2CLEAN)
EN2CLEAN_DICT.update(EN2CLEAN.to_dict())
del CH2EN, EN2CLEAN


def rm_tmp_file(filename):
    global TEMP_DIR
    filename = TEMP_DIR + "/" + filename.split("/")[-1]
    if os.path.exists(filename):
        os.remove(filename)
        return True
    return False


def rm_tmp():
    global TEMP_DIR
    dir_count = 0
    file_count = 0
    for root, dirs, files in os.walk(TEMP_DIR, topdown=False):
        for name in files:
            filename = os.path.join(root, name).replace("\\", "/")
            os.remove(filename)
            file_count += 1
        for name in dirs:
            filename = os.path.join(root, name).replace("\\", "/")
            os.rmdir(filename)
            dir_count += 1
    return {"dir_count": dir_count, "file_count": file_count}

with open("{}/config/db_config.ini".format(ROOT_PATH), "r") as f:
    db_config = json.load(f)
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 17:00:51 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""
import add_path
from utils.global_variables import station_info

import time

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
    "$ln({\\rm PM_{10}}$浓度值$)$",
    "$ln({\\rm PM_{2.5}}$浓度值$)$",
    "$ln({\\rm SO_{2}}$浓度值$)$",
    "$ln({\\rm NO_{X}}$浓度值$)$",
    "$ln({\\rm NO}$浓度值$)$",
    "$ln({\\rm CO}$浓度值$)$",
    "$ln({\\rm O_{3}}$浓度值$)$",
]


# pollutants_thd = [[0,800]]
years = list(range(2017, time.localtime().tm_year + 1))
seasons = list("春夏秋冬")
season_bundaries = ["02-04", "05-06", "08-08", "11-08"]
stations = list(station_info["db_table_name"])
station_names = list(station_info["station_name2"])
station_snames = [i[:2] + i[-1] for i in station_names]
box_colors = ["#000000", "#006000", "#AA0000"]

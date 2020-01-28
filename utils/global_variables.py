# -*- coding: utf-8 -*-
""" Global variables.
"""
import tempfile
from os.path import abspath, dirname
import pandas as pd

## path
ROOT_PATH = dirname(dirname(abspath(__file__))).replace('\\', '/')

STATION_INFO_PATH = '{}/config/station_info.csv'.format(ROOT_PATH)
COL_INFO_PATH = '{}/config/col_info.csv'.format(ROOT_PATH)

TEMP_DIR = abspath(tempfile.mkdtemp(prefix = 'eco-db_tmp')).replace('\\', '/')

## info dataframe
station_info = pd.read_csv(STATION_INFO_PATH, encoding = 'utf-8', sep = ',')
col_info = pd.read_csv(COL_INFO_PATH, encoding = 'utf-8', sep = ',')


# English name dict
# From: Chinese name; Into: English name
CH2EN_DICT = dict()
CH2EN = col_info['en_name'].copy()
for ii in range(4):
    CH2EN.index = col_info['label' + str(ii)]
    CH2EN_DICT.update(CH2EN.to_dict())

# replace " " with "_", delete "(", ")"
# Input: pd.Series
def clean_series(series):
    clean_series = series.str.replace(' ', '_')
    clean_series = clean_series.str.replace('.', 'p')
    clean_series = clean_series.str.replace('(', '')
    clean_series = clean_series.str.replace(')', '')
    return clean_series

# clean English name dict
# From: English name; Into: English name with underline
EN2CLEAN_DICT = dict()
EN2CLEAN = col_info['en_name'].copy()
EN2CLEAN.index = col_info['en_name']
EN2CLEAN = clean_series(EN2CLEAN)
EN2CLEAN_DICT.update(EN2CLEAN.to_dict())
del CH2EN, EN2CLEAN

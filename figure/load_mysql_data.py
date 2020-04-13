# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 16:48:53 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""

import pandas as pd

import add_path
from database.mysql_init import connect_db, close_db


def mysql_q(query="SELECT 'PF';", series=False):
    db = connect_db()
    db_cursor = db.cursor()
    db_cursor.execute(query)
    result = db_cursor.fetchall()
    close_db(db)
    if series:
        result = pd.Series(result).apply(lambda x: x[0])
    return result

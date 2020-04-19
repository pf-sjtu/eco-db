# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 03:50:37 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""

import pandas as pd
import MySQLdb

import add_path
from utils.global_variables import (
    CR_STR,
    TEMP_DIR,
    STATION_NUM,
    EN2CLEAN_DICT,
    station_info,
    col_info,
    clean_series,
    rm_tmp,
    db_config,
)
from utils.color_log import Logger


add_id = False
insert_methods = ["LOCAL INFILE", "INFILE"]
insert_method = insert_methods[0]
id_methods = ["IDENTIFIED WITH mysql_native_password BY", "IDENTIFIED BY"]
id_method = id_methods[0]

# 打开数据库连接
def connect_db(root_database=False):
    db_name = "station_db"
    if root_database:
        db_name = "mysql"
    db = MySQLdb.connect(
        host=db_config["root"]["host"],
        port=db_config["root"]["port"],
        user=db_config["root"]["user"],
        passwd=db_config["root"]["passwd"],
        db=db_name,
        charset="utf8mb4",
    )
    return db


def close_db(db):
    db.close()


def creat_table(db_cursor, tb_name, col_names, col_types):
    col_names = "`" + col_names + "`"
    sql_line = "CREATE TABLE IF NOT EXISTS {}(".format(tb_name)
    for col_name, col_type in zip(col_names, col_types):
        col_info_line = "{} {}, ".format(col_name, col_type)
        sql_line += col_info_line
    sql_line = sql_line.strip(", ")
    sql_line += ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
    db_cursor.execute(sql_line)
    # print("表{}已创建。".format(tb_name))
    print("Table {} created.".format(tb_name))


def add_col_front(aval_cols, col_name, col_type):
    tb_cols = aval_cols.iloc[0:1, :].copy()
    tb_cols.loc[0, :] = [col_name, col_type]
    tb_cols = tb_cols.append(aval_cols)
    return tb_cols


def aval_col_types(station_no):
    global add_id
    aval_cols = clean_series(col_info["en_name"])[
        col_info["station" + str(station_no)] == 1
    ]
    aval_cols = pd.DataFrame(aval_cols)
    aval_cols.reset_index(drop=True, inplace=True)
    aval_cols["type"] = "FLOAT"
    if add_id:
        aval_cols.loc[aval_cols["en_name"] == "datetime", "type"] = "DATETIME"
        aval_cols = add_col_front(
            aval_cols, "ID", "INT UNSIGNED AUTO_INCREMENT PRIMARY KEY"
        )
    else:
        aval_cols.loc[
            aval_cols["en_name"] == "datetime", "type"
        ] = "DATETIME PRIMARY KEY"
    return aval_cols


def insert_to_db(db, csv_dir, db_table_name, col_name_series, replace=False):
    global insert_method, insert_methods
    col_name_string = ("`" + col_name_series + "`,").sum().strip(",")
    db_cursor = db.cursor()
    method = "REPLACE" if replace else "IGNORE"
    try:
        sql_insert = """
            LOAD DATA {} '{}'
                {} INTO TABLE {}
                CHARACTER SET utf8
                FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED by '{}'
                IGNORE 1 LINES
                ({});""".format(
            insert_method, csv_dir, method, db_table_name, CR_STR, col_name_string
        )
        n_row_insert = db_cursor.execute(sql_insert)
    except MySQLdb.OperationalError as e:
        # print("插入数据库错误", e, "， 改变插入方式{}->{}。".format(insert_method, insert_methods[1]))
        Logger.log_warn(
            "WARNING:",
            "current method applied to insert into the database caused an error, change the method from {} to {}. {}.".format(
                insert_method, insert_methods[1], e
            ),
        )
        insert_method = insert_methods[1]
        sql_insert = """
            LOAD DATA {} '{}'
                {} INTO TABLE {}
                CHARACTER SET utf8
                FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED by '{}'
                IGNORE 1 LINES
                ({});""".format(
            insert_method, csv_dir, method, db_table_name, CR_STR, col_name_string
        )
        n_row_insert = db_cursor.execute(sql_insert)
    db.commit()
    return n_row_insert


def num_filter(string, remove_num=True):
    if remove_num:
        return "".join(list(filter(lambda x: x not in "0123456789", string)))
    else:
        return "".join(list(filter(lambda x: x in "0123456789", string)))


def update_table(db, table_name_str, csv_dir, df, primary_str, primary_type_str):
    cols = pd.DataFrame()
    cols["name"] = list(df.columns)
    cols["types"] = list(
        df.dtypes.astype(str).apply(num_filter).replace("object", "VARCHAR(100)")
    )
    cols.loc[cols["name"] == primary_str, "types"] = primary_type_str
    db_cursor = db.cursor()
    creat_table(db_cursor, table_name_str, cols["name"], cols["types"])
    df.to_csv(csv_dir, encoding="utf-8", index=False)
    row_num = insert_to_db(db, csv_dir, table_name_str, cols["name"], replace=True)
    return row_num


def delete_table(db, table_name_str):
    db_cursor = db.cursor()
    sql_drop = "DROP TABLE IF EXISTS {};".format(table_name_str)
    db_cursor.execute(sql_drop)
    # print("成功删除表{}。".format(table_name_str))
    print("Successfully dropped table {}.".format(table_name_str))


def init_authority_tables(db):
    db_cursor = db.cursor()
    db_cursor.execute("SHOW TABLES; ")
    tables = [i[0] for i in db_cursor.fetchall()]
    if "member" in tables:
        Logger.log_warn(
            "WARNING:", "Table 'member' already exists.",
        )
    else:
        db_cursor.execute(
            """
CREATE TABLE IF NOT EXISTS `member`(
  `id` INT(11) UNSIGNED PRIMARY KEY auto_increment,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(50) NOT NULL,
  `question_id` TINYINT(1) UNSIGNED NOT NULL,
  `answer` VARCHAR(50) NOT NULL,
  `truename` VARCHAR(50) DEFAULT NULL,
  `address` VARCHAR(50) DEFAULT NULL,
  `email` VARCHAR(50) NOT NULL,
  `authority` TINYINT(1) UNSIGNED DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `member` (`username`, `password`, `question_id`, `answer`, `truename`, `address`, `email`, `authority`) VALUES
    ('admin', '123123', '1', 'answer', '管理员', '上海交通大学农业与生物学院', 'admin@surfes', '3'),
    ('visitor', 'visitor', '1', 'answer', '访客', '访客', 'visitor@surfes', '1'),
    ('freeze', 'freeze', '1', 'answer', '冻结测试账户', '冻结测试账户',  'freeze@surfes', '0');"""
        )
    if "question" in tables:
        Logger.log_warn(
            "WARNING:", "Table 'question' already exists.",
        )
    else:
        db_cursor.execute(
            """
CREATE TABLE IF NOT EXISTS `question` (
  `id` TINYINT(1) UNSIGNED PRIMARY KEY auto_increment,
  `question` VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `question` (`question`) VALUES
    ("您祖母叫什么名字？"), ("您祖父叫什么名字？"), ("您的生日是什么时候？（例如：1980/01/01）"),
    ("您母亲的名字？"), ("您父亲的名字？"), ("您宠物的名字叫什么？"), ("您的车号是什么？"),
    ("您的家乡是哪里？"), ("您的小学叫什么名字？"), ("您最喜欢的颜色？"),
    ("您女儿/儿子的小名叫什么？"), ("谁是您儿时最好的伙伴？"), ( "您最尊敬的老师的名字？");"""
        )
    if "auth" in tables:
        Logger.log_warn(
            "WARNING:", "Table 'auth' already exists.",
        )
    else:
        db_cursor.execute(
            """
CREATE TABLE IF NOT EXISTS `auth` (
  `id` INT(1) UNSIGNED PRIMARY KEY auto_increment,
  `contentID` VARCHAR(50) NOT NULL,
	`authLevel` TINYINT(1) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `auth` (`contentID`, `authLevel`) VALUES
	('about', 1),
	('account', 1),
	('footingInfo', 1),
	('live', 1),
	('historyTable', 2),
	('historyGraph', 2),
	('download', 2),
	('setting', 1),
	('afterLoad', 1);"""
        )


def create_user(db):
    global id_methods, id_method
    db_cursor = db.cursor()
    db_cursor.execute(
        "SELECT DISTINCT CONCAT('''',user,'''@''',host,'''') AS query FROM mysql.user;"
    )
    users = [i[0] for i in db_cursor.fetchall()]

    user_names = [i for i in db_config.keys() if i != "root"]
    for user_name in user_names:
        user_name_full = "'{}'@'{}'".format(user_name, "localhost")
        if user_name_full in users:
            Logger.log_warn(
                "WARNING:", "user {} already exists.".format(user_name_full),
            )
        else:
            try:
                db_cursor.execute(
                    "CREATE USER {} {} '{}';".format(
                        user_name_full, id_method, db_config[user_name]["passwd"]
                    )
                )
            except MySQLdb.OperationalError as e:
                Logger.log_warn(
                    "WARNING:",
                    "current method applied to create a user caused an error, change the method from {} to {}. {}.".format(
                        id_method, id_methods[1], e
                    ),
                )
                id_method = id_methods[1]
                db_cursor.execute(
                    "CREATE USER {} {} '{}';".format(
                        user_name_full, id_method, db_config[user_name]["passwd"]
                    )
                )
            Logger.log_normal("USER:", "add user {}.".format(user_name_full))
    webUser_table = list(station_info["db_table_name"]) + ["col_info", "station_info"]
    loginAssistant_table = ["member", "question", "auth"]
    privilege_args = [(i, "webUser") for i in webUser_table] + [
        (i, "loginAssistant") for i in loginAssistant_table
    ]
    for args in privilege_args:
        db_cursor.execute(
            "GRANT SELECT ON station_db.{} TO '{}'@'localhost';".format(
                args[0], args[1]
            )
        )
    db_cursor.execute("FLUSH PRIVILEGES;")
    Logger.log_normal("USER:", "privileges flushed.")


def init_db():
    db = connect_db(True)
    db_cursor = db.cursor()

    db_cursor.execute(
        """CREATE DATABASE IF NOT EXISTS station_db;
           USE station_db;"""
    )

    # create station info
    delete_table(db, "station_info")
    s_info_tmp_dir = TEMP_DIR + "/s_info.csv"
    station_info.to_csv(s_info_tmp_dir, encoding="utf-8", index=False)
    s_num = update_table(
        db,
        "station_info",
        s_info_tmp_dir,
        station_info,
        "station_no",
        "INT PRIMARY KEY",
    )
    # print("{}条站点信息已更新。".format(s_num))
    Logger.log_normal(
        "UPDATE:", "{} lines of imformation of stations updated.".format(s_num)
    )

    # create column info
    delete_table(db, "col_info")
    c_info = col_info.loc[~col_info["data_label"].isin(["日期", "时间"]), :].reset_index(
        drop=True
    )
    c_info = c_info.reset_index(drop=False)
    c_info.rename(columns={"index": "id"}, inplace=True)
    c_info["db_name"] = c_info["en_name"].map(EN2CLEAN_DICT)
    c_info_tmp_dir = TEMP_DIR + "/c_info.csv"
    c_info.to_csv(c_info_tmp_dir, encoding="utf-8", index=False)
    c_num = update_table(
        db, "col_info", c_info_tmp_dir, c_info, "id", "int primary key"
    )
    # print("{}条表头信息已更新。".format(c_num))
    Logger.log_normal(
        "UPDATE:", "{} lines of imformation of columns updated.".format(c_num)
    )

    for ii in range(STATION_NUM):
        tb_cols = aval_col_types(ii)
        tb_name = station_info.loc[ii, "db_table_name"]
        creat_table(db_cursor, tb_name, tb_cols["en_name"], tb_cols["type"])

    init_authority_tables(db)
    create_user(db)

    close_db(db)
    rm_tmp()


if __name__ == "__main__":
    init_db()

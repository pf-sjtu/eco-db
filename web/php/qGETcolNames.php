<?php
isset($_GET['table_name']) && isset($_GET['rand']) || die('{"phpErrorCode": 0, "phpError": "Parameters error."}');

// 临时设置脚本最长运行时间/秒
ini_set("max_execution_time", "5");
//设置程序运行的内存
ini_set('memory_limit','16M');

$table_cols = "table_cols".$_GET['rand'];
$all_cols   = "all_cols".$_GET['rand'];

$cTmp1 =   "CREATE TEMPORARY TABLE ".$all_cols." AS SELECT
                en_name AS title,
                db_name
            FROM
                col_info;";

$cTmp2 =   "CREATE TEMPORARY TABLE ".$table_cols." AS SELECT
                COLUMN_NAME AS `key` 
            FROM
                information_schema.COLUMNS 
            WHERE
                table_name = '".$_GET['table_name']."';";

$qTitleKey =    "SELECT
                    title, `key`
                FROM
                    ".$table_cols.
                " LEFT JOIN ".$all_cols." 
                ON ".$table_cols.".`key` = ".$all_cols.".db_name;";

$conn = new mysqli('localhost',
                    'webUser',
                    '516150910019',
                    'station_db',
                    3306);
if ($conn->connect_error) {
    die('{"phpErrorCode": 1, "phpError": "'.$conn->connect_error.'"}');
}

if (mysqli_query($conn, $cTmp1) === FALSE) {
    die('{"phpErrorCode": 2, "phpError": "'.$conn->error.'", "mysqlQuery": "'.$cTmp1.'"}');
}
if (mysqli_query($conn, $cTmp2) === FALSE) {
    die('{"phpErrorCode": 2, "phpError": "'.$conn->error.'", "mysqlQuery": "'.$cTmp2.'"}');
}

$r = $conn->query($qTitleKey);
if ($r === FALSE) {
    die('{"phpErrorCode": 2, "phpError": "'.$conn->error.'", "mysqlQuery": "'.$r.'"}');
}

if ($r->num_rows > 0){
    if (isset($_GET['dtype']) && $_GET['dtype'] == "num"){
        echo json_encode(mysqli_fetch_all($r, MYSQLI_NUM));
    }
    elseif (isset($_GET['dtype']) && $_GET['dtype'] == "both"){
        echo json_encode(mysqli_fetch_all($r, MYSQLI_BOTH));
    }
    else {
        echo json_encode(mysqli_fetch_all($r, MYSQLI_ASSOC));
    }
}
else {
    die('{"phpErrorCode": 3, "phpError": "No result."}');
}
?>
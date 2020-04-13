<?php
// 临时设置脚本最长运行时间/秒
ini_set("max_execution_time", "5");
//设置程序运行的内存
ini_set('memory_limit', '16M');

$conn = new mysqli(
    'localhost',
    'webUser',
    '516150910019',
    'station_db',
    3306
);
if ($conn->connect_error) {
    die('{"phpErrorCode": 1, "phpError": "' . $conn->connect_error . '"}');
}

$q = "SELECT en_name AS title, db_name AS `key`, unit FROM col_info";

if (isset($_GET['sta_i']) && is_numeric($_GET['sta_i'])) {
    $q .= " WHERE station" . $_GET['sta_i'] . "=1";
}

$r = $conn->query($q);
if ($r === FALSE) {
    die('{"phpErrorCode": 2, "phpError": "' . $conn->error . '", "mysqlQuery": "' . $_GET['q'] . '"}');
}

if ($r->num_rows > 0) {
    if (isset($_GET['dtype']) && $_GET['dtype'] == "num") {
        echo json_encode(mysqli_fetch_all($r, MYSQLI_NUM));
    } elseif (isset($_GET['dtype']) && $_GET['dtype'] == "both") {
        echo json_encode(mysqli_fetch_all($r, MYSQLI_BOTH));
    } else {
        echo json_encode(mysqli_fetch_all($r, MYSQLI_ASSOC));
    }
} else {
    die('{"phpErrorCode": 3, "phpError": "No result."}');
}

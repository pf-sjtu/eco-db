<?php
isset($_GET['tb']) || die('{"phpErrorCode": 0, "phpError": "Parameters error."}');

// 临时设置脚本最长运行时间/秒
ini_set("max_execution_time", "5");
//设置程序运行的内存
ini_set("memory_limit", "100M");

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

$q = "SELECT * FROM " . mysqli_escape_string($conn, $_GET['tb']);

if (isset($_GET['dt_beg']) && isset($_GET['dt_end'])) {
    $q .= " WHERE datetime >= '" . mysqli_escape_string($conn, $_GET['dt_beg']) . "' AND datetime <= '" . mysqli_escape_string($conn, $_GET['dt_end']) . "'";
}

if (isset($_GET['order'])) {
    if ($_GET['order'] == "A") {
        $q .= " ORDER BY datetime ASC";
    } else if ($_GET['order'] == "D") {
        $q .= " ORDER BY datetime DESC";
    }
}

if (isset($_GET['limit']) && is_numeric($_GET['limit'])) {
    $q .= " LIMIT " . $_GET['limit'];
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

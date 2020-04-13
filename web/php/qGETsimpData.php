<?php
isset($_GET['table_name']) && isset($_GET['dtBegStr']) && isset($_GET['dtEndStr']) && isset($_GET['num']) && is_numeric($_GET['num']) || die('{"phpErrorCode": 0, "phpError": "Parameters error."}');

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

$qLineTotal = "SELECT (@total:=COUNT(*)) FROM " .  mysqli_escape_string($conn, $_GET['table_name']) . " WHERE datetime >= '" .  mysqli_escape_string($conn, $_GET['dtBegStr']) . "' AND datetime <= '" .  mysqli_escape_string($conn, $_GET['dtEndStr']) . "';";
$setParams  = "SET @id = 0, @num = " . $_GET['num'] . ";";
$qSimpData  = "SELECT * FROM " .  mysqli_escape_string($conn, $_GET['table_name']) . " WHERE datetime >= '" .  mysqli_escape_string($conn, $_GET['dtBegStr']) . "' AND datetime <= '" .  mysqli_escape_string($conn, $_GET['dtEndStr']) . "' AND (@tmp:=(@id:=@id+1)*@num/@total)-FLOOR(@tmp)<@num/@total;";

if (mysqli_query($conn, $qLineTotal) === FALSE) {
    die('{"phpErrorCode": 2, "phpError": "' . $conn->error . '", "mysqlQuery": "' . $cTmp1 . '"}');
}
if (mysqli_query($conn, $setParams) === FALSE) {
    die('{"phpErrorCode": 2, "phpError": "' . $conn->error . '", "mysqlQuery": "' . $cTmp2 . '"}');
}

$r = $conn->query($qSimpData);
if ($r === FALSE) {
    die('{"phpErrorCode": 2, "phpError": "' . $conn->error . '", "mysqlQuery": "' . $r . '"}');
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

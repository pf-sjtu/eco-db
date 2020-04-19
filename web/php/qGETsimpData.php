<?php
isset($_GET['table_name']) && isset($_GET['dtBegStr']) && isset($_GET['dtEndStr']) && isset($_GET['num']) && is_numeric($_GET['num']) || die('{"phpErrorCode": 0, "phpError": "Parameters error."}');

ini_set("max_execution_time", "5");
ini_set('memory_limit', '16M');

require_once('webConn.php');

$table_name = mysqli_escape_string($conn, $_GET['table_name']);
$dtBegStr = mysqli_escape_string($conn, $_GET['dtBegStr']);
$dtEndStr = mysqli_escape_string($conn, $_GET['dtEndStr']);

$qLineTotal = "SELECT (@total:=COUNT(*)) FROM `$table_name` WHERE datetime >= '$dtBegStr' AND datetime <= '$dtEndStr';";
$setParams  = "SET @id = 0, @num = " . $_GET['num'] . ";";
$q = "SELECT * FROM `$table_name` WHERE datetime >= '$dtBegStr' AND datetime <= '$dtEndStr' AND (@tmp:=(@id:=@id+1)*@num/@total)-FLOOR(@tmp)<@num/@total;";

if (mysqli_query($conn, $qLineTotal) === FALSE) {
    die('{"phpErrorCode": 2, "phpError": "' . $conn->error . '", "mysqlQuery": "' . $cTmp1 . '"}');
}
if (mysqli_query($conn, $setParams) === FALSE) {
    die('{"phpErrorCode": 2, "phpError": "' . $conn->error . '", "mysqlQuery": "' . $cTmp2 . '"}');
}

require_once('queryQ.php');

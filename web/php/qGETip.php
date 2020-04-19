<?php
isset($_GET['datetime']) &&
    isset($_GET['ip0']) &&
    isset($_GET['ip1']) &&
    isset($_GET['ip2']) &&
    isset($_GET['ip3']) || die('{"phpErrorCode": 0, "phpError": "Parameters error."}');

ini_set("max_execution_time", "5");
ini_set('memory_limit', '16M');

$datetime = $_GET['datetime'];
$ip0 = $_GET['ip0'];
$ip1 = $_GET['ip1'];
$ip2 = $_GET['ip2'];
$ip3 = $_GET['ip3'];

$insert = "INSERT INTO ip (`datetime`, ip0, ip1, ip2, ip3) VALUES ('$datetime', $ip0,  $ip1,  $ip2, $ip3)";

require_once('webConn.php');

if (mysqli_query($conn, $insert) === FALSE) {
    die('{"phpErrorCode": 2, "phpError": "' . $conn->error . '", "mysqlQuery": "' . $insert . '"}');
}
mysqli_close($conn);

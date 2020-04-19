<?php
isset($_GET['tb']) || die('{"phpErrorCode": 0, "phpError": "Parameters error."}');

ini_set("max_execution_time", "5");
ini_set("memory_limit", "100M");

require_once('webConn.php');

$table_name = mysqli_escape_string($conn, $_GET['tb']);
$q = "SELECT * FROM `$table_name`";

if (isset($_GET['dt_beg']) && isset($_GET['dt_end'])) {
    $dtBegStr = mysqli_escape_string($conn, $_GET['dt_beg']);
    $dtEndStr = mysqli_escape_string($conn, $_GET['dt_end']);
    $q .= " WHERE datetime >= '$dtBegStr' AND datetime <= '$dtEndStr'";
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

require_once('queryQ.php');

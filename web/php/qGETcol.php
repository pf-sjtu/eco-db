<?php
ini_set("max_execution_time", "5");
ini_set('memory_limit', '16M');

require_once('webConn.php');

$q = "SELECT en_name AS title, db_name AS `key`, unit FROM col_info";

if (isset($_GET['sta_i']) && is_numeric($_GET['sta_i'])) {
    $q .= " WHERE station" . $_GET['sta_i'] . "=1";
}

require_once('queryQ.php');

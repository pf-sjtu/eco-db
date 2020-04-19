<?php
ini_set("max_execution_time", "5");
ini_set('memory_limit', '16M');

require_once('webConn.php');
$q = "SELECT * FROM station_info";
require_once('queryQ.php');

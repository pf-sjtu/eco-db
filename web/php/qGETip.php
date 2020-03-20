<?php
isset($_GET['datetime']) && 
isset($_GET['ip0']) && 
isset($_GET['ip1']) && 
isset($_GET['ip2']) && 
isset($_GET['ip3']) && 
isset($_GET['location']) || die('{"phpErrorCode": 0, "phpError": "Parameters error."}');

// 临时设置脚本最长运行时间/秒
ini_set("max_execution_time", "5");
//设置程序运行的内存
ini_set('memory_limit','16M');

$insert = "INSERT INTO ip (`datetime`, ip0, ip1, ip2, ip3, `location`) VALUES ('".$_GET['datetime']."', ".$_GET['ip0'].", ".$_GET['ip1'].", ".$_GET['ip2'].", ".$_GET['ip3'].", '".$_GET['location']."');";

$conn = new mysqli('localhost',
                    'webUser',
                    '516150910019',
                    'station_db',
                    3306);
if ($conn->connect_error) {
    die('{"phpErrorCode": 1, "phpError": "'.$conn->connect_error.'"}');
}

if (mysqli_query($conn, $insert) === FALSE) {
    die('{"phpErrorCode": 2, "phpError": "'.$conn->error.'", "mysqlQuery": "'.$insert.'"}');
}
?>
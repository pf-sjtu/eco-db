<?php
session_start();
$auth = $_SESSION['auth'];

if ($auth < 3) {
    echo "[]";
    exit;
}

require_once('../conn.php');
$sql = mysqli_query($conn, "SELECT * FROM `member` WHERE `username` != 'admin' AND `username` != 'visitor'");
$userInfoArr = mysqli_fetch_all($sql, MYSQLI_ASSOC);
echo json_encode($userInfoArr);

<?php
require_once('conn.php');
$sql = mysqli_query($conn, "SELECT `email` FROM `member` WHERE `username`='admin'");
$adminEmail = mysqli_fetch_array($sql)[0];
echo $adminEmail;

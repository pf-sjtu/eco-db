<?php
$conn = mysqli_connect("localhost", "loginAssistant", "l516150910019", "station_db");
@mysqli_set_charset($conn, 'utf8mb4');
@mysqli_query($conn, 'utf8mb4');

if (mysqli_connect_errno($conn)) {
    echo "连接MySql数据库失败" . mysqli_connect_error() . "<br>";
}

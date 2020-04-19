<?php
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
if (!$conn->set_charset("utf8mb4")) {
    printf("Error loading character set utf8mb4: %s\n", $conn->error);
}

<?php
$r = $conn->query($q);
if ($r === FALSE) {
    die('{"phpErrorCode": 2, "phpError": "' . $conn->error . '", "mysqlQuery": "' . $_GET['q'] . '"}');
}

mysqli_close($conn);

if ($r->num_rows > 0) {
    if (isset($_GET['dtype']) && $_GET['dtype'] == "num") {
        echo json_encode(mysqli_fetch_all($r, MYSQLI_NUM));
    } elseif (isset($_GET['dtype']) && $_GET['dtype'] == "both") {
        echo json_encode(mysqli_fetch_all($r, MYSQLI_BOTH));
    } else {
        echo json_encode(mysqli_fetch_all($r, MYSQLI_ASSOC));
    }
} else {
    die('{"phpErrorCode": 3, "phpError": "No result."}');
}

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,height=device-height,inital-scale=1.0,maximum-scale=2.0,user-scalable=no" />
    <title>用户管理</title>
    <link rel="shortcut icon" href="../pic/icon2.64.ico" />
    <link rel="stylesheet" type="text/css" href="../css/account.css" />
</head>

<body>
    <?php
    session_start();
    $auth = $_SESSION['auth'];

    if ($auth < 3) {
        exit;
    }

    require_once('../conn.php');
    for ($i = 0; isset($_POST['id' . $i]); $i++) {
        $ID = $_POST['id' . $i];
        $auth = $_POST['authority' . $i];
        $delete = ($_POST['delete' . $i] == 1);
        if (preg_match('/[0-9]+/', $ID) && preg_match('/[0-9]+/', $auth)) {
            if ($delete == true) {
                mysqli_query($conn, "DELETE FROM `member` WHERE `id`=$ID");
            } else {
                mysqli_query($conn, "UPDATE `member` SET `authority`=$auth WHERE `id`='$ID'");
            }
        } else {
            echo "<script>alert('参数错误，修改终止。');history.back();</script>";
            exit;
        }
    }
    echo "<script>alert('修改用户数据成功。');history.back();</script>";
    exit;
    ?>
</body>

</html>
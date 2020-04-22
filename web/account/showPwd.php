<!DOCTYPE html>
<html lang="en" class="full">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,height=device-height,inital-scale=1.0,maximum-scale=2.0,user-scalable=no" />
    <title>找回密码</title>
    <link rel="shortcut icon" href="../pic/icon2.64.ico" />
    <link rel="stylesheet" type="text/css" href="../css/account.css" />
    <?php
    require_once('conn.php');
    $user_name = $_POST['user_name'];
    $answer = mysqli_escape_string($conn, $_POST['answer']);
    $email = strtolower(mysqli_escape_string($conn, $_POST['email']));
    $sql = mysqli_query($conn, "SELECT * FROM `member` WHERE username='$user_name'");
    $info = mysqli_fetch_array($sql);
    if ($info['answer'] != $answer) {
        echo "<script>alert('问题答案输入错误！');history.back();</script>";
        exit;
    } elseif ($info['email'] != $email) {
        echo "<script>alert('邮箱输入错误！');history.back();</script>";
        exit;
    } else {
        $password = $info['password'];
    }
    ?>
</head>

<body class="full">
    <div class="loginForm uForm">
        <div class="title">
            <img class="icon" src="../pic/icon2.dark.small.png" alt="" />
            <p>SURFES<span>上海城市森林生态站数据库管理系统</span></p>
        </div>
        <p class="uTitle">找回密码</p>
        <p class="tLine">
            用户名：<?php echo $user_name ?>
        </p>
        <p class="tLine">
            密码：<?php echo $password ?>
        </p>
        <div class="formOption2">
            <a class="loginOption" href="../index.php">重新登录</a>
        </div>
    </div>

</body>

</html>